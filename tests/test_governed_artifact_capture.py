from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OWNER_HEADING = "## Governed Artifact Capture"
OWNER_LINK = "evidence-lifecycle.md#governed-artifact-capture"


class GovernedArtifactCaptureTests(unittest.TestCase):
    def test_evidence_lifecycle_is_the_unique_semantic_owner(self):
        owners = []
        for path in DOCS.rglob("*.md"):
            if OWNER_HEADING in path.read_text(encoding="utf-8").splitlines():
                owners.append(path.relative_to(DOCS).as_posix())
        self.assertEqual(owners, ["evidence-lifecycle.md"])

        for relative_path in (
            "prompts.md",
            "tool-adapters/codex.md",
        ):
            contents = (DOCS / relative_path).read_text(encoding="utf-8")
            self.assertIn(OWNER_LINK, contents, relative_path)


if __name__ == "__main__":
    unittest.main()
