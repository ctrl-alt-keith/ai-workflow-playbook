from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

SCRIPT_PATH = SCRIPTS_DIR / "generate_workspace_bootstrap.py"
SPEC = importlib.util.spec_from_file_location("generate_workspace_bootstrap", SCRIPT_PATH)
assert SPEC is not None
generator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = generator
SPEC.loader.exec_module(generator)


class WorkspaceBootstrapGeneratorTest(unittest.TestCase):
    def test_render_workspace_bootstrap_includes_sources_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            first = tmp / "first.md"
            second = tmp / "second.md"
            first.write_text("# First\n\nAlpha\n", encoding="utf-8")
            second.write_text("# Second\n\nBeta\n", encoding="utf-8")

            content = generator.render_workspace_bootstrap((first, second))

        self.assertTrue(content.startswith("# Workspace Bootstrap Context\n"))
        self.assertIn(f"## Source: `{first}`\n\n# First\n\nAlpha\n", content)
        self.assertIn(f"## Source: `{second}`\n\n# Second\n\nBeta\n", content)
        self.assertLess(
            content.index(f"## Source: `{first}`"),
            content.index(f"## Source: `{second}`"),
        )

    def test_render_workspace_bootstrap_fails_for_missing_source(self) -> None:
        with self.assertRaises(FileNotFoundError):
            generator.render_workspace_bootstrap((Path("missing.md"),))


if __name__ == "__main__":
    unittest.main()
