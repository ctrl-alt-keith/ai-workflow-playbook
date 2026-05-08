from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

SCRIPT_PATH = SCRIPTS_DIR / "generate_github_context.py"
SPEC = importlib.util.spec_from_file_location("generate_github_context", SCRIPT_PATH)
assert SPEC is not None
generator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = generator
SPEC.loader.exec_module(generator)


class GitHubContextGeneratorTest(unittest.TestCase):
    def test_render_github_context_outputs_paste_ready_block(self) -> None:
        content = generator.render_github_context(
            (
                "ctrl-alt-keith/first",
                "ctrl-alt-keith/second",
            )
        )

        self.assertTrue(
            content.startswith(
                "\n".join(
                    [
                        "# GitHub Connector Context",
                        "Status: generated snapshot",
                        "Canonical: false",
                        (
                            "This file is a generated convenience artifact for "
                            "refreshing GitHub connector repo context in fresh threads."
                        ),
                    ]
                )
            )
        )
        self.assertIn(
            "\n".join(
                [
                    "```text",
                    "@GitHub ctrl-alt-keith/first",
                    "@GitHub ctrl-alt-keith/second",
                    "```",
                ]
            ),
            content,
        )


if __name__ == "__main__":
    unittest.main()
