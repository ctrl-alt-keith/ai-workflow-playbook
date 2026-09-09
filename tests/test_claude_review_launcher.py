import json
import os
from pathlib import Path
import pwd
import subprocess
import stat
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts" / "claude-review"
CODEX_RULE = ROOT / ".codex" / "rules" / "claude-review.rules"


class ClaudeReviewLauncherTests(unittest.TestCase):
    def make_fake_claude(self, root: Path, body: str) -> Path:
        executable = root / "claude"
        executable.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = \"--version\" ]; then printf 'claude 1.2.3\\n'; exit 0; fi\n"
            + body,
            encoding="utf-8",
        )
        executable.chmod(0o700)
        return executable

    def run_launcher(self, executable: Path, *arguments: str, prompt: bytes = b"") -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [str(LAUNCHER), "--claude-bin", str(executable), *arguments],
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_project_rule_keeps_claude_review_approval_gated(self):
        rule = CODEX_RULE.read_text(encoding="utf-8")
        self.assertIn('"./scripts/claude-review"', rule)

    def test_requires_an_absolute_executable_path(self):
        completed = subprocess.run(
            [str(LAUNCHER), "--claude-bin", "claude", "--auth-preflight"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"absolute path", completed.stderr)

    def test_auth_preflight_uses_fixed_prompt_and_returns_only_success_marker(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(
                root,
                "input=$(cat)\n[ \"$input\" = \"Reply exactly: CLAUDE_AUTH_OK\" ] || exit 4\nprintf 'CLAUDE_AUTH_OK\\n'\n",
            )
            completed = self.run_launcher(executable, "--auth-preflight")
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(completed.stdout, b"CLAUDE_AUTH_OK\n")

    def test_preflight_isolated_from_connectors_and_memory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            arguments_file = root / "arguments"
            environment_file = root / "environment"
            executable = self.make_fake_claude(
                root,
                f"printf '%s\\n' \"$@\" > {arguments_file}\nprintf '%s\\n' \"$CLAUDE_CODE_DISABLE_AUTO_MEMORY\" \"$CLAUDE_CODE_DISABLE_CLAUDE_MDS\" > {environment_file}\nprintf 'CLAUDE_AUTH_OK\\n'\n",
            )
            completed = self.run_launcher(executable, "--auth-preflight")
            observed_arguments = arguments_file.read_text(encoding="utf-8").splitlines()
            observed_environment = environment_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertIn("--strict-mcp-config", observed_arguments)
        self.assertIn('{"mcpServers":{}}', observed_arguments)
        self.assertIn("--setting-sources", observed_arguments)
        self.assertEqual(observed_environment, ["1", "1"])

    def test_non_auth_preflight_failure_is_not_reported_as_reauthentication(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "printf 'unexpected output\\n'\n")
            completed = self.run_launcher(executable, "--auth-preflight")
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"expected canary response", completed.stderr)
        self.assertNotIn(b"authentication needs operator attention", completed.stderr)

    def test_review_delivers_prompt_on_stdin_and_owns_restricted_arguments(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            arguments_file = root / "arguments"
            executable = self.make_fake_claude(
                root,
                f"printf '%s\\n' \"$@\" > {arguments_file}\ncat\n",
            )
            completed = self.run_launcher(
                executable,
                "--",
                "--model",
                "opus",
                "--effort=high",
                prompt=b"Review the candidate.\n",
            )
            observed_arguments = arguments_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(completed.stdout, b"Review the candidate.\n")
        self.assertEqual(observed_arguments[:3], ["-p", "--model", "opus"])
        self.assertIn("--tools", observed_arguments)
        self.assertIn("Read,Grep,Glob", observed_arguments)
        self.assertIn("--no-session-persistence", observed_arguments)

    def test_review_uses_the_effective_account_login_context(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            context_file = root / "context"
            executable = self.make_fake_claude(
                root,
                f"printf '%s\\n' \"$USER\" \"$LOGNAME\" \"$HOME\" > {context_file}\nprintf 'review\\n'\n",
            )
            completed = self.run_launcher(executable, prompt=b"Review\n")
            observed = context_file.read_text(encoding="utf-8").splitlines()
        account = pwd.getpwuid(os.geteuid())
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(observed, [account.pw_name, account.pw_name, account.pw_dir])

    def test_rejects_options_that_compete_with_wrapper_controls(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "printf 'review\\n'\n")
            completed = self.run_launcher(executable, "--", "--tools", "Bash", prompt=b"Review\n")
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"unsupported Claude option", completed.stderr)

    def test_non_substantive_review_output_is_a_failure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "exit 0\n")
            completed = self.run_launcher(executable, prompt=b"Review\n")
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"substantive review output", completed.stderr)

    def test_auth_failure_diagnostics_are_redacted_and_can_be_retained(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(
                root,
                "printf 'OAuth token=super-secret-value Authorization: Bearer another-secret sk-ant-bare-secret\\n' >&2\nexit 1\n",
            )
            diagnostics_file = root / "diagnostics.json"
            completed = self.run_launcher(
                executable,
                "--auth-preflight",
                "--diagnostics-file",
                str(diagnostics_file),
            )
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
            diagnostics_mode = stat.S_IMODE(diagnostics_file.stat().st_mode)
        self.assertEqual(completed.returncode, 78)
        self.assertEqual(record["failure"], "Claude authentication needs operator attention")
        self.assertIn("[REDACTED]", record["stderr"])
        self.assertNotIn("super-secret-value", record["stderr"])
        self.assertNotIn("another-secret", record["stderr"])
        self.assertNotIn("sk-ant-bare-secret", record["stderr"])
        self.assertEqual(diagnostics_mode, 0o600)


if __name__ == "__main__":
    unittest.main()
