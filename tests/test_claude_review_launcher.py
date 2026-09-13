from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import pwd
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from launcher_support import ROOT, current_commit, load_launcher, run_launcher


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

    def run_launcher(self, executable: Path, *arguments: str, **options) -> subprocess.CompletedProcess[bytes]:
        return run_launcher(LAUNCHER, "--claude-bin", executable, *arguments, **options)

    def run_with_recorded_arguments(self, *arguments: str, prompt: bytes = b"", output: str):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            arguments_file = root / "arguments"
            diagnostics_file = root / "diagnostics.json"
            executable = self.make_fake_claude(
                root,
                f"printf '%s\\n' \"$@\" > {arguments_file}\n{output}",
            )
            completed = self.run_launcher(
                executable, "--diagnostics-file", str(diagnostics_file), *arguments, prompt=prompt
            )
            observed_arguments = arguments_file.read_text(encoding="utf-8").splitlines()
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        return record, observed_arguments

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

    def test_preflight_isolated_from_memory_and_instruction_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            environment_file = root / "environment"
            executable = self.make_fake_claude(
                root,
                f"printf '%s\\n' \"$CLAUDE_CODE_DISABLE_AUTO_MEMORY\" \"$CLAUDE_CODE_DISABLE_CLAUDE_MDS\" > {environment_file}\nprintf 'CLAUDE_AUTH_OK\\n'\n",
            )
            completed = self.run_launcher(executable, "--auth-preflight")
            observed_environment = environment_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(observed_environment, ["1", "1"])

    def test_non_auth_preflight_failure_is_not_reported_as_reauthentication(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(
                Path(temporary_directory), "printf 'unexpected port 401 output\\n'\n"
            )
            completed = self.run_launcher(executable, "--auth-preflight")
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"expected canary response", completed.stderr)
        self.assertNotIn(b"authentication needs operator attention", completed.stderr)

    def test_authentication_error_response_is_reported_as_reauthentication(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(
                Path(temporary_directory),
                "printf '{\"error\":{\"type\":\"authentication_error\",\"message\":\"invalid x-api-key\"}}\\n' >&2\nexit 1\n",
            )
            completed = self.run_launcher(executable, "--auth-preflight")
        self.assertEqual(completed.returncode, 78)
        self.assertIn(b"authentication needs operator attention", completed.stderr)

    def test_review_delivers_prompt_on_stdin_with_verified_candidate_context(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "cat\n")
            completed = self.run_launcher(executable, prompt=b"Review the candidate.\n")
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertIn(b"Verified review selection:", completed.stdout)
        self.assertIn(str(ROOT).encode(), completed.stdout)
        self.assertIn(current_commit().encode(), completed.stdout)
        self.assertIn(b"uncommitted worktree bytes were validated", completed.stdout)
        self.assertTrue(completed.stdout.endswith(b"Review question:\nReview the candidate.\n"))

    ENVELOPE_CASES = {
        "review with requested model and effort": (
            ("--", "--model", "opus", "--effort=high"),
            b"Review the candidate.\n",
            "cat\n",
        ),
        "review with nothing requested": ((), b"Review the candidate.\n", "cat\n"),
        "auth preflight": (("--auth-preflight",), b"", "printf 'CLAUDE_AUTH_OK\\n'\n"),
    }

    def test_record_declares_the_envelope_actually_passed(self):
        launcher = load_launcher(LAUNCHER, "claude_review_envelope_fixture")
        for label, (arguments, prompt, output) in self.ENVELOPE_CASES.items():
            with self.subTest(label):
                record, observed_arguments = self.run_with_recorded_arguments(
                    *arguments, prompt=prompt, output=output
                )
                rendered = ["-p", *launcher.claude_arguments(record["configured_envelope"])]
                self.assertEqual(observed_arguments, rendered)

    def test_record_declares_network_reach_from_configured_tools_and_servers(self):
        launcher = load_launcher(LAUNCHER, "claude_review_network_fixture")
        self.assertEqual(set(launcher.LOCAL_READ_ONLY_TOOLS), {"Read", "Grep", "Glob"})
        for label, (arguments, prompt, output) in self.ENVELOPE_CASES.items():
            with self.subTest(label):
                record, _ = self.run_with_recorded_arguments(*arguments, prompt=prompt, output=output)
                envelope = record["configured_envelope"]
                network = envelope["network_access"]
                reaching_tools = set(envelope["tools"]) - set(launcher.LOCAL_READ_ONLY_TOOLS)
                self.assertEqual(
                    network["granted"], bool(reaching_tools or envelope["mcp_config"]["mcpServers"])
                )
                self.assertEqual(any(network["derived_from"].values()), network["granted"])
                self.assertFalse(network["granted"])

    def test_candidate_mismatch_record_retains_the_configured_envelope(self):
        launcher = load_launcher(LAUNCHER, "claude_review_mismatch_fixture")
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            diagnostics_file = root / "diagnostics.json"
            executable = self.make_fake_claude(root, "printf 'review\\n'\n")
            completed = self.run_launcher(
                executable,
                "--diagnostics-file",
                str(diagnostics_file),
                "--",
                "--model",
                "opus",
                "--effort=high",
                prompt=b"Review\n",
                candidate_commit="0" * 40,
            )
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
        self.assertEqual(completed.returncode, 70)
        self.assertIn("candidate commit mismatch", record["failure"])
        self.assertEqual(record["attempt_kind"], "review")
        expected = launcher.configured_envelope({"model": "opus", "effort": "high"}, preflight=False)
        self.assertEqual(record["configured_envelope"], expected)

    def test_record_keeps_the_existing_stdout_received_field(self):
        """Archived governed-review diagnostics already carry this key; keep its name and meaning."""
        with_output, _ = self.run_with_recorded_arguments(prompt=b"Review\n", output="cat\n")
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            diagnostics_file = root / "diagnostics.json"
            executable = self.make_fake_claude(root, "exit 0\n")
            completed = self.run_launcher(
                executable, "--diagnostics-file", str(diagnostics_file), prompt=b"Review\n"
            )
            without_output = json.loads(diagnostics_file.read_text(encoding="utf-8"))
        self.assertEqual(completed.returncode, 70)
        self.assertIs(with_output["stdout_received"], True)
        self.assertIs(without_output["stdout_received"], False)

    def test_auth_failure_during_review_stops_for_operator_attention(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(
                Path(temporary_directory),
                "printf '{\"error\":{\"type\":\"authentication_error\",\"message\":\"invalid x-api-key\"}}\\n' >&2\nexit 1\n",
            )
            completed = self.run_launcher(executable, prompt=b"Review\n")
        self.assertEqual(completed.returncode, 78)
        self.assertIn(b"authentication needs operator attention", completed.stderr)
        self.assertNotIn(b"substantive review output", completed.stderr)

    def test_auth_words_in_review_output_do_not_diagnose_credentials(self):
        """Reviewer prose is not provider evidence: an unrelated failure stays generic reviewer failure."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(
                Path(temporary_directory),
                "printf 'Finding: the endpoint returns 401 Unauthorized without a token check.\\n'\n"
                "printf 'reviewer process crashed after streaming\\n' >&2\nexit 1\n",
            )
            completed = self.run_launcher(executable, prompt=b"Review the authentication path.\n")
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"substantive review output", completed.stderr)
        self.assertNotIn(b"authentication needs operator attention", completed.stderr)

    def test_scratch_cleanup_failure_fails_an_otherwise_successful_attempt(self):
        """Shared-flow behavior, covered once here: provider output alone does not make the attempt succeed."""
        launcher = load_launcher(LAUNCHER, "claude_review_cleanup_fixture")
        shared = sys.modules["review_launcher"]
        leaked: list[str] = []

        class FailingDirectory(tempfile.TemporaryDirectory):
            def cleanup(self):
                leaked.append(self.name)
                raise OSError("fixture cleanup failure")

        stdout, stderr = io.StringIO(), io.StringIO()
        try:
            with tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory)
                executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
                diagnostics_file = root / "diagnostics.json"
                with mock.patch.object(shared.tempfile, "TemporaryDirectory", FailingDirectory):
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        code = launcher.main(
                            launcher.PROVIDER,
                            ["--claude-bin", str(executable), "--auth-preflight", "--diagnostics-file", str(diagnostics_file)],
                        )
                record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
        finally:
            for name in leaked:
                shutil.rmtree(name, ignore_errors=True)
        self.assertEqual(code, 70)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(record["status"], "failed")
        self.assertIs(record["stdout_received"], True)
        self.assertIn("cleanup failed", record["failure"])
        self.assertIn("fixture cleanup failure", record["stderr"])

    def run_in_process(self, *arguments: str, executable: Path, patches: dict, prompt: bytes = b"") -> tuple[int, dict, str]:
        """Drive main() in-process so shared-launcher internals can be patched; return exit code, record, stderr."""
        launcher = load_launcher(LAUNCHER, "claude_review_in_process_fixture")
        shared = sys.modules["review_launcher"]
        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as temporary_directory:
            diagnostics_file = Path(temporary_directory) / "diagnostics.json"
            stdin = mock.Mock(buffer=io.BytesIO(prompt))
            with mock.patch.multiple(shared, **patches), mock.patch.object(sys, "stdin", stdin):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = launcher.main(
                        launcher.PROVIDER, ["--claude-bin", str(executable), "--diagnostics-file", str(diagnostics_file), *arguments]
                    )
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
        self.assertEqual(stdout.getvalue(), "")
        return code, record, stderr.getvalue()

    def test_preflight_is_time_bounded(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "sleep 30\nprintf 'CLAUDE_AUTH_OK\\n'\n")
            started = time.monotonic()
            code, record, _ = self.run_in_process(
                "--auth-preflight", executable=executable, patches={"AUTH_PREFLIGHT_TIMEOUT_SECONDS": 1}
            )
            elapsed = time.monotonic() - started
        self.assertEqual(code, 70)
        self.assertLess(elapsed, 10)
        self.assertIn("preflight exceeded 1 seconds", record["failure"])
        self.assertNotIn("authentication", record["failure"])

    def test_scratch_allocation_failure_is_bounded_wrapper_failure(self):
        def refuse(prefix: str):
            raise OSError("fixture: no scratch available")

        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "printf 'CLAUDE_AUTH_OK\\n'\n")
            code, record, _ = self.run_in_process(
                "--auth-preflight",
                executable=executable,
                patches={"tempfile": mock.Mock(TemporaryDirectory=refuse)},
            )
        self.assertEqual(code, 70)
        self.assertIn("could not allocate a scratch directory", record["failure"])
        self.assertIn("fixture: no scratch available", record["failure"])

    def test_exception_path_keeps_the_original_failure_and_surfaces_cleanup_failure(self):
        leaked: list[str] = []

        class FailingDirectory(tempfile.TemporaryDirectory):
            def cleanup(self):
                leaked.append(self.name)
                raise OSError("fixture cleanup failure")

        try:
            with tempfile.TemporaryDirectory() as temporary_directory:
                executable = self.make_fake_claude(Path(temporary_directory), "printf 'review\\n'\n")
                code, record, _ = self.run_in_process(
                    "--candidate-commit",
                    "0" * 40,
                    executable=executable,
                    prompt=b"Review\n",
                    patches={"tempfile": mock.Mock(TemporaryDirectory=FailingDirectory)},
                )
        finally:
            for name in leaked:
                shutil.rmtree(name, ignore_errors=True)
        self.assertEqual(code, 70)
        self.assertIn("candidate commit mismatch", record["failure"])
        self.assertIn("cleanup failed: fixture cleanup failure", record["failure"])

    def test_requested_diagnostics_file_that_cannot_be_written_prevents_success(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            destination_dir = root / "evidence"
            destination_dir.mkdir()
            executable = self.make_fake_claude(root, f"chmod 500 {destination_dir}\nprintf 'CLAUDE_AUTH_OK\\n'\n")
            try:
                completed = self.run_launcher(
                    executable, "--auth-preflight", "--diagnostics-file", str(destination_dir / "diagnostics.json")
                )
                written = (destination_dir / "diagnostics.json").exists()
            finally:
                destination_dir.chmod(0o700)
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(completed.stdout, b"")
        self.assertFalse(written)
        record = json.loads(completed.stderr.decode().split("diagnostics: ", 1)[1])
        self.assertEqual(record["status"], "failed")
        self.assertIn("diagnostics file could not be written", record["failure"])

    def test_record_values_are_bounded_and_redacted(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
            diagnostics_file = root / "diagnostics.json"
            redacted = self.run_launcher(
                executable, "--auth-preflight", "--diagnostics-file", str(diagnostics_file), "--", "--model", "token=super-secret-value"
            )
            stored = diagnostics_file.read_text(encoding="utf-8")
            too_long = self.run_launcher(executable, "--auth-preflight", "--", "--model", "m" * 200)
        self.assertEqual(redacted.returncode, 0, redacted.stderr.decode())
        self.assertNotIn("super-secret-value", stored)
        self.assertIn("[REDACTED]", json.loads(stored)["configured_envelope"]["requested"]["model"])
        self.assertEqual(too_long.returncode, 70)
        self.assertIn(b"exceeds 128 characters", too_long.stderr)

    def test_review_requires_candidate_commit(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "printf 'review\n'\n")
            completed = self.run_launcher(
                executable,
                prompt=b"Review\n",
                candidate_commit=None,
            )
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"candidate-commit is required", completed.stderr)

    def test_candidate_commit_mismatch_fails_before_review_invocation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            invoked = root / "invoked"
            executable = self.make_fake_claude(
                root,
                f"touch {invoked}\nprintf 'review\n'\n",
            )
            completed = self.run_launcher(
                executable,
                prompt=b"Review\n",
                candidate_commit="0" * 40,
            )
            review_invoked = invoked.exists()
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"candidate commit mismatch", completed.stderr)
        self.assertFalse(review_invoked)

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
