import json
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import pwd
import subprocess
import stat
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts" / "codex-review"
CODEX_RULE = ROOT / ".codex" / "rules" / "codex-review.rules"
CATALOG = {
    "models": [
        {
            "slug": "gpt-5.6-terra",
            "supported_reasoning_levels": [{"effort": "low"}, {"effort": "medium"}, {"effort": "high"}],
        }
    ]
}


def load_launcher(name: str):
    loader = importlib.machinery.SourceFileLoader(name, str(LAUNCHER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class CodexReviewLauncherTests(unittest.TestCase):
    def make_fake_codex(self, root: Path, body: str, catalog: dict | None = None) -> Path:
        """Answer --version and debug models; run body for exec with $out as the last-message file."""
        catalog_file = root / "catalog.json"
        catalog_file.write_text(json.dumps(CATALOG if catalog is None else catalog), encoding="utf-8")
        executable = root / "codex"
        executable.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = \"--version\" ]; then printf 'codex-cli 9.9.9\\n'; exit 0; fi\n"
            f"if [ \"$1\" = \"debug\" ]; then cat {catalog_file}; exit 0; fi\n"
            "out=\"\"\n"
            "for arg in \"$@\"; do\n"
            "  if [ \"$expect_out\" = 1 ]; then out=\"$arg\"; expect_out=0; fi\n"
            "  if [ \"$arg\" = \"--output-last-message\" ]; then expect_out=1; fi\n"
            "done\n" + body,
            encoding="utf-8",
        )
        executable.chmod(0o700)
        return executable

    def current_commit(self) -> str:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.strip()

    def run_launcher(
        self,
        executable: Path,
        *arguments: str,
        prompt: bytes = b"",
        candidate_commit: str | None = "current",
        selector: tuple[str, ...] = ("--", "--model", "gpt-5.6-terra"),
    ) -> subprocess.CompletedProcess[bytes]:
        command = [str(LAUNCHER), "--codex-bin", str(executable)]
        if "--auth-preflight" not in arguments and candidate_commit is not None:
            commit = self.current_commit() if candidate_commit == "current" else candidate_commit
            command.extend(("--candidate-commit", commit))
        command.extend(arguments)
        command.extend(selector)
        return subprocess.run(
            command,
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            cwd=ROOT,
        )

    def run_with_recorded_arguments(self, *arguments: str, prompt: bytes = b"", selector: tuple[str, ...]):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            arguments_file = root / "arguments"
            diagnostics_file = root / "diagnostics.json"
            executable = self.make_fake_codex(
                root,
                f"printf '%s\\n' \"$@\" > {arguments_file}\n"
                "if [ -t 0 ]; then exit 3; fi\ninput=$(cat)\n"
                "case \"$input\" in *CODEX_AUTH_OK*) printf 'CODEX_AUTH_OK\\n' > \"$out\";; *) printf '%s\\n' \"$input\" > \"$out\";; esac\n",
            )
            completed = self.run_launcher(
                executable, "--diagnostics-file", str(diagnostics_file), *arguments, prompt=prompt, selector=selector
            )
            observed_arguments = arguments_file.read_text(encoding="utf-8").splitlines()
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        return record, observed_arguments

    ENVELOPE_CASES = {
        "review with model and effort": ((), b"Review the candidate.\n", ("--", "--model", "gpt-5.6-terra", "--effort=high")),
        "review with model only": ((), b"Review the candidate.\n", ("--", "--model", "gpt-5.6-terra")),
        "auth preflight": (("--auth-preflight",), b"", ("--", "--model", "gpt-5.6-terra", "--effort", "low")),
    }

    def test_record_declares_the_envelope_actually_passed(self):
        launcher = load_launcher("codex_review_envelope_fixture")
        for label, (arguments, prompt, selector) in self.ENVELOPE_CASES.items():
            with self.subTest(label):
                record, observed = self.run_with_recorded_arguments(*arguments, prompt=prompt, selector=selector)
                rendered = launcher.codex_arguments(record["configured_envelope"])
                self.assertEqual(observed[: len(rendered)], rendered)
                self.assertEqual(observed[-1], "-")
                self.assertIsNone(record["configured_envelope"]["network_access"]["granted"])
                self.assertEqual(record["configured_envelope"]["requested"]["model"], "gpt-5.6-terra")

    def test_candidate_mismatch_record_retains_the_configured_envelope(self):
        launcher = load_launcher("codex_review_mismatch_fixture")
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            diagnostics_file = root / "diagnostics.json"
            executable = self.make_fake_codex(root, "printf 'review\\n' > \"$out\"\n")
            completed = self.run_launcher(
                executable,
                "--diagnostics-file",
                str(diagnostics_file),
                prompt=b"Review\n",
                candidate_commit="0" * 40,
                selector=("--", "--model", "gpt-5.6-terra", "--effort=high"),
            )
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
        self.assertEqual(completed.returncode, 70)
        self.assertIn("candidate commit mismatch", record["failure"])
        self.assertEqual(record["attempt_kind"], "review")
        expected = launcher.configured_envelope({"model": "gpt-5.6-terra", "effort": "high"}, preflight=False)
        self.assertEqual(record["configured_envelope"], expected)

    def test_project_rule_keeps_codex_review_approval_gated(self):
        rule = CODEX_RULE.read_text(encoding="utf-8")
        self.assertIn('"./scripts/codex-review"', rule)

    def test_requires_an_absolute_executable_path(self):
        completed = subprocess.run(
            [str(LAUNCHER), "--codex-bin", "codex", "--auth-preflight", "--", "--model", "gpt-5.6-terra"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"absolute path", completed.stderr)

    def test_auth_preflight_uses_fixed_prompt_and_returns_only_success_marker(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_codex(
                root,
                "input=$(cat)\n[ \"$input\" = \"Reply exactly: CODEX_AUTH_OK\" ] || exit 4\n"
                "printf 'CODEX_AUTH_OK\\n' > \"$out\"\nprintf 'transcript noise\\n'\n",
            )
            completed = self.run_launcher(executable, "--auth-preflight")
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(completed.stdout, b"CODEX_AUTH_OK\n")

    def test_preflight_supplies_isolation_controls_and_login_context(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            arguments_file = root / "arguments"
            context_file = root / "context"
            executable = self.make_fake_codex(
                root,
                f"printf '%s\\n' \"$@\" > {arguments_file}\n"
                f"printf '%s\\n' \"$USER\" \"$LOGNAME\" \"$HOME\" > {context_file}\n"
                "printf 'CODEX_AUTH_OK\\n' > \"$out\"\n",
            )
            completed = self.run_launcher(executable, "--auth-preflight", selector=("--", "--model=gpt-5.6-terra", "--effort", "high"))
            observed_arguments = arguments_file.read_text(encoding="utf-8").splitlines()
            observed_context = context_file.read_text(encoding="utf-8").splitlines()
        account = pwd.getpwuid(os.geteuid())
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(observed_arguments[0], "exec")
        self.assertIn("--ignore-user-config", observed_arguments)
        self.assertIn("--ephemeral", observed_arguments)
        self.assertIn("read-only", observed_arguments)
        self.assertIn("gpt-5.6-terra", observed_arguments)
        self.assertIn('approval_policy="never"', observed_arguments)
        self.assertIn('model_reasoning_effort="high"', observed_arguments)
        self.assertEqual(observed_context, [account.pw_name, account.pw_name, account.pw_dir])

    def test_non_auth_preflight_failure_is_not_reported_as_reauthentication(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_codex(
                Path(temporary_directory), "printf 'unexpected port 401 output\\n' > \"$out\"\n"
            )
            completed = self.run_launcher(executable, "--auth-preflight")
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"expected canary response", completed.stderr)
        self.assertNotIn(b"authentication needs operator attention", completed.stderr)

    def test_authentication_error_response_is_reported_as_reauthentication(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_codex(
                Path(temporary_directory),
                "printf 'Error: Not logged in. Run `codex login` first.\\n' >&2\nexit 1\n",
            )
            completed = self.run_launcher(executable, "--auth-preflight")
        self.assertEqual(completed.returncode, 78)
        self.assertIn(b"authentication needs operator attention", completed.stderr)

    def test_review_delivers_prompt_on_stdin_and_returns_last_message(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            arguments_file = root / "arguments"
            executable = self.make_fake_codex(
                root,
                f"printf '%s\\n' \"$@\" > {arguments_file}\ncat > \"$out\"\nprintf 'transcript noise\\n'\n",
            )
            completed = self.run_launcher(executable, prompt=b"Review the candidate.\n")
            observed_arguments = arguments_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertIn(b"Verified review selection:", completed.stdout)
        self.assertIn(str(ROOT).encode(), completed.stdout)
        self.assertIn(self.current_commit().encode(), completed.stdout)
        self.assertIn(b"uncommitted worktree bytes were validated", completed.stdout)
        self.assertTrue(completed.stdout.endswith(b"Review question:\nReview the candidate.\n"))
        self.assertNotIn(b"transcript noise", completed.stdout)
        self.assertEqual(observed_arguments[-1], "-")
        self.assertIn(str(ROOT), observed_arguments)

    def test_review_requires_candidate_commit(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_codex(Path(temporary_directory), "printf 'review\\n' > \"$out\"\n")
            completed = self.run_launcher(executable, prompt=b"Review\n", candidate_commit=None)
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"candidate-commit is required", completed.stderr)

    def test_candidate_commit_mismatch_fails_before_review_invocation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            invoked = root / "invoked"
            executable = self.make_fake_codex(root, f"touch {invoked}\nprintf 'review\\n' > \"$out\"\n")
            completed = self.run_launcher(executable, prompt=b"Review\n", candidate_commit="0" * 40)
            review_invoked = invoked.exists()
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"candidate commit mismatch", completed.stderr)
        self.assertFalse(review_invoked)

    def test_unaccepted_selector_is_rejected_before_task_start(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            invoked = root / "invoked"
            executable = self.make_fake_codex(root, f"touch {invoked}\nprintf 'review\\n' > \"$out\"\n")
            model_rejected = self.run_launcher(
                executable, prompt=b"Review\n", selector=("--", "--model", "gpt-5.6")
            )
            effort_rejected = self.run_launcher(
                executable, prompt=b"Review\n", selector=("--", "--model", "gpt-5.6-terra", "--effort", "ultra")
            )
            review_invoked = invoked.exists()
        self.assertEqual(model_rejected.returncode, 70)
        self.assertIn(b"does not accept model selector gpt-5.6", model_rejected.stderr)
        self.assertEqual(effort_rejected.returncode, 70)
        self.assertIn(b"does not accept effort ultra", effort_rejected.stderr)
        self.assertFalse(review_invoked)

    def test_unreadable_model_catalog_is_wrapper_failure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_codex(root, "printf 'review\\n' > \"$out\"\n", catalog={"unexpected": []})
            completed = self.run_launcher(executable, prompt=b"Review\n")
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"could not read the Codex model catalog", completed.stderr)

    def test_model_selector_is_required(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_codex(Path(temporary_directory), "printf 'review\\n' > \"$out\"\n")
            completed = self.run_launcher(executable, prompt=b"Review\n", selector=())
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"--model is required", completed.stderr)

    def test_rejects_options_that_compete_with_wrapper_controls(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_codex(Path(temporary_directory), "printf 'review\\n' > \"$out\"\n")
            completed = self.run_launcher(
                executable,
                prompt=b"Review\n",
                selector=("--", "--model", "gpt-5.6-terra", "--sandbox", "danger-full-access"),
            )
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"unsupported Codex option", completed.stderr)

    def test_non_substantive_review_output_is_a_failure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            empty = self.make_fake_codex(root, "printf 'transcript noise\\n'\nexit 0\n")
            empty_result = self.run_launcher(empty, prompt=b"Review\n")
            failing = self.make_fake_codex(root, "printf 'REJECT\\n' > \"$out\"\nexit 1\n")
            failing_result = self.run_launcher(failing, prompt=b"Review\n")
        self.assertEqual(empty_result.returncode, 70)
        self.assertIn(b"substantive review output", empty_result.stderr)
        self.assertEqual(failing_result.returncode, 70)
        self.assertEqual(failing_result.stdout, b"")
        self.assertIn(b"substantive review output", failing_result.stderr)

    def test_auth_failure_diagnostics_are_redacted_and_can_be_retained(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_codex(
                root,
                "printf 'unauthorized: token=super-secret-value Authorization: Bearer another-secret sk-proj-bare-secret\\n' >&2\nexit 1\n",
            )
            diagnostics_file = root / "diagnostics.json"
            completed = self.run_launcher(
                executable, "--auth-preflight", "--diagnostics-file", str(diagnostics_file)
            )
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
            diagnostics_mode = stat.S_IMODE(diagnostics_file.stat().st_mode)
        self.assertEqual(completed.returncode, 78)
        self.assertEqual(record["failure"], "Codex authentication needs operator attention")
        self.assertIn("[REDACTED]", record["stderr"])
        self.assertNotIn("super-secret-value", record["stderr"])
        self.assertNotIn("another-secret", record["stderr"])
        self.assertNotIn("sk-proj-bare-secret", record["stderr"])
        self.assertEqual(diagnostics_mode, 0o600)


if __name__ == "__main__":
    unittest.main()
