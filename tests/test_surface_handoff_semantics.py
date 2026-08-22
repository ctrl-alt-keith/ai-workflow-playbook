from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class SurfaceHandoffSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.core = normalized(DOCS / "core-model.md")
        cls.prompts = normalized(DOCS / "prompts.md")
        cls.chatgpt = normalized(DOCS / "tool-adapters" / "chatgpt.md")

    def test_core_owns_controller_executor_role_and_zero_authority_boundary(self):
        for phrase in (
            "Interactive Control And Bounded Execution",
            "semantic roles, not universal product identities or authority classes",
            "bounded deliverable and execution contract, not difficulty or model choice",
            "does not become canonical, universally authoritative, or a required intermediary",
            "fail closed where the applicable contract or exact recoverable state cannot be resolved",
        ):
            self.assertIn(phrase, self.core)

    def test_surface_selection_preserves_distinct_dimensions_and_task_shape(self):
        for phrase in (
            "Interaction surface",
            "Executor identity",
            "Task shape",
            "Model or reasoning choice",
            "Handoff contract",
            "Durable package pointer",
            "Durable continuity",
            "choose Work for a bounded general-purpose multi-step outcome",
            "choose Codex when completion materially depends on repository locality",
            "Difficulty, model tier, and reasoning setting do not select a surface",
            "Ordinary chat, brainstorming, and conceptual discussion remain lightweight",
        ):
            self.assertIn(phrase, self.prompts)

    def test_transition_is_proportional_and_refreshes_mutable_owners(self):
        for phrase in (
            "Surface-transition check",
            "re-evaluate context sufficiency",
            "acting identity",
            "refresh mutable repository, GitHub, planning-system, and provider facts",
            "Reuse still-current verified context",
            "does not require blanket rehydration",
        ):
            self.assertIn(phrase, self.prompts)

    def test_thin_envelope_requires_exact_identity_and_fails_closed(self):
        for phrase in (
            "exact self-describing governed manifest or sealed-package identity",
            "These are semantic fields, not an operational package schema",
            "exact identity evidence required by the owning package contract",
            "bare folder path is navigation only",
            "creates zero authority itself",
            "recorded next action remains historical or asserted instruction",
            "inaccessible, unresolved, stale, mismatched, or ambiguous",
            "Do not reconstruct missing contract, authority, or evidence from conversation memory",
        ):
            self.assertIn(phrase, self.prompts)

    def test_work_and_codex_handoffs_are_target_shaped(self):
        for phrase in (
            "Target: Work — bounded general-purpose outcome",
            "Tools and locality: [permitted connected sources and execution location]",
            "Return boundary: [return to Chat for review or stop condition]",
            "Target: Codex — repository execution",
            "Repository and locality: [repository, worktree, branch, relevant surface]",
            "Validation and delivery: [canonical command, outputs, commit/push/PR expectation]",
        ):
            self.assertIn(phrase, self.prompts)

    def test_all_required_examples_are_present(self):
        for phrase in (
            "Difficult architecture discussion remains in Chat",
            "Source-backed report moves from Chat to Work",
            "Repository implementation moves from Chat to Codex",
            "Discussion becomes delegated execution",
            "Worker result returns to Chat",
            "Package reference fails closed",
        ):
            self.assertIn(phrase, self.prompts)

    def test_chatgpt_projection_keeps_one_adapter_and_verifies_package_access(self):
        self.assertIn("Chat is the normal interactive control plane", self.chatgpt)
        self.assertIn("Work is the preferred ChatGPT surface", self.chatgpt)
        self.assertIn("nested surfaces under one ChatGPT adapter", self.chatgpt)
        self.assertIn("Inspect or attempt retrieval", self.chatgpt)
        self.assertIn("Listing a folder or reaching a mutable package root", self.chatgpt)
        self.assertFalse((DOCS / "tool-adapters" / "work.md").exists())


if __name__ == "__main__":
    unittest.main()
