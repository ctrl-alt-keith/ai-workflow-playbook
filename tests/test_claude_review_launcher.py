from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import pwd
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

    def test_health_probe_uses_the_substantive_path_and_requires_its_exact_answer(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            diagnostics_file = root / "diagnostics.json"
            prompt_file = root / "prompt"
            executable = self.make_fake_claude(root, f"cat > {prompt_file}\nprintf '1\\n'\n")
            completed = self.run_launcher(executable, "--health-probe", "--diagnostics-file", str(diagnostics_file))
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
            prompt = prompt_file.read_bytes()
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(completed.stdout, b"1\n")
        self.assertIn(b"Read exactly scripts/reviewer-health-probe.txt", prompt)
        self.assertTrue(prompt.endswith(b"Reply with only that decimal integer and no other text.\n"))
        self.assertEqual(record["attempt_kind"], "health_probe")
        self.assertEqual(record["health_probe"], {"fixture": "scripts/reviewer-health-probe.txt", "expected_output": "1"})
        self.assertEqual(record["diagnostics_file"], "unverified")
        self.assertIn(b'"diagnostics_file": "written"', completed.stderr)
        self.assertEqual(record["configured_envelope"], load_launcher(LAUNCHER, "claude_probe_envelope").configured_envelope({}, preflight=False))

    def test_health_probe_classifies_no_output_wrong_output_and_provider_failure(self):
        cases = {
            "no output": ("exit 0\n", b"health probe did not return output"),
            "wrong output": ("printf '2\\n'\n", b"health probe returned '2', expected '1'"),
            "provider failure": ("printf '1\\n'\nexit 3\n", b"Claude exited 3 despite producing output"),
        }
        for label, (body, expected) in cases.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as temporary_directory:
                executable = self.make_fake_claude(Path(temporary_directory), body)
                completed = self.run_launcher(executable, "--health-probe")
                self.assertEqual(completed.returncode, 70)
                self.assertIn(expected, completed.stderr)
                self.assertEqual(completed.stdout, b"")

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
        """A failure before any provider attempt keeps the pre-launch declaration of the intended review configuration; it is not attempt evidence."""
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
        self.assertTrue(record["failure"].startswith("Claude authentication needs operator attention\n"))
        self.assertIn("requested diagnostics file could not be", record["failure"])

    def test_scratch_cleanup_failure_fails_an_otherwise_successful_attempt(self):
        """Shared-flow behavior, covered once here: provider output alone does not make the attempt succeed."""
        launcher = load_launcher(LAUNCHER, "claude_review_cleanup_fixture")
        shared = sys.modules["review_launcher"]
        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
            diagnostics_file = root / "diagnostics.json"
            with mock.patch.object(shared, "cleanup_scratch", return_value="fixture cleanup failure"):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = launcher.main(
                        launcher.PROVIDER,
                        ["--claude-bin", str(executable), "--auth-preflight", "--diagnostics-file", str(diagnostics_file)],
                    )
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
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
                patches={"allocate_scratch": refuse},
            )
        self.assertEqual(code, 70)
        self.assertIn("could not allocate a scratch directory", record["failure"])
        self.assertIn("fixture: no scratch available", record["failure"])
        # a failure after the attempt's envelope exists still reports that exact envelope
        launcher = load_launcher(LAUNCHER, "claude_review_scratch_envelope_fixture")
        self.assertEqual(record["configured_envelope"], launcher.configured_envelope({}, preflight=True))

    def test_linux_projection_rejects_a_non_root_owned_shared_parent(self):
        launcher = load_launcher(LAUNCHER, "claude_review_linux_root_fixture")
        shared = sys.modules["review_launcher"]
        unsafe = os.stat_result((stat.S_IFDIR | 0o1777, 0, 0, 0, 501, 0, 0, 0, 0, 0))
        with (
            mock.patch.object(shared.platform, "system", return_value="Linux"),
            mock.patch.object(shared.os, "lstat", return_value=unsafe),
        ):
            with self.assertRaisesRegex(OSError, "root-owned 01777"):
                shared.qualified_scratch_root()

    def test_linux_projection_accepts_only_a_real_root_owned_sticky_directory(self):
        launcher = load_launcher(LAUNCHER, "claude_review_linux_projection_fixture")
        shared = sys.modules["review_launcher"]
        accepted = os.stat_result((stat.S_IFDIR | 0o1777, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        wrong_mode = os.stat_result((stat.S_IFDIR | 0o777, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        regular_file = os.stat_result((stat.S_IFREG | 0o1777, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        symlink = os.stat_result((stat.S_IFLNK | 0o777, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        with mock.patch.object(shared.platform, "system", return_value="Linux"):
            with mock.patch.object(shared.os, "lstat", return_value=accepted):
                self.assertEqual(shared.qualified_scratch_root(), Path("/tmp"))
            with mock.patch.object(shared.os, "lstat", return_value=wrong_mode):
                with self.assertRaisesRegex(OSError, "root-owned 01777"):
                    shared.qualified_scratch_root()
            for malformed in (regular_file, symlink):
                with self.subTest(mode=malformed.st_mode), mock.patch.object(shared.os, "lstat", return_value=malformed):
                    with self.assertRaisesRegex(OSError, "real directory"):
                        shared.qualified_scratch_root()

    def test_scratch_allocation_sets_private_mode_and_successful_cleanup_removes_regular_output(self):
        launcher = load_launcher(LAUNCHER, "claude_review_scratch_success_fixture")
        shared = sys.modules["review_launcher"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            root.chmod(0o700)
            previous_umask = os.umask(0o277)
            try:
                with (
                    mock.patch.object(shared, "qualified_scratch_root", return_value=root),
                    mock.patch.object(shared.secrets, "token_hex", return_value="fixture-token"),
                ):
                    scratch = shared.allocate_scratch("claude")
            finally:
                os.umask(previous_umask)
            self.assertEqual(scratch.path, root / "claude-review-fixture-token")
            self.assertEqual(stat.S_IMODE(os.lstat(scratch.path).st_mode), 0o700)
            output = scratch.path / "review.txt"
            output.write_text("review output", encoding="utf-8")
            output.chmod(0o600)
            with mock.patch.object(shared, "qualified_scratch_root", return_value=root):
                self.assertIsNone(shared.cleanup_scratch(scratch))
            self.assertFalse(scratch.path.exists())

    def test_provider_scratch_output_is_private_under_a_group_umask(self):
        launcher = load_launcher(LAUNCHER, "claude_review_group_umask_fixture")
        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(
                root,
                "printf review > provider-output.txt\nprintf 'CLAUDE_AUTH_OK\\n'\n",
            )
            diagnostics_file = root / "diagnostics.json"
            previous_umask = os.umask(0o002)
            try:
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = launcher.main(
                        launcher.PROVIDER,
                        ["--claude-bin", str(executable), "--auth-preflight", "--diagnostics-file", str(diagnostics_file)],
                    )
            finally:
                os.umask(previous_umask)
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue(), "CLAUDE_AUTH_OK\n")
        self.assertEqual(record["status"], "ok")

    def test_scratch_cleanup_refuses_mode_drift_and_symlink_members(self):
        launcher = load_launcher(LAUNCHER, "claude_review_scratch_cleanup_fixture")
        shared = sys.modules["review_launcher"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            child = root / "attempt"
            child.mkdir(mode=0o700)
            root_info = os.lstat(root)
            child_info = os.lstat(child)
            scratch = shared.ScratchDirectory(root, (root_info.st_dev, root_info.st_ino), child, (child_info.st_dev, child_info.st_ino))
            with mock.patch.object(shared, "qualified_scratch_root", return_value=root):
                child.chmod(0o755)
                self.assertIn("identity, ownership, or mode drift", shared.cleanup_scratch(scratch))
                self.assertTrue(child.exists())
                child.chmod(0o700)
                safe = child / "safe-output.txt"
                safe.write_text("review output", encoding="utf-8")
                safe.chmod(0o600)
                os.symlink(root / "missing", child / "unexpected-link")
                with mock.patch.object(Path, "iterdir", return_value=iter((safe, child / "unexpected-link"))):
                    self.assertIn("unexpected member", shared.cleanup_scratch(scratch))
                self.assertTrue((child / "unexpected-link").is_symlink())
                self.assertTrue(safe.exists())
                (child / "unexpected-link").unlink()
                safe.unlink()
                unsafe = child / "mode-drift.txt"
                unsafe.write_text("residue", encoding="utf-8")
                unsafe.chmod(0o666)
                self.assertIn("member identity or mode drift", shared.cleanup_scratch(scratch))
                self.assertTrue(unsafe.exists())

    def test_exception_path_keeps_the_original_failure_and_surfaces_cleanup_failure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "sleep 30\nprintf 'CLAUDE_AUTH_OK\\n'\n")
            code, record, _ = self.run_in_process(
                "--auth-preflight",
                executable=executable,
                patches={"cleanup_scratch": lambda directory: "fixture cleanup failure", "AUTH_PREFLIGHT_TIMEOUT_SECONDS": 1},
            )
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

    def run_preflight_with_diagnostics_patches(
        self, patches: dict, swap_path: bool = False, fail_write: bool = False, provider_body: str = "printf 'CLAUDE_AUTH_OK\\n'\n"
    ) -> tuple[int, dict, str, Path, str | None]:
        """Drive a preflight in-process with patches on the launcher's diagnostics seams.

        With ``swap_path`` the destination is replaced by another actor during the write while the
        wrapper still holds its own file open; ``fail_write`` makes completion fail after the bytes
        landed. ``patches`` maps launcher-module attribute names (e.g. ``close_descriptor``,
        ``names_identity``) to replacements. Returns exit code, stderr record, stdout, destination,
        and the destination's final text (None if absent).
        """
        launcher = load_launcher(LAUNCHER, "claude_review_diagnostics_fixture")
        shared = sys.modules["review_launcher"]
        real_write = shared.write_bytes
        state: dict = {}

        def write(descriptor, data):
            real_write(descriptor, data)
            if swap_path:
                state["destination"].unlink()
                state["destination"].write_text("replacement by another actor\n", encoding="utf-8")
            if fail_write:
                raise OSError("fixture: fsync failed after the bytes landed")

        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(root, provider_body)
            destination = state["destination"] = root / "diagnostics.json"
            from contextlib import ExitStack
            with ExitStack() as stack:
                stack.enter_context(mock.patch.object(shared, "write_bytes", write))
                for name, replacement in patches.items():
                    stack.enter_context(mock.patch.object(shared, name, replacement))
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = launcher.main(
                        launcher.PROVIDER, ["--claude-bin", str(executable), "--auth-preflight", "--diagnostics-file", str(destination)]
                    )
            after = destination.read_text(encoding="utf-8") if destination.exists() else None
        record = json.loads(stderr.getvalue().split("diagnostics: ", 1)[1])
        return code, record, stdout.getvalue(), destination, after

    def test_failed_diagnostics_write_leaves_the_file_marked_incomplete_without_cleanup(self):
        """The wrapper never unlinks at the destination: an incomplete file stays, is reported, and is not evidence."""
        code, record, stdout, destination, after = self.run_preflight_with_diagnostics_patches({}, fail_write=True)
        self.assertEqual(code, 70)
        self.assertIsNotNone(after)  # nothing was deleted
        self.assertEqual(stdout, "")
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["diagnostics_file"], "incomplete")
        self.assertIn("fsync failed after the bytes landed", record["failure"])
        self.assertIn("not valid evidence", record["failure"])
        self.assertNotIn("removed", record["failure"])
        # every byte landed, so the file parses — and it must still not certify itself
        retained = json.loads(after)
        self.assertEqual(retained["diagnostics_file"], "unverified")
        self.assertEqual(retained["status"], "ok")  # the provider did succeed; retention did not, and the file says so

    def test_retained_file_never_certifies_its_own_retention(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
            destination = root / "diagnostics.json"
            completed = self.run_launcher(executable, "--auth-preflight", "--diagnostics-file", str(destination))
            retained = json.loads(destination.read_text(encoding="utf-8"))
        terminal = json.loads(completed.stderr.decode().split("diagnostics: ", 1)[1])
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(retained["diagnostics_file"], "unverified")
        self.assertEqual(terminal["diagnostics_file"], "written")

    def test_path_inspection_failure_is_reported_as_such_not_as_mismatch(self):
        shared_names = sys.modules.get("review_launcher")
        code, record, _, _, _ = self.run_preflight_with_diagnostics_patches({"names_identity": lambda destination, identity: None})
        self.assertEqual(code, 70)
        self.assertEqual(record["diagnostics_file"], "unknown")
        self.assertIn("could not be inspected", record["failure"])
        self.assertNotIn("different file", record["failure"])

    def test_close_failure_composes_into_the_bounded_result(self):
        def refuse_close(descriptor):
            import os as _os
            _os.close(descriptor)
            raise OSError("fixture: close failed token=close-secret-value")

        # otherwise-successful retention: close failure is the primary diagnostics cause, state unknown
        code, record, stdout, _, _ = self.run_preflight_with_diagnostics_patches({"close_descriptor": refuse_close})
        self.assertEqual(code, 70)
        self.assertEqual(stdout, "")
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["diagnostics_file"], "unknown")
        self.assertTrue(record["failure"].startswith("requested diagnostics file descriptor could not be closed"))
        self.assertNotIn("close-secret-value", json.dumps(record))
        # write failure + close failure: write failure stays primary, close failure survives
        code, record, _, _, _ = self.run_preflight_with_diagnostics_patches({"close_descriptor": refuse_close}, fail_write=True)
        self.assertEqual(code, 70)
        self.assertEqual(record["diagnostics_file"], "unknown")
        self.assertTrue(record["failure"].startswith("requested diagnostics file could not be written: fixture: fsync failed"))
        self.assertIn("descriptor could not be closed", record["failure"])
        # auth primary + close failure: auth classification and exit 78 preserved
        code, record, _, _, _ = self.run_preflight_with_diagnostics_patches(
            {"close_descriptor": refuse_close},
            provider_body="printf '{\"error\":{\"type\":\"authentication_error\",\"message\":\"invalid x-api-key\"}}\\n' >&2\nexit 1\n",
        )
        self.assertEqual(code, 78)
        self.assertTrue(record["failure"].startswith("Claude authentication needs operator attention\n"))
        self.assertIn("descriptor could not be closed", record["failure"])

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
        """If the path stops naming this attempt's file, the replacement is untouched and the state is unknown."""
        code, record, _, _, after = self.run_preflight_with_diagnostics_patches({}, swap_path=True, fail_write=True)
        self.assertEqual(code, 70)
        self.assertEqual(record["diagnostics_file"], "unknown")
        self.assertIn("the path now names a different file", record["failure"])
        self.assertEqual(after, "replacement by another actor\n")

    def test_completed_write_whose_path_was_replaced_is_not_reported_written(self):
        code, record, stdout, _, after = self.run_preflight_with_diagnostics_patches({}, swap_path=True)
        self.assertEqual(code, 70)
        self.assertEqual(stdout, "")
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["diagnostics_file"], "unknown")
        self.assertIn("could not be verified after writing", record["failure"])
        self.assertEqual(after, "replacement by another actor\n")

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
        self.assertNotIn("configured_envelope", record)  # configuration had not been constructed yet

    def test_executable_failure_before_configuration_claims_no_envelope_or_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing = Path(temporary_directory) / "no-such-claude"
            completed = self.run_launcher(missing, "--auth-preflight", "--", "--model", "opus")
        record = json.loads(completed.stderr.decode().split("diagnostics: ", 1)[1])
        self.assertEqual(completed.returncode, 70)
        self.assertEqual(record["status"], "failed")
        self.assertNotIn("configured_envelope", record)
        self.assertNotIn("claude_exit_code", record)

    def test_provider_options_must_follow_the_delimiter(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "printf 'CLAUDE_AUTH_OK\\n'\n")
            delimited = self.run_launcher(executable, "--auth-preflight", "--", "--model", "opus", "--effort=high")
            bare_model = self.run_launcher(executable, "--auth-preflight", "--model", "opus")
            bare_effort = self.run_launcher(executable, "--auth-preflight", "--effort=high")
        self.assertEqual(delimited.returncode, 0, delimited.stderr.decode())
        for completed in (bare_model, bare_effort):
            self.assertEqual(completed.returncode, 70)
            self.assertIn(b"provider options must follow --", completed.stderr)

    def test_qualified_credential_keys_are_redacted(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(
                root,
                "printf 'refresh_token=plain-a client_secret=plain-b OPENAI_API_KEY=plain-c ANTHROPIC_API_KEY=plain-d\\n' >&2\n"
                "printf '%s\\n' '{\"refresh_token\":\"plain-e\",\"Proxy-Authorization\":\"Bearer plain-f\"}' >&2\n"
                "printf 'CLAUDE_AUTH_OK\\n'\n",
            )
            diagnostics_file = root / "diagnostics.json"
            completed = self.run_launcher(executable, "--auth-preflight", "--diagnostics-file", str(diagnostics_file))
            stored = diagnostics_file.read_text(encoding="utf-8")
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        for secret in ("plain-a", "plain-b", "plain-c", "plain-d", "plain-e", "plain-f"):
            self.assertNotIn(secret, stored)
            self.assertNotIn(secret.encode(), completed.stderr)
        load_launcher(LAUNCHER, "claude_review_redact_fixture")
        redact = sys.modules["review_launcher"].redact
        once = redact("OPENAI_API_KEY=plain-c")
        self.assertEqual(once, "OPENAI_API_KEY=[REDACTED]")
        self.assertEqual(redact(once), once)  # idempotent

    def test_credential_constructs_are_redacted_to_end_of_line_and_ordinary_fields_survive(self):
        load_launcher(LAUNCHER, "claude_review_redact_shapes_fixture")
        redact = sys.modules["review_launcher"].redact
        adversarial = {
            "Authorization: Basic dXNlcjpwYXNz": "dXNlcjpwYXNz",
            "Proxy-Authorization: Basic abc def": "abc def",
            '{"client_secret":"part one"}': "part one",
            "'refresh_token'='part two'": "part two",
            "OPENAI_API_KEY=plain-value; next=field": "plain-value",
            "password: hunter2 (from config)": "hunter2",
        }
        for text, secret in adversarial.items():
            with self.subTest(text):
                out = redact(text)
                self.assertNotIn(secret, out)
                self.assertIn("[REDACTED]", out)
                self.assertEqual(redact(out), out)
        ordinary = "model: gpt-5.6-sol\nreasoning effort: high\ntokens used\n2,108\ntoken_count=5\nsandbox: read-only"
        self.assertEqual(redact(ordinary), ordinary)
        # a construct on one line does not erase the next line
        two_lines = "client_secret=abc\nsandbox: read-only"
        self.assertEqual(redact(two_lines), "client_secret=[REDACTED]\nsandbox: read-only")

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
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_claude(Path(temporary_directory), "exit 3\n")
            code, record, _ = self.run_in_process(
                "--auth-preflight", executable=executable, patches={"cleanup_scratch": lambda directory: "fixture cleanup failure"}
            )
        self.assertEqual(code, 70)
        self.assertTrue(record["failure"].startswith("Claude exited 3 without substantive output\n"))
        self.assertIn("temporary-directory cleanup failed: fixture cleanup failure", record["failure"])

    def test_requested_selector_is_bounded_at_ingress_and_retained_exactly(self):
        """Option values are validated when accepted; the envelope then records the exact accepted value, never a mutated one."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_claude(root, "printf 'CLAUDE_AUTH_OK\\n'\n")
            diagnostics_file = root / "diagnostics.json"
            accepted = self.run_launcher(
                executable, "--auth-preflight", "--diagnostics-file", str(diagnostics_file), "--", "--model", "token=super-secret-value"
            )
            stored = diagnostics_file.read_text(encoding="utf-8")
            too_long = self.run_launcher(executable, "--auth-preflight", "--", "--model", "m" * 200)
        self.assertEqual(accepted.returncode, 0, accepted.stderr.decode())
        self.assertEqual(json.loads(stored)["configured_envelope"]["requested"]["model"], "token=super-secret-value")
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
