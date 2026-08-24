from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class KickoffMutationBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.core_raw = (DOCS / "core-model.md").read_text(encoding="utf-8")
        cls.prompts_raw = (DOCS / "prompts.md").read_text(encoding="utf-8")
        cls.core = " ".join(cls.core_raw.split())
        cls.prompts = " ".join(cls.prompts_raw.split())
        cls.prompt_contracts = normalized(DOCS / "prompt-contracts.md")

        prompt_start = cls.prompts_raw.index("## Explicit Kickoff Mutation Boundary")
        prompt_end = cls.prompts_raw.index(
            "## Thread Routing And Configuration Continuity"
        )
        cls.boundary_section = cls.prompts_raw[prompt_start:prompt_end]

        core_start = cls.core_raw.index("## Kickoff Mutation Boundaries")
        core_end = cls.core_raw.index("## Authority And Transitions")
        cls.core_boundary_section = cls.core_raw[core_start:core_end]

    def test_core_owns_the_three_class_authority_boundary(self):
        for phrase in (
            "Kickoff Mutation Boundaries",
            "Task-owned orchestration and evidence mutations may be permitted",
            "Delegated substantive execution is not implied",
            "Human-gated transitions remain separately human-gated",
            "requires its own bounded authority and satisfied prerequisites",
            "Unrelated planning items, repositories, providers, and execution state remain untouched",
        ):
            self.assertIn(phrase, self.core)

    def test_generated_prompts_require_an_explicit_boundary(self):
        for phrase in (
            "Every generated kickoff or orchestration prompt must declare an explicit",
            "Orchestration/evidence mutations",
            "Delegated substantive execution",
            "Human-gated transitions",
            "Unrelated state",
            "Blocked kickoff",
        ):
            self.assertIn(phrase, self.prompts)

        self.assertGreaterEqual(self.prompts_raw.count("Kickoff mutation boundary:"), 5)
        self.assertIn("`kickoff_mutation_boundary`", self.prompts_raw)

        for heading, next_heading in (
            ("## Repository Implementation Task", "## Parallel Batch Add-On"),
            ("## Orchestration Handoff", "## Governed Artifact Capture Add-On"),
            ("## PR Review", None),
        ):
            start = self.prompts_raw.index(heading)
            end = self.prompts_raw.index(next_heading) if next_heading else None
            template = self.prompts_raw[start:end]
            for field in (
                "Orchestration/evidence mutations:",
                "Delegated substantive execution:",
                "Human-gated transitions:",
                "Unrelated state:",
                "Blocked kickoff:",
            ):
                self.assertIn(field, template, f"{heading}: {field}")

    def test_read_only_and_blocked_kickoffs_are_narrow_and_fail_closed(self):
        for phrase in (
            "genuinely fully read-only, say why",
            "name the actor and mutation surfaces covered",
            "do not falsely advance the governing task",
            "record the exact blocker only when that task-owned write is useful and authorized",
            "must not mark the governing work in progress merely because kickoff occurred",
        ):
            self.assertIn(phrase, f"{self.core} {self.prompts}")

    def test_zero_authority_boundary_covers_execution_evidence(self):
        for phrase in (
            "planning status",
            "successful call",
            "storage object",
            "comment",
            "validation result",
            "retrieval",
            "review verdict",
            "branch",
            "commit",
            "pull request",
            "creates zero authority",
        ):
            self.assertIn(phrase, self.core)

    def test_shared_prompt_doctrine_is_provider_neutral(self):
        for provider_name in ("Dropbox", "Linear", "ChatGPT", "Codex"):
            self.assertNotIn(provider_name, self.boundary_section)
            self.assertNotIn(provider_name, self.core_boundary_section)

    def test_blanket_phrases_are_examples_not_instruction_substitutes(self):
        for phrase in (
            "`read-only first response`",
            "`no mutation on kickoff`",
            "`do not touch anything yet`",
            "as substitutes for the actual boundary",
        ):
            self.assertIn(phrase, self.boundary_section)

    def test_adjacent_owner_boundaries_remain_explicit(self):
        for phrase in (
            "does not redefine interactive-control or target-surface routing",
            "artifact storage admission, transport, delivery, retention, cleanup, or replay",
            "operator-visible progress and client behavior",
            "not prompt-contract machinery",
            "remain unable to drive lifecycle state or orchestration",
        ):
            self.assertIn(phrase, self.prompts)

        self.assertIn(
            "This is the no-authority, no-state-transition, and no-orchestration boundary",
            self.prompt_contracts,
        )

    def test_required_provider_neutral_examples_are_present(self):
        for phrase in (
            "Ready kickoff",
            "Blocked kickoff",
            "Architecture thread",
            "Destructive workflow",
            "Delegated repository implementation",
        ):
            self.assertIn(phrase, self.boundary_section)


if __name__ == "__main__":
    unittest.main()
