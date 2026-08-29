from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_global_bootstrap.py"
PROJECTIONS = ROOT / "distributions" / "global-bootstrap"


class GlobalBootstrapTests(unittest.TestCase):
    def run_check(
        self, codex_file: Path, claude_file: Path
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--codex-file",
                str(codex_file),
                "--claude-file",
                str(claude_file),
            ],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_projections_encode_persistent_material_change_boundary(self) -> None:
        exact_boundary = (
            "Before the first project action, and again only when the "
            "task/repository materially changes"
        )
        for name in (
            "codex-AGENTS.md",
            "claude-CLAUDE.md",
            "chatgpt-custom-instructions.md",
        ):
            contents = (PROJECTIONS / name).read_text(encoding="utf-8")
            normalized = " ".join(contents.split())
            self.assertIn(exact_boundary, normalized)
            self.assertIn("reuse the still-current repository operating mode", normalized)
            self.assertIn("do not retrieve `start-here.md` again merely", normalized)

    def test_validator_accepts_exact_blocks_with_unrelated_local_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            codex = (PROJECTIONS / "codex-AGENTS.md").read_text(encoding="utf-8")
            claude = (PROJECTIONS / "claude-CLAUDE.md").read_text(encoding="utf-8")
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

    def test_validator_reports_drift_without_writing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            codex = (PROJECTIONS / "codex-AGENTS.md").read_text(encoding="utf-8")
            claude = (PROJECTIONS / "claude-CLAUDE.md").read_text(encoding="utf-8")
            codex_file.write_text(
                codex.replace("first project action", "every action"), encoding="utf-8"
            )
            claude_file.write_text(claude, encoding="utf-8")
            before = codex_file.read_bytes()

            result = self.run_check(codex_file, claude_file)

            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL Codex: managed block differs", result.stdout)
            self.assertEqual(codex_file.read_bytes(), before)
            self.assertEqual(result.stderr, "")

    def test_validator_rejects_missing_or_duplicate_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            projection = (PROJECTIONS / "claude-CLAUDE.md").read_text(
                encoding="utf-8"
            )
            codex_file.write_text("unmanaged instructions only\n", encoding="utf-8")
            claude_file.write_text(projection + projection, encoding="utf-8")

            result = self.run_check(codex_file, claude_file)

            self.assertEqual(result.returncode, 1)
            self.assertIn("expected exactly one", result.stdout)
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
