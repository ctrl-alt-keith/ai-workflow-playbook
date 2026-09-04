from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_global_bootstrap.py"
PROJECTIONS = ROOT / "distributions" / "global-bootstrap"
ROUTER = PROJECTIONS / "bootstrap-router.md"
START_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:start -->"
END_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:end -->"


class GlobalBootstrapTests(unittest.TestCase):
    def marked(self, router: str) -> str:
        return f"{START_MARKER}\n{router}{END_MARKER}\n"

    def run_check(
        self, codex_file: Path, claude_file: Path, *, require_claude: bool = False
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(SCRIPT),
            "--codex-file",
            str(codex_file),
            "--claude-file",
            str(claude_file),
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

    def test_one_router_encodes_persistent_material_change_boundary(self) -> None:
        # This source is installed byte-for-byte into managed instruction blocks;
        # its exact bootstrap boundary is the distributed contract.
        exact_boundary = (
            "Before the first project action, and again only when the "
            "task/repository materially changes"
        )
        contents = ROUTER.read_text(encoding="utf-8")
        normalized = " ".join(contents.split())
        self.assertIn(exact_boundary, normalized)
        self.assertIn("reuse the still-current repository operating mode", normalized)
        self.assertIn("do not retrieve `start-here.md` again merely", normalized)
        self.assertIn(
            "When the first-action or material-change trigger applies, "
            "retrieving and applying `start-here.md` is the only permitted action:",
            normalized,
        )
        self.assertIn(
            "If it cannot be retrieved or read, the only permitted response is "
            "to say so plainly",
            normalized,
        )
        self.assertIn("do not proceed from memory", normalized)
        self.assertIn(
            "the only permitted action: Do not respond, reason about the task, "
            "or invoke another tool before applying it.",
            normalized,
        )
        for removed_copy in (
            "codex-AGENTS.md",
            "claude-CLAUDE.md",
            "chatgpt-custom-instructions.md",
        ):
            self.assertFalse((PROJECTIONS / removed_copy).exists())

    def test_router_projects_chat_work_latch_to_adapter_owner(self) -> None:
        contents = ROUTER.read_text(encoding="utf-8")
        normalized = " ".join(contents.split())

        self.assertIn("remain in Chat unless", normalized)
        self.assertIn("explicitly asks", normalized)
        self.assertIn("explicitly accepts", normalized)
        self.assertIn("docs/tool-adapters/chatgpt.md", contents)
        self.assertNotIn("task complexity", contents.lower())
        self.assertNotIn("browser", contents.lower())
        self.assertNotIn("file work", contents.lower())

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


if __name__ == "__main__":
    unittest.main()
