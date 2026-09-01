from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def normalized_section(path, start, end):
    contents = path.read_text(encoding="utf-8")
    section = contents[contents.index(start) : contents.index(end)]
    return " ".join(section.split())


class CrossThreadArtifactPreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intermediates = normalized_section(
            DOCS / "evidence-lifecycle.md",
            "### Cross-thread-useful intermediate artifacts",
            "### Storage Admission",
        )
        cls.prompt_ownership = normalized_section(
            DOCS / "prompt-contracts.md",
            "### Ownership selection",
            "### One durable identity",
        )
        cls.review_routing = normalized_section(
            DOCS / "external-ai-reviewer.md",
            "### Review output preservation and discussion routing",
            "### Governed reviewer launch and completion",
        )

    def test_intermediate_threshold_requires_downstream_exact_identity_value(self):
        for phrase in (
            "expected downstream consumer is a useful signal, but it is not sufficient",
            "substantial",
            "need an exact identity for the downstream dependency",
            "lossy or meaningfully weaker if reconstructed",
            "not from the executor or provider that produced it",
            "Apply this symmetrically to cross-executor handoffs",
        ):
            self.assertIn(phrase, self.intermediates)

    def test_preservation_and_disposal_cases_remain_distinct(self):
        for preserved in (
            "complete review output",
            "analysis package",
            "finding-disposition input",
            "implementation handoff",
            "temporary design document",
        ):
            self.assertIn(preserved, self.intermediates)
        for disposable in (
            "Disposable scratch",
            "conversational scaffolding",
            "redundant summaries",
            "easily regenerated notes",
        ):
            self.assertIn(disposable, self.intermediates)

    def test_compact_pointer_replaces_incidental_full_artifact_storage(self):
        for phrase in (
            "compact context plus its exact durable identity",
            "pull-request comment",
            "planning-system comment",
            "incidental discussion surface does not become the durable artifact store",
            "mandatory capture failure boundary",
        ):
            self.assertIn(phrase, self.intermediates)

    def test_review_owner_routes_complete_output_and_failed_attempts(self):
        for phrase in (
            "preserve the complete review",
            "concise verdict, material finding disposition",
            "immutable pointer or identity",
            "Do not paste the complete review",
            "failed and non-verdict attempts",
            "terminal receipt",
        ):
            self.assertIn(phrase, self.review_routing)
        self.assertNotIn("Dropbox", self.review_routing)

    def test_preservation_does_not_inflate_authority_or_status(self):
        for phrase in (
            "accepted evidence",
            "canonical doctrine",
            "approved decision",
            "completed work",
            "transition authority",
        ):
            self.assertIn(phrase, self.intermediates)
        for phrase in ("approval", "merge authority", "completion"):
            self.assertIn(phrase, self.review_routing)

    def test_issue_owned_prompt_profile_rejects_non_issue_placement(self):
        for phrase in (
            "issue-oriented destination is not a universal prompt-artifact root",
            "another existing natural durable owner",
            "Do not place non-issue material under an issue-like path",
            "invent a planning issue solely to obtain storage",
            "new durable root merely for naming symmetry",
            "fails storage admission until a natural durable owner is established",
        ):
            self.assertIn(phrase, self.prompt_ownership)


if __name__ == "__main__":
    unittest.main()
