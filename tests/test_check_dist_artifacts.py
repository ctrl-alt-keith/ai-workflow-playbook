from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

SCRIPT_PATH = SCRIPTS_DIR / "check_dist_artifacts.py"
SPEC = importlib.util.spec_from_file_location("check_dist_artifacts", SCRIPT_PATH)
assert SPEC is not None
checker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


class DistArtifactCheckTest(unittest.TestCase):
    def test_check_artifact_passes_for_current_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            artifact_path = tmp / "dist/example.md"
            artifact_path.parent.mkdir()
            artifact_path.write_text("current\n", encoding="utf-8")
            artifact = checker.Artifact(
                path=artifact_path,
                make_target="example",
                render_expected=lambda _manifest: "current\n",
            )

            with mock.patch("sys.stdout"):
                self.assertTrue(
                    checker.check_artifact(artifact, tmp / "manifest.txt", False)
                )

    def test_check_artifact_fails_for_stale_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            artifact_path = tmp / "dist/example.md"
            artifact_path.parent.mkdir()
            artifact_path.write_text("stale\n", encoding="utf-8")
            artifact = checker.Artifact(
                path=artifact_path,
                make_target="example",
                render_expected=lambda _manifest: "current\n",
            )

            with mock.patch("sys.stderr"):
                self.assertFalse(
                    checker.check_artifact(artifact, tmp / "manifest.txt", False)
                )

    def test_missing_artifact_is_skipped_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            artifact = checker.Artifact(
                path=tmp / "dist/example.md",
                make_target="example",
                render_expected=lambda _manifest: "current\n",
            )

            with mock.patch("sys.stdout"):
                self.assertTrue(
                    checker.check_artifact(artifact, tmp / "manifest.txt", False)
                )

    def test_missing_artifact_can_be_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            artifact = checker.Artifact(
                path=tmp / "dist/example.md",
                make_target="example",
                render_expected=lambda _manifest: "current\n",
            )

            with mock.patch("sys.stderr"):
                self.assertFalse(
                    checker.check_artifact(artifact, tmp / "manifest.txt", True)
                )

    def test_context_refresh_normalizes_generated_timestamp(self) -> None:
        self.assertEqual(
            checker.normalize_context_refresh("Generated: 2026-05-11T01:02:03Z\n"),
            "Generated: <normalized>\n",
        )


if __name__ == "__main__":
    unittest.main()
