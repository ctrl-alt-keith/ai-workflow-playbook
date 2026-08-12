from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import textwrap
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "codex-preflight"


class CodexPreflightTest(unittest.TestCase):
    def run_preflight(
        self,
        commands: dict[str, str],
        env_overrides: dict[str, str] | None = None,
        isolated_path: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            if isolated_path:
                sh_path = shutil.which("sh")
                self.assertIsNotNone(sh_path)
                (bin_dir / "sh").symlink_to(sh_path)

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
                env.update(env_overrides)
            return subprocess.run(
                [str(SCRIPT_PATH)],
                check=False,
                env=env,
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
        self.assertIn("PASS Codex local automation preflight complete", result.stdout)
        self.assertEqual(result.stderr, "")

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
                "Install GitHub CLI",
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
        self.assertIn("PASS Codex local automation preflight complete", result.stdout)

    def test_unavailable_ssh_add_diagnostic_does_not_fail_when_github_ssh_auth_succeeds(self) -> None:
        commands = self.fake_success_commands()
        commands["ssh-add"] = """
            if [ "$1" = "-l" ]; then
                printf '%s\\n' 'Could not open a connection to your authentication agent.'
                exit 2
            fi
            exit 2
        """

        result = self.run_preflight(commands)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "INFO ssh-add -l was unavailable or inconclusive; continuing to GitHub SSH authentication",
            result.stdout,
        )
        self.assertIn("PASS GitHub SSH connectivity works", result.stdout)

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
        self.assertIn("PASS Codex local automation preflight complete", result.stdout)

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
            if [ "$1" = "ls-remote" ] && [ "$2" = "--exit-code" ] && [ "$3" = "git@github.example:org/repo.git" ]; then
                exit 0
            fi
            exit 128
        """

        result = self.run_preflight(
            commands,
            {
                "CODEX_PREFLIGHT_GITHUB_SSH_TARGET": "git@ssh.github.example",
                "CODEX_PREFLIGHT_REPO_URL": "git@github.example:org/repo.git",
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
        repo_url = "git@github.example:org/repo.git;not-a-command"
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
                "CODEX_PREFLIGHT_GITHUB_SSH_TARGET": ssh_target,
                "CODEX_PREFLIGHT_REPO_URL": repo_url,
            },
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            f"PASS GitHub SSH connectivity works via ssh -T {ssh_target}",
            result.stdout,
        )
        self.assertIn("PASS playbook repository is reachable with git ls-remote", result.stdout)


if __name__ == "__main__":
    unittest.main()
