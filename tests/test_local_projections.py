from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "local_projections.py"
ROUTER = ROOT / "distributions" / "global-bootstrap" / "bootstrap-router.md"
START = "<!-- ai-workflow-playbook:global-bootstrap:start -->"
END = "<!-- ai-workflow-playbook:global-bootstrap:end -->"


def load_module():
    spec = importlib.util.spec_from_file_location("local_projections", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
            ],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_global_projection_delegates_real_check_plan_apply_and_verification(self) -> None:
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

            check = self.run_global("check", codex_file, claude_file)
            plan = self.run_global("plan", codex_file, claude_file)

            self.assertEqual(check.returncode, 1)
            self.assertIn("FAIL Codex", check.stdout)
            self.assertEqual(plan.returncode, 0, plan.stdout + plan.stderr)
            self.assertIn("PLAN Codex", plan.stdout)
            self.assertEqual(codex_file.read_bytes(), before)
            apply = self.run_global("apply", codex_file, claude_file)
            self.assertEqual(apply.returncode, 0, apply.stdout + apply.stderr)
            self.assertIn("APPLY Codex: verified", apply.stdout)
            self.assertIn("PASS Codex", apply.stdout)

    def test_apply_stops_before_other_components_when_claude_review_is_drifted(self) -> None:
        module = load_module()
        arguments = SimpleNamespace(
            mode="apply",
            component=None,
            codex_file=None,
            claude_file=None,
            require_claude=False,
        )
        drifted = module.CommandResult("claude-review", 1, "DRIFT claude-review: fixture\n")
        output = io.StringIO()
        with mock.patch.object(module, "parse_args", return_value=arguments), mock.patch.object(
            module, "run", return_value=drifted
        ) as run, contextlib.redirect_stdout(output):
            self.assertEqual(module.main(), 1)

        self.assertEqual(run.call_count, 1)
        self.assertIn("FAIL apply preflight", output.getvalue())


if __name__ == "__main__":
    unittest.main()
