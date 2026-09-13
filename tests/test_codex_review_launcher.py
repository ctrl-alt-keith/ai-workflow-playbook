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
    def make_fake_codex(self, root: Path, body: str, catalog: dict | None = None, banner: str | None = None) -> Path:
        """Answer --version and debug models; for exec, print the banner to stderr then run body with $out as the last-message file.

        By default the banner echoes the requested model and effort, as the real runtime does; pass
        `banner` to report something else (or "" for no banner).
        """
        catalog_file = root / "catalog.json"
        catalog_file.write_text(json.dumps(CATALOG if catalog is None else catalog), encoding="utf-8")
        report = (
            "printf 'OpenAI Codex v9.9.9\\n--------\\nmodel: %s\\nreasoning effort: %s\\n--------\\n' \"$model\" \"$effort\" >&2\n"
            if banner is None
            else f"printf '%s\\n' '{banner}' >&2\n" if banner else ""
        )
        executable = root / "codex"
        executable.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = \"--version\" ]; then printf 'codex-cli 9.9.9\\n'; exit 0; fi\n"
            f"if [ \"$1\" = \"debug\" ]; then cat {catalog_file}; exit 0; fi\n"
            "out=\"\"; model=\"\"; effort=\"\"; prev=\"\"\n"
            "for arg in \"$@\"; do\n"
            "  case \"$prev\" in\n"
            "    --output-last-message) out=\"$arg\";;\n"
            "    --model) model=\"$arg\";;\n"
            "    --config) case \"$arg\" in model_reasoning_effort=*) effort=${arg#model_reasoning_effort=\\\"}; effort=${effort%\\\"};; esac;;\n"
            "  esac\n"
            "  prev=\"$arg\"\n"
            "done\n" + report + body,
            encoding="utf-8",
        )
        executable.chmod(0o700)
        return executable

    def run_launcher(
        self, executable: Path, *arguments: str, selector: tuple[str, ...] = TERRA, **options
    ) -> subprocess.CompletedProcess[bytes]:
        return run_launcher(LAUNCHER, "--codex-bin", executable, *arguments, trailing=selector, **options)

    def test_project_rule_gates_the_checkout_relative_invocation(self):
        """Codex prefix rules match argv literally, so only `./scripts/codex-review` run from this checkout is gated."""
        rules: list[tuple[list, str]] = []
        namespace = {"prefix_rule": lambda *, pattern, decision, justification=None: rules.append((pattern, decision))}
        exec(CODEX_RULE.read_text(encoding="utf-8"), namespace)  # rule files are a Starlark subset that Python evaluates

        def matches(pattern: list, argv: list[str]) -> bool:
            return len(argv) >= len(pattern) and all(
                argument in (token if isinstance(token, list) else [token]) for token, argument in zip(pattern, argv)
            )

        self.assertEqual([decision for _, decision in rules], ["prompt"])
        (pattern, _), = rules
        self.assertTrue(matches(pattern, ["./scripts/codex-review", "--codex-bin", "/opt/codex"]))
        self.assertFalse(matches(pattern, [str(LAUNCHER), "--codex-bin", "/opt/codex"]))

    def test_project_layer_declaration_follows_the_rendered_user_config_control(self):
        """`project_layers_loaded: false` is a declaration derived from Codex's trust rule; only `user_config_loaded` renders."""
        launcher = load_launcher(LAUNCHER, "codex_review_isolation_fixture")
        for preflight in (False, True):
            with self.subTest(preflight=preflight):
                envelope = launcher.configured_envelope({"model": "gpt-5.6-terra"}, preflight=preflight)
                self.assertIs(envelope["user_config_loaded"], False)
                self.assertIs(envelope["project_layers_loaded"], False)
                self.assertIs(envelope["network_access"]["derived_from"]["project_layers_loaded"], False)
                loaded = launcher.codex_arguments({**envelope, "user_config_loaded": True})
                self.assertNotEqual(loaded, launcher.codex_arguments(envelope))
                # Account-level app connectors are not user config; the wrapper disables them explicitly.
                self.assertEqual(envelope["apps"], "disabled")
                self.assertNotEqual(launcher.codex_arguments({**envelope, "apps": None}), launcher.codex_arguments(envelope))

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
        self.assertIn(b"does not list model selector gpt-5.6", model_rejected.stderr)
        self.assertEqual(effort_rejected.returncode, 70)
        self.assertIn(b"does not list effort ultra", effort_rejected.stderr)
        self.assertFalse(review_invoked)

    def test_effective_selector_is_verified_from_the_runtime_banner(self):
        """Catalog listing is a pre-task observation; the banner is the execution evidence and must match."""
        canary = "printf 'CODEX_AUTH_OK\\n' > \"$out\"\n"
        block = "OpenAI Codex v9.9.9\n--------\n{}\n--------"
        cases = {
            "exact model and effort": (None, (*TERRA, "--effort", "high"), 0, b""),
            "substituted model": (block.format("model: gpt-5.6-luna\nreasoning effort: high"), (*TERRA, "--effort", "high"), 70, b"instead of the requested gpt-5.6-terra"),
            "different effort": (block.format("model: gpt-5.6-terra\nreasoning effort: low"), (*TERRA, "--effort", "high"), 70, b"effort low instead of the requested high"),
            "no effective model reported": ("", TERRA, 70, b"did not report its effective model"),
            "model line only in the echoed transcript": ("codex\nmodel: gpt-5.6-terra\nreasoning effort: high", (*TERRA, "--effort", "high"), 70, b"did not report its effective model"),
            "transcript line after a genuine banner is ignored": (block.format("model: gpt-5.6-terra\nreasoning effort: high") + "\ncodex\nmodel: gpt-5.6-luna", (*TERRA, "--effort", "high"), 0, b""),
        }
        for label, (banner, selector, code, message) in cases.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as temporary_directory:
                executable = self.make_fake_codex(Path(temporary_directory), canary, banner=banner)
                completed = self.run_launcher(executable, "--auth-preflight", selector=selector)
                self.assertEqual(completed.returncode, code, completed.stderr.decode())
                self.assertIn(message, completed.stderr)
                self.assertEqual(completed.stdout, b"CODEX_AUTH_OK\n" if code == 0 else b"")

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

    def test_auth_classification_reads_runtime_error_lines_not_the_echoed_transcript(self):
        """Codex echoes the model's text on stderr; only its runtime error lines are credential evidence."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            diagnostic = self.make_fake_codex(
                root, "printf '2026-09-13T07:57:42Z ERROR codex_api::endpoint: HTTP error: 401 Unauthorized\\n' >&2\nexit 1\n"
            )
            diagnostic_result = self.run_launcher(diagnostic, prompt=b"Review\n")
            transcript = self.make_fake_codex(
                root,
                "printf 'codex\\nThe handler returns 401 Unauthorized when the token is missing.\\n' >&2\n"
                "printf 'stream closed unexpectedly\\n' >&2\nexit 1\n",
            )
            transcript_result = self.run_launcher(transcript, prompt=b"Review\n")
        self.assertEqual(diagnostic_result.returncode, 78)
        self.assertIn(b"authentication needs operator attention", diagnostic_result.stderr)
        self.assertEqual(transcript_result.returncode, 70)
        self.assertIn(b"substantive review output", transcript_result.stderr)
        self.assertNotIn(b"authentication needs operator attention", transcript_result.stderr)

    def test_auth_failure_diagnostics_are_redacted_and_can_be_retained(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            executable = self.make_fake_codex(
                root,
                "printf '2026-09-13T07:57:42Z ERROR codex_api::endpoint: HTTP error: 401 Unauthorized token=super-secret-value Authorization: Bearer another-secret sk-proj-bare-secret\\n' >&2\nexit 1\n",
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
