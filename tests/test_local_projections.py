#!/usr/bin/env python3
"""Regression tests for Playbook-managed local projection routing."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "local_projections.py"
ROUTER = ROOT / "distributions" / "global-bootstrap" / "bootstrap-router.md"
START = "<!-- ai-workflow-playbook:global-bootstrap:start -->"
END = "<!-- ai-workflow-playbook:global-bootstrap:end -->"


class LocalProjectionTests(unittest.TestCase):
    def marked(self, body: str) -> str:
        return f"{START}\n{body}{END}\n"

    def run_global(self, mode: str, codex_file: Path, claude_file: Path):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                mode,
                "--component",
                "global-bootstrap",
                "--codex-file",
                str(codex_file),
                "--claude-file",
                str(claude_file),
                "--require-claude",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_global_projection_delegates_real_check_plan_apply_and_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_file = root / "AGENTS.md"
            claude_file = root / "CLAUDE.md"
            router = ROUTER.read_text(encoding="utf-8")
            codex_file.write_text(self.marked(router), encoding="utf-8")
            claude_file.write_text(self.marked(router), encoding="utf-8")
            before = codex_file.read_bytes()

            check = self.run_global("check", codex_file, claude_file)
            plan = self.run_global("plan", codex_file, claude_file)

            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertIn("PASS Codex", check.stdout)
            self.assertEqual(plan.returncode, 0, plan.stdout + plan.stderr)
            self.assertIn("PASS Codex", plan.stdout)
            self.assertEqual(codex_file.read_bytes(), before)
            apply = self.run_global("apply", codex_file, claude_file)
            self.assertEqual(apply.returncode, 0, apply.stdout + apply.stderr)
            self.assertIn("PASS Codex", apply.stdout)


if __name__ == "__main__":
    unittest.main()
