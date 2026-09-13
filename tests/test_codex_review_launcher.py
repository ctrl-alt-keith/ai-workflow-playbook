"""Codex deltas of the shared review launcher; the shared contract is covered by the Claude tests."""

import json
import os
from pathlib import Path
import pwd
import stat
import subprocess
import tempfile
import unittest

from launcher_support import ROOT, load_launcher, run_launcher


LAUNCHER = ROOT / "scripts" / "codex-review"
CODEX_RULE = ROOT / ".codex" / "rules" / "codex-review.rules"
TERRA = ("--", "--model", "gpt-5.6-terra")
CATALOG = {
    "models": [
        {
            "slug": "gpt-5.6-terra",
            "supported_reasoning_levels": [{"effort": "low"}, {"effort": "medium"}, {"effort": "high"}],
        }
    ]
}


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

    def run_launcher(
        self, executable: Path, *arguments: str, selector: tuple[str, ...] = TERRA, **options
    ) -> subprocess.CompletedProcess[bytes]:
        return run_launcher(LAUNCHER, "--codex-bin", executable, *arguments, trailing=selector, **options)

    def test_project_rule_keeps_codex_review_approval_gated(self):
        rule = CODEX_RULE.read_text(encoding="utf-8")
        self.assertIn('"./scripts/codex-review"', rule)

    ENVELOPE_CASES = {
        "review with model and effort": ((), b"Review the candidate.\n", (*TERRA, "--effort=high")),
        "review with model only": ((), b"Review the candidate.\n", TERRA),
        "auth preflight": (("--auth-preflight",), b"", (*TERRA, "--effort", "low")),
    }

    def test_record_declares_the_envelope_actually_passed(self):
        launcher = load_launcher(LAUNCHER, "codex_review_envelope_fixture")
        for label, (arguments, prompt, selector) in self.ENVELOPE_CASES.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory)
                arguments_file = root / "arguments"
                diagnostics_file = root / "diagnostics.json"
                executable = self.make_fake_codex(
                    root,
                    f"printf '%s\\n' \"$@\" > {arguments_file}\ninput=$(cat)\n"
                    "case \"$input\" in *CODEX_AUTH_OK*) printf 'CODEX_AUTH_OK\\n' > \"$out\";; "
                    "*) printf '%s\\n' \"$input\" > \"$out\";; esac\n",
                )
                completed = self.run_launcher(
                    executable, "--diagnostics-file", str(diagnostics_file), *arguments, prompt=prompt, selector=selector
                )
                observed = arguments_file.read_text(encoding="utf-8").splitlines()
                record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
                self.assertEqual(completed.returncode, 0, completed.stderr.decode())
                rendered = launcher.codex_arguments(record["configured_envelope"])
                self.assertEqual(observed[: len(rendered)], rendered)
                self.assertEqual(observed[-1], "-")
                self.assertIsNone(record["configured_envelope"]["network_access"]["granted"])

    def test_review_returns_the_last_message_from_the_effective_login_context(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            context_file = root / "context"
            executable = self.make_fake_codex(
                root,
                f"printf '%s\\n' \"$USER\" \"$LOGNAME\" \"$HOME\" > {context_file}\n"
                "cat > \"$out\"\nprintf 'transcript noise\\n'\n",
            )
            completed = self.run_launcher(executable, prompt=b"Review the candidate.\n")
            observed = context_file.read_text(encoding="utf-8").splitlines()
        account = pwd.getpwuid(os.geteuid())
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertTrue(completed.stdout.endswith(b"Review question:\nReview the candidate.\n"))
        self.assertNotIn(b"transcript noise", completed.stdout)
        self.assertEqual(observed, [account.pw_name, account.pw_name, account.pw_dir])

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
            model_rejected = self.run_launcher(executable, prompt=b"Review\n", selector=("--", "--model", "gpt-5.6"))
            effort_rejected = self.run_launcher(executable, prompt=b"Review\n", selector=(*TERRA, "--effort", "ultra"))
            review_invoked = invoked.exists()
        self.assertEqual(model_rejected.returncode, 70)
        self.assertIn(b"does not accept model selector gpt-5.6", model_rejected.stderr)
        self.assertEqual(effort_rejected.returncode, 70)
        self.assertIn(b"does not accept effort ultra", effort_rejected.stderr)
        self.assertFalse(review_invoked)

    def test_unreadable_model_catalog_is_wrapper_failure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_codex(
                Path(temporary_directory), "printf 'review\\n' > \"$out\"\n", catalog={"unexpected": []}
            )
            completed = self.run_launcher(executable, prompt=b"Review\n")
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"could not read the Codex model catalog", completed.stderr)

    def test_model_selector_is_required(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = self.make_fake_codex(Path(temporary_directory), "printf 'review\\n' > \"$out\"\n")
            completed = self.run_launcher(executable, prompt=b"Review\n", selector=())
        self.assertEqual(completed.returncode, 70)
        self.assertIn(b"--model is required", completed.stderr)

    def test_empty_or_failing_response_is_wrapper_failure_not_a_verdict(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            empty = self.run_launcher(self.make_fake_codex(root, "printf 'transcript noise\\n'\nexit 0\n"), prompt=b"Review\n")
            failing = self.run_launcher(self.make_fake_codex(root, "printf 'REJECT\\n' > \"$out\"\nexit 1\n"), prompt=b"Review\n")
        for completed in (empty, failing):
            self.assertEqual(completed.returncode, 70)
            self.assertEqual(completed.stdout, b"")
            self.assertIn(b"substantive review output", completed.stderr)

    def test_auth_failure_diagnostics_are_redacted_and_can_be_retained(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_codex(
                root,
                "printf 'Not logged in: token=super-secret-value Authorization: Bearer another-secret sk-proj-bare-secret\\n' >&2\nexit 1\n",
            )
            diagnostics_file = root / "diagnostics.json"
            completed = self.run_launcher(executable, "--auth-preflight", "--diagnostics-file", str(diagnostics_file))
            record = json.loads(diagnostics_file.read_text(encoding="utf-8"))
            diagnostics_mode = stat.S_IMODE(diagnostics_file.stat().st_mode)
        self.assertEqual(completed.returncode, 78)
        self.assertEqual(record["failure"], "Codex authentication needs operator attention")
        self.assertIn("[REDACTED]", record["stderr"])
        for secret in ("super-secret-value", "another-secret", "sk-proj-bare-secret"):
            self.assertNotIn(secret, record["stderr"])
        self.assertEqual(diagnostics_mode, 0o600)


if __name__ == "__main__":
    unittest.main()
