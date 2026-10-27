from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import textwrap
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "repository-preflight"


class RepositoryPreflightTest(unittest.TestCase):
    def run_preflight(
        self,
        commands: dict[str, str],
        env_overrides: dict[str, str | None] | None = None,
        isolated_path: bool = False,
        arguments: tuple[str, ...] = (),
        injected_module_location: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            if isolated_path:
                sh_path = shutil.which("sh")
                self.assertIsNotNone(sh_path)
                (bin_dir / "sh").symlink_to(sh_path)
                python_path = shutil.which("python3")
                self.assertIsNotNone(python_path)
                (bin_dir / "python3").symlink_to(python_path)

            for name, body in commands.items():
                path = bin_dir / name
                path.write_text("#!/bin/sh\n" + textwrap.dedent(body), encoding="utf-8")
                path.chmod(path.stat().st_mode | stat.S_IXUSR)

            env = os.environ.copy()
            if isolated_path:
                env["PATH"] = str(bin_dir)
            else:
                env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
            if env_overrides:
                for name, value in env_overrides.items():
                    if value is None:
                        env.pop(name, None)
                    else:
                        env[name] = value
            caller_dir = None
            if injected_module_location is not None:
                module_dir = bin_dir / injected_module_location
                module_dir.mkdir()
                (module_dir / "subprocess.py").write_text("raise SystemExit(71)\n", encoding="utf-8")
                if injected_module_location == "caller":
                    caller_dir = module_dir
                elif injected_module_location == "pythonpath":
                    env["PYTHONPATH"] = str(module_dir)
                else:
                    raise ValueError("unknown injection location")
            return subprocess.run(
                [str(SCRIPT_PATH), *arguments],
                check=False,
                env=env,
                cwd=caller_dir,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

    def fake_success_commands(self) -> dict[str, str]:
        return {
            "ssh-add": """
                if [ "$1" = "-l" ]; then
                    printf '%s\\n' '256 SHA256:test-key comment (ED25519)'
                    exit 0
                fi
                exit 2
            """,
            "ssh": """
                batch=0
                strict=0
                timeout=0
                target=0
                for arg in "$@"; do
                    [ "$arg" = "BatchMode=yes" ] && batch=1
                    [ "$arg" = "StrictHostKeyChecking=yes" ] && strict=1
                    [ "$arg" = "ConnectTimeout=15" ] && timeout=1
                    [ "$arg" = "git@github.com" ] && target=1
                done
                if [ "$batch" -eq 1 ] && [ "$strict" -eq 1 ] && [ "$timeout" -eq 1 ] && [ "$target" -eq 1 ]; then
                    printf '%s\\n' "Hi test! You've successfully authenticated, but GitHub does not provide shell access." >&2
                    exit 1
                fi
                exit 255
            """,
            "gh": """
                if [ "$1" = "auth" ] && [ "$2" = "status" ]; then
                    exit 0
                fi
                exit 1
            """,
            "git": """
                if [ "$1" = "ls-remote" ]; then
                    case "$GIT_SSH_COMMAND" in
                        *"BatchMode=yes"*"StrictHostKeyChecking=yes"*"ConnectTimeout=15"*) exit 0 ;;
                    esac
                    exit 128
                fi
                exit 1
            """,
        }

    def test_success_path_accepts_github_ssh_auth_exit_one(self) -> None:
        result = self.run_preflight(self.fake_success_commands())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS ssh-add -l listed identities for diagnostic context", result.stdout)
        self.assertIn("PASS GitHub SSH connectivity works", result.stdout)
        self.assertIn("PASS Repository preflight complete", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_https_git_read_profile_uses_only_isolated_noninteractive_git(self) -> None:
        git = """
            [ "$PWD" = "/" ] || exit 2
            [ "$1" = "-c" ] && [ "$2" = "credential.helper=" ] || exit 3
            [ "$3" = "ls-remote" ] && [ "$4" = "--exit-code" ] || exit 4
            [ "$5" = "https://github.com/ctrl-alt-keith/ai-workflow-playbook.git" ] || exit 5
            [ "$6" = "HEAD" ] || exit 6
            [ "$GIT_TERMINAL_PROMPT" = "0" ] && [ "$GIT_ASKPASS" = "/bin/false" ] || exit 7
            [ "$GIT_CONFIG_GLOBAL" = "/dev/null" ] && [ "$GIT_CONFIG_NOSYSTEM" = "1" ] || exit 8
            [ -z "${GH_TOKEN-}" ] && [ -z "${OP_SERVICE_ACCOUNT_TOKEN-}" ] || exit 9
            [ -z "${HOME+x}" ] && [ -z "${GIT_CONFIG_COUNT+x}" ] || exit 10
            [ "$HTTPS_PROXY" = "http://proxy.example:8080" ] || exit 11
            [ "$SSL_CERT_FILE" = "/tmp/synthetic-ca.pem" ] || exit 12
            [ "$SSL_CERT_DIR" = "/tmp/synthetic-certs" ] || exit 13
            [ "$GIT_SSL_CAINFO" = "/tmp/git-ca.pem" ] || exit 14
            [ -z "${GIT_SSL_CAPATH+x}" ] && [ -z "${CURL_CA_BUNDLE+x}" ] || exit 15
            exit 0
        """
        result = self.run_preflight(
            {"git": git}, isolated_path=True,
            env_overrides={"GH_TOKEN": "synthetic", "OP_SERVICE_ACCOUNT_TOKEN": "synthetic",
                           "GIT_CONFIG_COUNT": "1", "HTTPS_PROXY": "http://proxy.example:8080",
                           "SSL_CERT_FILE": "/tmp/synthetic-ca.pem",
                           "SSL_CERT_DIR": "/tmp/synthetic-certs",
                           "GIT_SSL_CAINFO": "/tmp/git-ca.pem", "GIT_SSL_CAPATH": None,
                           "CURL_CA_BUNDLE": "synthetic-not-forwarded"},
            arguments=("--https-git-read", "https://github.com/ctrl-alt-keith/ai-workflow-playbook.git"),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("anonymous or proxy-routed read only", result.stdout)
        self.assertNotIn("GitHub SSH", result.stdout)
        self.assertNotIn("gh auth", result.stdout)

    def test_https_git_read_profile_does_not_create_empty_proxy_or_ca_variables(self) -> None:
        absent = ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy",
                  "no_proxy", "SSL_CERT_FILE", "SSL_CERT_DIR", "GIT_SSL_CAINFO",
                  "GIT_SSL_CAPATH")
        checks = "\n".join(f'[ -z "${{{name}+x}}" ] || exit 2' for name in absent)
        result = self.run_preflight(
            {"git": checks + "\nexit 0\n"}, isolated_path=True,
            env_overrides={name: None for name in absent},
            arguments=("--https-git-read", "https://github.com/owner/repo"),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_https_git_read_profile_ignores_caller_and_pythonpath_modules(self) -> None:
        for location in ("caller", "pythonpath"):
            with self.subTest(location=location):
                result = self.run_preflight(
                    {"git": "exit 0\n"}, isolated_path=True,
                    arguments=("--https-git-read", "https://github.com/owner/repo"),
                    injected_module_location=location,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("Isolated HTTPS Git-read preflight complete", result.stdout)

    def test_https_git_read_profile_accepts_documented_url_forms(self) -> None:
        for url in ("https://github.com/owner/repo",
                    "https://github.com/owner.name/repo_name.git",
                    "https://github.com/owner/repo.git.git"):
            with self.subTest(url=url):
                result = self.run_preflight(
                    {"git": "exit 0\n"}, isolated_path=True,
                    arguments=("--https-git-read", url),
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_https_git_read_profile_rejects_nonexact_urls_before_git(self) -> None:
        urls = (
            "https://user:token@github.com/owner/repo.git",
            "https://github.com.evil/owner/repo.git",
            "https://github.com/owner/repo.git?token=x",
            "https://github.com/owner/repo.git#fragment",
            "https://github.com/owner/repo/extra",
            "https://github.com/owner/",
            "git@github.com:owner/repo.git",
        )
        for url in urls:
            with self.subTest(url=url):
                result = self.run_preflight(
                    {"git": "exit 99\n"}, isolated_path=True,
                    arguments=("--https-git-read", url),
                )
                self.assertEqual(result.returncode, 1)
                self.assertIn("exact credential-free GitHub repository URL", result.stdout)
                self.assertNotIn("git ls-remote", result.stdout)

    def test_https_git_read_profile_reports_transport_failure_without_push_claim(self) -> None:
        result = self.run_preflight(
            {"git": "exit 1\n"}, isolated_path=True,
            arguments=("--https-git-read", "https://github.com/owner/repo.git"),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("isolated HTTPS Git repository read", result.stdout)
        self.assertIn("does not test task Git credentials, push, or GitHub API", result.stdout)

    def test_preflight_rejects_unsupported_profile_arguments(self) -> None:
        for arguments in (("--unknown", "value"), ("--https-git-read",), ("--https-git-read", "https://github.com/owner/repo.git", "extra")):
            with self.subTest(arguments=arguments):
                result = self.run_preflight({"git": "exit 99\n"}, isolated_path=True, arguments=arguments)
                self.assertEqual(result.returncode, 1)
                self.assertIn("supported profile", result.stdout)

    def test_missing_required_commands_fail_fast_with_install_remediation(self) -> None:
        cases = [
            (
                "ssh",
                "FAIL ssh is installed",
                "Install OpenSSH client tools",
                "gh is installed",
            ),
            (
                "gh",
                "FAIL gh is installed",
                "GitHub CLI",
                "git is installed",
            ),
            (
                "git",
                "FAIL git is installed",
                "Install Git",
                "ssh-add -l",
            ),
        ]

        for missing_command, failure, remediation, unexpected_next_check in cases:
            with self.subTest(missing_command=missing_command):
                commands = self.fake_success_commands()
                del commands[missing_command]

                result = self.run_preflight(commands, isolated_path=True)

                self.assertEqual(result.returncode, 1)
                self.assertIn(failure, result.stdout)
                self.assertIn(remediation, result.stdout)
                self.assertNotIn(unexpected_next_check, result.stdout)
                self.assertEqual(result.stderr, "")

    def test_gh_missing_from_path_reports_path_remediation(self) -> None:
        commands = self.fake_success_commands()
        del commands["gh"]

        result = self.run_preflight(commands, isolated_path=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL gh is installed", result.stdout)
        self.assertIn("Add GitHub CLI to PATH if already installed", result.stdout)
        self.assertIn("https://cli.github.com/", result.stdout)
        self.assertNotIn("git is installed", result.stdout)

    def test_onepassword_style_empty_ssh_add_still_succeeds_with_github_ssh_auth(self) -> None:
        commands = self.fake_success_commands()
        commands["ssh-add"] = """
            if [ "$1" = "-l" ]; then
                printf '%s\\n' 'The agent has no identities.'
                exit 1
            fi
            exit 2
        """

        result = self.run_preflight(commands)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "INFO ssh-add -l reported no identities; continuing to GitHub SSH authentication",
            result.stdout,
        )
        self.assertIn("PASS GitHub SSH connectivity works", result.stdout)
        self.assertIn("PASS Repository preflight complete", result.stdout)

    def test_missing_optional_ssh_add_still_succeeds_with_github_ssh_auth(self) -> None:
        commands = self.fake_success_commands()
        del commands["ssh-add"]

        result = self.run_preflight(commands, isolated_path=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "INFO ssh-add is unavailable; continuing to GitHub SSH authentication",
            result.stdout,
        )
        self.assertIn("PASS GitHub SSH connectivity works", result.stdout)
        self.assertIn("PASS Repository preflight complete", result.stdout)

    def test_github_ssh_failure_stops_before_gh_checks(self) -> None:
        commands = self.fake_success_commands()
        commands["ssh"] = """
            printf '%s\\n' 'git@github.com: Permission denied (publickey).' >&2
            exit 255
        """

        result = self.run_preflight(commands)

        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL GitHub SSH connectivity works via ssh -T git@github.com", result.stdout)
        self.assertIn(
            "resolve the reported GitHub SSH authentication or known_hosts issue",
            result.stdout,
        )
        self.assertNotIn("gh auth status succeeds", result.stdout)

    def test_github_ssh_success_banner_with_unexpected_exit_code_fails_closed(self) -> None:
        commands = self.fake_success_commands()
        commands["ssh"] = """
            printf '%s\\n' "Hi test! You've successfully authenticated, but GitHub does not provide shell access." >&2
            exit 255
        """

        result = self.run_preflight(commands)

        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL GitHub SSH connectivity works via ssh -T git@github.com", result.stdout)
        self.assertIn("Resolve SSH authentication for GitHub", result.stdout)
        self.assertNotIn("gh auth status succeeds", result.stdout)

    def test_negated_authentication_text_does_not_pass(self) -> None:
        commands = self.fake_success_commands()
        commands["ssh"] = """
            printf '%s\\n' 'Hi test! Not successfully authenticated.' >&2
            exit 1
        """

        result = self.run_preflight(commands)

        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL GitHub SSH connectivity works", result.stdout)
        self.assertNotIn("gh auth status succeeds", result.stdout)

    def test_gh_auth_status_failure_reports_login_remediation(self) -> None:
        commands = self.fake_success_commands()
        commands["gh"] = """
            if [ "$1" = "auth" ] && [ "$2" = "status" ]; then
                exit 1
            fi
            exit 1
        """

        result = self.run_preflight(commands)

        self.assertEqual(result.returncode, 1)
        self.assertIn("PASS GitHub SSH connectivity works", result.stdout)
        self.assertIn("FAIL gh auth status succeeds", result.stdout)
        self.assertIn("gh auth login", result.stdout)

    def test_git_reachability_failure_reports_read_only_check(self) -> None:
        commands = self.fake_success_commands()
        commands["git"] = """
            if [ "$1" = "ls-remote" ]; then
                exit 128
            fi
            exit 1
        """

        result = self.run_preflight(commands)

        self.assertEqual(result.returncode, 1)
        self.assertIn("PASS gh auth status succeeds", result.stdout)
        self.assertIn("FAIL playbook repository is reachable with git ls-remote", result.stdout)
        self.assertIn("git ls-remote git@github.com:ctrl-alt-keith/ai-workflow-playbook.git HEAD", result.stdout)

    def test_repository_and_ssh_target_overrides_are_used(self) -> None:
        commands = self.fake_success_commands()
        commands["ssh"] = """
            for arg in "$@"; do
                [ "$arg" = "git@ssh.github.example" ] && target=1
            done
            if [ "${target:-0}" -eq 1 ]; then
                printf '%s\\n' "Hi test! You've successfully authenticated, but GitHub does not provide shell access." >&2
                exit 1
            fi
            exit 255
        """
        commands["git"] = """
            if [ "$1" = "ls-remote" ] && [ "$2" = "--exit-code" ] && [ "$3" = "git@ssh.github.example:org/repo.git" ]; then
                exit 0
            fi
            exit 128
        """

        result = self.run_preflight(
            commands,
            {
                "REPOSITORY_PREFLIGHT_GITHUB_SSH_TARGET": "git@ssh.github.example",
                "REPOSITORY_PREFLIGHT_REPO_URL": "git@ssh.github.example:org/repo.git",
            },
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "PASS GitHub SSH connectivity works via ssh -T git@ssh.github.example",
            result.stdout,
        )
        self.assertIn("PASS playbook repository is reachable with git ls-remote", result.stdout)

    def test_repository_and_ssh_target_overrides_are_passed_as_literal_arguments(self) -> None:
        commands = self.fake_success_commands()
        ssh_target = "git@ssh.github.example;not-a-command"
        repo_url = "git@ssh.github.example;not-a-command:org/repo.git"
        commands["ssh"] = f"""
            for arg in "$@"; do
                [ "$arg" = "{ssh_target}" ] && target=1
            done
            if [ "${{target:-0}}" -eq 1 ]; then
                printf '%s\\n' "Hi test! You've successfully authenticated, but GitHub does not provide shell access." >&2
                exit 1
            fi
            exit 255
        """
        commands["git"] = f"""
            if [ "$1" = "ls-remote" ] && [ "$2" = "--exit-code" ] && [ "$3" = "{repo_url}" ]; then
                exit 0
            fi
            exit 128
        """

        result = self.run_preflight(
            commands,
            {
                "REPOSITORY_PREFLIGHT_GITHUB_SSH_TARGET": ssh_target,
                "REPOSITORY_PREFLIGHT_REPO_URL": repo_url,
            },
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            f"PASS GitHub SSH connectivity works via ssh -T {ssh_target}",
            result.stdout,
        )
        self.assertIn("PASS playbook repository is reachable with git ls-remote", result.stdout)

    def test_mismatched_ssh_target_and_repository_host_fail_before_auth_checks(self) -> None:
        commands = self.fake_success_commands()

        result = self.run_preflight(
            commands,
            {
                "REPOSITORY_PREFLIGHT_GITHUB_SSH_TARGET": "git@ssh.github.example",
                "REPOSITORY_PREFLIGHT_REPO_URL": "git@github.example:org/repo.git",
            },
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "FAIL GitHub SSH target and repository URL use the same host",
            result.stdout,
        )
        self.assertIn("matching git@host values", result.stdout)
        self.assertNotIn("ssh-add -l", result.stdout)
        self.assertNotIn("GitHub SSH connectivity works", result.stdout)

    def test_malformed_ssh_target_or_repository_url_fail_before_auth_checks(self) -> None:
        cases = [
            (
                "ssh target omits git user",
                {
                    "REPOSITORY_PREFLIGHT_GITHUB_SSH_TARGET": "ssh.github.example",
                    "REPOSITORY_PREFLIGHT_REPO_URL": "git@ssh.github.example:org/repo.git",
                },
            ),
            (
                "repository URL omits git user",
                {
                    "REPOSITORY_PREFLIGHT_GITHUB_SSH_TARGET": "git@ssh.github.example",
                    "REPOSITORY_PREFLIGHT_REPO_URL": "ssh.github.example:org/repo.git",
                },
            ),
        ]

        for name, overrides in cases:
            with self.subTest(name=name):
                result = self.run_preflight(self.fake_success_commands(), overrides)

                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "FAIL GitHub SSH target and repository URL use the same host",
                    result.stdout,
                )
                self.assertNotIn("ssh-add -l", result.stdout)
                self.assertNotIn("GitHub SSH connectivity works", result.stdout)

    def test_executor_failure_is_not_part_of_repository_preflight(self) -> None:
        commands = self.fake_success_commands()
        for executor_name in ("codex", "claude"):
            commands[executor_name] = """
                touch "$EXECUTOR_TEST_MARKER"
                exit 1
            """

        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "executor-invoked"
            # Executor hints must not trigger a launch or qualification.
            result = self.run_preflight(
                commands,
                {
                    "PREFLIGHT_TEST_REQUESTED_MODEL": "Example Model",
                    "PREFLIGHT_TEST_THREAD_ROUTING": "FRESH THREAD",
                    "EXECUTOR_TEST_MARKER": str(marker),
                },
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
