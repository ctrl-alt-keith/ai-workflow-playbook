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
        self.assertIn(b"exited 1 despite producing output", completed.stderr)
        self.assertNotIn(b"authentication needs operator attention", completed.stderr)

    def test_compound_failure_keeps_the_primary_cause_and_its_exit_code(self):
        """A failed diagnostics write is appended evidence; an auth failure stays auth (78)."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            destination_dir = root / "evidence"
            destination_dir.mkdir()
            executable = self.make_fake_claude(
                root,
                f"chmod 500 {destination_dir}\n"
                "printf '{\"error\":{\"type\":\"authentication_error\",\"message\":\"invalid x-api-key\"}}\\n' >&2\nexit 1\n",
            )
            try:
                completed = self.run_launcher(
                    executable, "--auth-preflight", "--diagnostics-file", str(destination_dir / "diagnostics.json")
                )
            finally:
                destination_dir.chmod(0o700)
        record = json.loads(completed.stderr.decode().split("diagnostics: ", 1)[1])
        self.assertEqual(completed.returncode, 78)
        self.assertEqual(record["status"], "failed")
        self.assertTrue(record["failure"].startswith("Claude authentication needs operator attention; "))
        self.assertIn("requested diagnostics file could not be", record["failure"])

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
        self.assertTrue(record["failure"].startswith("Claude temporary-directory cleanup failed: fixture cleanup failure"))

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
        self.assertIn("canary exceeded 1 seconds", record["failure"])
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
                executable = self.make_fake_claude(Path(temporary_directory), "sleep 30\nprintf 'CLAUDE_AUTH_OK\\n'\n")
                code, record, _ = self.run_in_process(
                    "--auth-preflight",
                    executable=executable,
                    patches={"tempfile": mock.Mock(TemporaryDirectory=FailingDirectory), "AUTH_PREFLIGHT_TIMEOUT_SECONDS": 1},
                )
        finally:
            for name in leaked:
                shutil.rmtree(name, ignore_errors=True)
        self.assertEqual(code, 70)
        self.assertTrue(record["failure"].startswith("Claude canary exceeded 1 seconds"))
        self.assertIn("temporary-directory cleanup failed: fixture cleanup failure", record["failure"])

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
        self.assertIn("requested diagnostics file could not be", record["failure"])

    def test_compound_failure_record_stays_bounded_and_redacted(self):
        """A raw primary cause must not be recomposed into the record after sanitization when the write fails."""
        long_value = " ".join(["padding"] * 400)  # > MAX_DIAGNOSTIC_CHARS once echoed back
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            destination_dir = root / "evidence"
            destination_dir.mkdir(mode=0o500)
            executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
            try:
                completed = self.run_launcher(
                    executable,
                    "--auth-preflight",
                    "--diagnostics-file",
                    str(destination_dir / "diagnostics.json"),
                    "--",
                    f"--tools=token=super-secret-value {long_value}",
                )
            finally:
                destination_dir.chmod(0o700)
        record = json.loads(completed.stderr.decode().split("diagnostics: ", 1)[1])
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(record["status"], "failed")
        self.assertTrue(record["failure"].startswith("unsupported Claude option: --tools=token=[REDACTED]"))
        self.assertIn("requested diagnostics file could not be", record["failure"])
        self.assertNotIn("super-secret-value", completed.stderr.decode())
        self.assertLessEqual(len(record["failure"]), 1000)

    def test_repeated_model_or_effort_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "printf 'CLAUDE_AUTH_OK\\n'\n")
            model = self.run_launcher(executable, "--auth-preflight", "--", "--model", "opus", "--model", "sonnet")
            effort = self.run_launcher(executable, "--auth-preflight", "--", "--effort=high", "--effort", "low")
        self.assertEqual(model.returncode, 70)
        self.assertIn(b"--model may be provided only once", model.stderr)
        self.assertEqual(effort.returncode, 70)
        self.assertIn(b"--effort may be provided only once", effort.stderr)

    def test_quoted_credential_forms_are_redacted(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(
                root,
                "printf '%s\\n' '{\"token\":\"quoted-secret-value\",\"Authorization\":\"Bearer quoted-bearer-secret\",\"api_key\": \"spaced-secret\"}' >&2\n"
                "printf 'CLAUDE_AUTH_OK\\n'\n",
            )
            diagnostics_file = root / "diagnostics.json"
            completed = self.run_launcher(executable, "--auth-preflight", "--diagnostics-file", str(diagnostics_file))
            stored = diagnostics_file.read_text(encoding="utf-8")
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        for secret in ("quoted-secret-value", "quoted-bearer-secret", "spaced-secret"):
            self.assertNotIn(secret, stored)
            self.assertNotIn(secret.encode(), completed.stderr)
        self.assertIn("[REDACTED]", json.loads(stored)["stderr"])

    def test_late_diagnostics_write_failure_leaves_no_partial_file(self):
        launcher = load_launcher(LAUNCHER, "claude_review_late_write_fixture")
        shared = sys.modules["review_launcher"]
        real_fdopen = shared.os.fdopen

        class FailingStream:
            def __init__(self, descriptor):
                self.stream = real_fdopen(descriptor, "w", encoding="utf-8")

            def __enter__(self):
                return self

            def write(self, text):
                raise OSError("fixture: device full after create")

            def __exit__(self, *exc):
                self.stream.close()
                return False

        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
            destination = root / "diagnostics.json"
            with mock.patch.object(shared.os, "fdopen", lambda descriptor, *a, **k: FailingStream(descriptor)):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = launcher.main(
                        launcher.PROVIDER, ["--claude-bin", str(executable), "--auth-preflight", "--diagnostics-file", str(destination)]
                    )
            leftover = destination.exists()
        record = json.loads(stderr.getvalue().split("diagnostics: ", 1)[1])
        self.assertEqual(code, 70)
        self.assertFalse(leftover)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["diagnostics_file"], "removed")
        self.assertIn("device full after create", record["failure"])

    def test_late_write_failure_with_failed_removal_reports_untrusted_residue(self):
        """When the created file can be neither completed nor removed, the record says so and never calls it evidence."""
        launcher = load_launcher(LAUNCHER, "claude_review_residue_fixture")
        shared = sys.modules["review_launcher"]
        real_fdopen = shared.os.fdopen

        class FailingStream:
            def __init__(self, descriptor):
                self.stream = real_fdopen(descriptor, "w", encoding="utf-8")

            def __enter__(self):
                return self

            def write(self, text):
                raise OSError("fixture: device full after create")

            def __exit__(self, *exc):
                self.stream.close()
                return False

        def refuse_unlink(path):
            raise OSError("fixture: unlink refused token=unlink-secret-value " + "x" * 1500)

        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
            destination = root / "diagnostics.json"
            with mock.patch.object(shared.os, "fdopen", lambda descriptor, *a, **k: FailingStream(descriptor)):
                with mock.patch.object(shared.os, "unlink", refuse_unlink):
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        code = launcher.main(
                            launcher.PROVIDER, ["--claude-bin", str(executable), "--auth-preflight", "--diagnostics-file", str(destination)]
                        )
            leftover = destination.exists()
        record = json.loads(stderr.getvalue().split("diagnostics: ", 1)[1])
        self.assertEqual(code, 70)
        self.assertTrue(leftover)
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["diagnostics_file"], "residue")
        self.assertTrue(record["failure"].startswith("requested diagnostics file could not be written: fixture: device full"))
        self.assertIn("could not be removed", record["failure"])
        self.assertIn("incomplete, untrusted bytes", record["failure"])
        self.assertNotIn("unlink-secret-value", stderr.getvalue())
        self.assertLessEqual(len(record["failure"]), 1000)

    def test_destination_appearing_after_validation_is_not_created_and_left_alone(self):
        """A create race is reported as this attempt not creating the artifact, with no claim about the path."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            destination = root / "diagnostics.json"
            executable = self.make_fake_claude(root, f"printf 'someone else\\n' > {destination}\nprintf 'CLAUDE_AUTH_OK\\n'\n")
            completed = self.run_launcher(executable, "--auth-preflight", "--diagnostics-file", str(destination))
            after = destination.read_text(encoding="utf-8")
        record = json.loads(completed.stderr.decode().split("diagnostics: ", 1)[1])
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(record["diagnostics_file"], "not_created")
        self.assertIn("could not be created", record["failure"])
        self.assertEqual(after, "someone else\n")

    def test_replaced_destination_is_never_unlinked_and_reported_unknown(self):
        """If the path stops naming this attempt's file before cleanup, nothing is removed and the state is unknown."""
        launcher = load_launcher(LAUNCHER, "claude_review_replacement_fixture")
        shared = sys.modules["review_launcher"]
        real_fdopen = shared.os.fdopen

        class ReplacingStream:
            def __init__(self, descriptor, destination):
                self.stream = real_fdopen(descriptor, "w", encoding="utf-8")
                self.destination = destination

            def __enter__(self):
                return self

            def write(self, text):
                self.destination.unlink()
                self.destination.write_text("replacement by another actor\n", encoding="utf-8")
                raise OSError("fixture: write failed after replacement")

            def __exit__(self, *exc):
                self.stream.close()
                return False

        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
            destination = root / "diagnostics.json"
            with mock.patch.object(shared.os, "fdopen", lambda descriptor, *a, **k: ReplacingStream(descriptor, destination)):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = launcher.main(
                        launcher.PROVIDER, ["--claude-bin", str(executable), "--auth-preflight", "--diagnostics-file", str(destination)]
                    )
            after = destination.read_text(encoding="utf-8")
        record = json.loads(stderr.getvalue().split("diagnostics: ", 1)[1])
        self.assertEqual(code, 70)
        self.assertEqual(record["diagnostics_file"], "unknown")
        self.assertIn("now names a different file; nothing was removed", record["failure"])
        self.assertEqual(after, "replacement by another actor\n")

    def test_completed_write_whose_path_was_replaced_is_not_reported_written(self):
        launcher = load_launcher(LAUNCHER, "claude_review_post_write_fixture")
        shared = sys.modules["review_launcher"]
        real_fdopen = shared.os.fdopen

        class SwapOnCloseStream:
            def __init__(self, descriptor, destination):
                self.stream = real_fdopen(descriptor, "w", encoding="utf-8")
                self.destination = destination

            def __enter__(self):
                return self

            def write(self, text):
                self.stream.write(text)

            def __exit__(self, *exc):
                self.stream.close()
                self.destination.unlink()
                self.destination.write_text("replacement after completion\n", encoding="utf-8")
                return False

        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
            destination = root / "diagnostics.json"
            with mock.patch.object(shared.os, "fdopen", lambda descriptor, *a, **k: SwapOnCloseStream(descriptor, destination)):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = launcher.main(
                        launcher.PROVIDER, ["--claude-bin", str(executable), "--auth-preflight", "--diagnostics-file", str(destination)]
                    )
            after = destination.read_text(encoding="utf-8")
        record = json.loads(stderr.getvalue().split("diagnostics: ", 1)[1])
        self.assertEqual(code, 70)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["diagnostics_file"], "unknown")
        self.assertIn("could not be verified after writing", record["failure"])
        self.assertEqual(after, "replacement after completion\n")

    def test_missing_effective_account_entry_is_bounded_wrapper_failure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "printf 'CLAUDE_AUTH_OK\\n'\n")
            code, record, stderr = self.run_in_process(
                "--auth-preflight",
                executable=executable,
                patches={"pwd": mock.Mock(getpwuid=mock.Mock(side_effect=KeyError(4242)))},
            )
        self.assertEqual(code, 70)
        self.assertEqual(record["status"], "failed")
        self.assertIn("no password-database entry for effective uid", record["failure"])
        self.assertNotIn("Traceback", stderr)

    def test_pre_existing_diagnostics_destination_is_refused_and_untouched(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
            destination = root / "diagnostics.json"
            destination.write_text("prior evidence\n", encoding="utf-8")
            completed = self.run_launcher(executable, "--auth-preflight", "--diagnostics-file", str(destination))
            after = destination.read_text(encoding="utf-8")
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"must be a new absolute path", completed.stderr)
        self.assertEqual(after, "prior evidence\n")

    def test_provider_failure_stays_primary_over_cleanup_failure(self):
        launcher = load_launcher(LAUNCHER, "claude_review_precedence_fixture")
        leaked: list[str] = []

        class FailingDirectory(tempfile.TemporaryDirectory):
            def cleanup(self):
                leaked.append(self.name)
                raise OSError("fixture cleanup failure")

        try:
            with tempfile.TemporaryDirectory() as temporary_directory:
                executable = self.make_fake_claude(Path(temporary_directory), "exit 3\n")
                code, record, _ = self.run_in_process(
                    "--auth-preflight", executable=executable, patches={"tempfile": mock.Mock(TemporaryDirectory=FailingDirectory)}
                )
        finally:
            for name in leaked:
                shutil.rmtree(name, ignore_errors=True)
        self.assertEqual(code, 70)
        self.assertTrue(record["failure"].startswith("Claude exited 3 without substantive output; "))
        self.assertIn("temporary-directory cleanup failed: fixture cleanup failure", record["failure"])

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
        self.assertTrue(record["failure"].startswith("Claude authentication needs operator attention"))
        self.assertIn("[REDACTED]", record["stderr"])
        self.assertNotIn("super-secret-value", record["stderr"])
        self.assertNotIn("another-secret", record["stderr"])
        self.assertNotIn("sk-ant-bare-secret", record["stderr"])
        self.assertEqual(diagnostics_mode, 0o600)


if __name__ == "__main__":
    unittest.main()
