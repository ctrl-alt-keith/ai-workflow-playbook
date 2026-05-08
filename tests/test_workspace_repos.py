from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from workspace_repos import (  # noqa: E402
    WorkspaceRepoManifestError,
    parse_workspace_repos,
    read_workspace_repos,
)


class WorkspaceReposTest(unittest.TestCase):
    def test_manifest_parser_preserves_order_and_ignores_comments(self) -> None:
        repos = parse_workspace_repos(
            "\n".join(
                [
                    "# comment",
                    "",
                    "ctrl-alt-keith/first",
                    "  ctrl-alt-keith/second  ",
                ]
            )
        )

        self.assertEqual(
            repos,
            ("ctrl-alt-keith/first", "ctrl-alt-keith/second"),
        )

    def test_manifest_parser_rejects_empty_manifest(self) -> None:
        with self.assertRaises(WorkspaceRepoManifestError):
            parse_workspace_repos("# comment\n\n")

    def test_manifest_parser_rejects_invalid_entries(self) -> None:
        with self.assertRaisesRegex(
            WorkspaceRepoManifestError,
            "expected owner/name",
        ):
            parse_workspace_repos("ctrl-alt-keith\n")

    def test_manifest_reader_rejects_missing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "missing.txt"

            with self.assertRaisesRegex(WorkspaceRepoManifestError, "missing"):
                read_workspace_repos(missing_path)


if __name__ == "__main__":
    unittest.main()
