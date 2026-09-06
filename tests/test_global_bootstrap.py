from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_global_bootstrap.py"
PROJECTIONS = ROOT / "distributions" / "global-bootstrap"
ROUTER = PROJECTIONS / "bootstrap-router.md"
START_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:start -->"
END_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:end -->"


def load_script_module():
    spec = importlib.util.spec_from_file_location("global_bootstrap", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GlobalBootstrapTests(unittest.TestCase):
    def marked(self, router: str) -> str:
        return f"{START_MARKER}\n{router}{END_MARKER}\n"

    def run_check(
        self,
        codex_file: Path,
        claude_file: Path,
        *,
        mode: str = "check",
        require_claude: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(SCRIPT),
            "--codex-file",
            str(codex_file),
            "--claude-file",
            str(claude_file),
            "--mode",
            mode,
        ]
        if require_claude:
            command.append("--require-claude")
        return subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_validator_accepts_exact_blocks_with_unrelated_local_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            router = ROUTER.read_text(encoding="utf-8")
            codex = self.marked(router)
            claude = self.marked(router)
            codex_file.write_text(
                f"Personal preface.\n\n{codex}\nPersonal suffix.\n", encoding="utf-8"
            )
            claude_file.write_text(
                f"Personal preface.\n\n{claude}\nPersonal suffix.\n", encoding="utf-8"
            )

            result = self.run_check(codex_file, claude_file)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS Codex", result.stdout)
            self.assertIn("PASS Claude", result.stdout)
            self.assertEqual(result.stderr, "")

    def test_validator_skips_absent_optional_claude_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "missing-CLAUDE.md"
            codex_file.write_text(
                self.marked(ROUTER.read_text(encoding="utf-8")), encoding="utf-8"
            )

            optional = self.run_check(codex_file, claude_file)
            required = self.run_check(
                codex_file, claude_file, require_claude=True
            )

            self.assertEqual(optional.returncode, 0, optional.stdout)
            self.assertIn("SKIP Claude: broader-rollout", optional.stdout)
            self.assertIn("PASS Codex", optional.stdout)
            self.assertEqual(required.returncode, 1)
            self.assertIn("FAIL Claude: missing local instruction file", required.stdout)

    def test_validator_normalizes_outer_newlines_symmetrically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            router = ROUTER.read_text(encoding="utf-8").rstrip("\n") + "\n\n"
            codex_file.write_text(self.marked(router), encoding="utf-8")
            claude_file.write_text(self.marked(router), encoding="utf-8")

            result = self.run_check(codex_file, claude_file)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_reports_drift_without_writing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            router = ROUTER.read_text(encoding="utf-8")
            codex = self.marked(router)
            claude = self.marked(router)
            codex_file.write_text(
                codex.replace("first project action", "every action"), encoding="utf-8"
            )
            claude_file.write_text(claude, encoding="utf-8")
            before = codex_file.read_bytes()

            result = self.run_check(codex_file, claude_file)

            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL Codex: managed body differs", result.stdout)
            self.assertEqual(codex_file.read_bytes(), before)
            self.assertEqual(result.stderr, "")

    def test_validator_rejects_missing_or_duplicate_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            projection = self.marked(ROUTER.read_text(encoding="utf-8"))
            codex_file.write_text("unmanaged instructions only\n", encoding="utf-8")
            claude_file.write_text(projection + projection, encoding="utf-8")

            result = self.run_check(codex_file, claude_file)

            self.assertEqual(result.returncode, 1)
            self.assertIn("expected exactly one", result.stdout)
            self.assertEqual(result.stderr, "")

    def test_plan_is_read_only_and_shows_the_exact_managed_body_diff(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            router = ROUTER.read_text(encoding="utf-8")
            codex_file.write_text(
                self.marked(router.replace("first project action", "every action")),
                encoding="utf-8",
            )
            claude_file.write_text(self.marked(router), encoding="utf-8")
            before = codex_file.read_bytes()

            result = self.run_check(codex_file, claude_file, mode="plan")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PLAN Codex: replace managed body", result.stdout)
            self.assertIn("--- ", result.stdout)
            self.assertIn("PASS Claude: already current", result.stdout)
            self.assertEqual(codex_file.read_bytes(), before)

    def test_apply_replaces_only_the_managed_body_and_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            router = ROUTER.read_text(encoding="utf-8")
            drifted = self.marked(router.replace("first project action", "every action"))
            prefix = b"Personal preface.\r\n\r\n"
            suffix = b"\r\nPersonal suffix.\r\n"
            codex_file.write_bytes(prefix + drifted.encode("utf-8") + suffix)
            claude_file.write_text(self.marked(router), encoding="utf-8")

            result = self.run_check(codex_file, claude_file, mode="apply")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("APPLY Codex: verified", result.stdout)
            self.assertIn("PASS Claude: already current", result.stdout)
            contents = codex_file.read_bytes()
            self.assertTrue(contents.startswith(prefix))
            self.assertTrue(contents.endswith(suffix))
            self.assertIn(self.marked(router).encode("utf-8"), contents)

    def test_plan_and_apply_fail_closed_for_malformed_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            codex_file.write_text("unmanaged instructions only\n", encoding="utf-8")
            claude_file.write_text(
                self.marked(ROUTER.read_text(encoding="utf-8")) * 2,
                encoding="utf-8",
            )

            for mode in ("plan", "apply"):
                result = self.run_check(codex_file, claude_file, mode=mode)
                self.assertEqual(result.returncode, 1)
                self.assertIn("expected exactly one", result.stdout)

    def test_apply_preflight_preserves_other_files_when_any_surface_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            router = ROUTER.read_text(encoding="utf-8")
            codex_file.write_text(
                self.marked(router.replace("first project action", "every action")),
                encoding="utf-8",
            )
            claude_file.write_text("unmanaged instructions only\n", encoding="utf-8")
            before = codex_file.read_bytes()

            result = self.run_check(codex_file, claude_file, mode="apply")

            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL apply preflight", result.stdout)
            self.assertEqual(codex_file.read_bytes(), before)

    def test_apply_rejects_symlinked_instruction_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "actual-AGENTS.md"
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            target.write_text(self.marked(ROUTER.read_text(encoding="utf-8")), encoding="utf-8")
            codex_file.symlink_to(target)
            claude_file.write_text(self.marked(ROUTER.read_text(encoding="utf-8")), encoding="utf-8")

            result = self.run_check(codex_file, claude_file, mode="apply")

            self.assertEqual(result.returncode, 1)
            self.assertIn("unsupported local instruction file type", result.stdout)

    def test_apply_fails_closed_when_state_changes_before_replacement(self) -> None:
        module = load_script_module()
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "AGENTS.md"
            router = module.normalize_router(ROUTER.read_text(encoding="utf-8"))
            target.write_text(
                self.marked(router.replace("first project action", "every action")),
                encoding="utf-8",
            )
            check = module.Check("Codex", target)
            initial = module.inspect(check)
            target.write_text(
                self.marked(router.replace("first project action", "changed action")),
                encoding="utf-8",
            )
            changed = module.inspect(check)

            with mock.patch.object(module, "inspect", side_effect=[initial, changed]):
                with self.assertRaisesRegex(ValueError, "changed before"):
                    module.apply(check, router)


if __name__ == "__main__":
    unittest.main()
