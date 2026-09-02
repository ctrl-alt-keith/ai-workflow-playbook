from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OWNER = DOCS / "evidence-lifecycle.md"
PROMPTS = DOCS / "prompts.md"
CODEX = DOCS / "tool-adapters" / "codex.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


class GovernedArtifactCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.owner = normalized(OWNER)
        cls.prompts = normalized(PROMPTS)
        cls.codex = normalized(CODEX)

    def test_evidence_lifecycle_is_the_single_semantic_owner(self):
        self.assertIn("## Governed Artifact Capture", self.owner)
        self.assertIn("## Governed Artifact Capture Add-On", self.prompts)
        self.assertIn("## Governed Artifact Capture", self.codex)
        self.assertIn("evidence-lifecycle.md#governed-artifact-capture", self.prompts)
        self.assertIn("evidence-lifecycle.md#governed-artifact-capture", self.codex)
        self.assertNotIn("### Storage Admission", self.prompts)
        self.assertNotIn("### Storage Admission", self.codex)

    def test_candidate_floor_precedes_storage_permission(self):
        floor = (
            "the output is substantial rather than ordinary chat; 2. its exact "
            "identity is required for review, citation, disposition, decision, "
            "recovery, or another authorized downstream dependency; and 3. "
            "regeneration or conversation-only retention would weaken that "
            "downstream dependency"
        )
        self.assertIn(floor, self.owner)
        recognition = "Meeting the floor identifies a governed-artifact candidate only"
        permission = "All applicable privacy, visibility, licensing, retention"
        self.assertLess(self.owner.index(recognition), self.owner.index(permission))
        self.assertIn("Prohibited or uncertain retention fails closed", self.owner)
        self.assertIn("Routine work does not inherit governed-artifact ceremony", self.owner)

    def test_direct_capture_and_immutable_identity_are_protected(self):
        for phrase in (
            "Use one writer",
            "exclusive no-overwrite creation",
            "freeze the exact local bytes",
            "whole-file SHA-256",
            "Exact raw-byte readback is one qualified route",
            "provider-integrity route may instead compare authoritative stored size",
            "Re-observe containment and provider identity",
            "Corrections use a new identity with explicit lineage",
            "scratch is not a substitute for required durable capture",
        ):
            self.assertIn(phrase, self.owner)

    def test_receipt_role_surface_and_delivery_remain_distinct(self):
        for phrase in (
            "exactly one producing-receipt record",
            "smallest permitted append-only surface sufficient for recovery",
            "separate immutable producing-receipt artifact",
            "planning record references the separate receipt's exact identity",
            "later receipt-surface change creates a new receipt identity",
            "chat is not the producing receipt",
        ):
            self.assertIn(phrase, " ".join((self.owner, self.codex)))
        self.assertIn("compact conversation summary", self.prompts)

    def test_narrow_failure_evidence_and_authority_boundaries(self):
        for phrase in (
            "### Mandatory governed-artifact capture failure boundary",
            "prompt-contracts.md#mandatory-failure-boundary",
            "evidenced separately",
            "planning mutation, or downstream work",
            "transfer zero authority",
        ):
            self.assertIn(phrase, self.owner)

if __name__ == "__main__":
    unittest.main()
