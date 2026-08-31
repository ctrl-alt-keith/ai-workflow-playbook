from dataclasses import dataclass, replace
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "docs" / "prompts.md"

STAGES = (
    "artifact-production",
    "artifact-classification",
    "operator-viewer-resolution",
    "execution-recipient-resolution",
    "capability-and-transport-resolution",
    "presentation-selection",
    "renderer-selection",
    "delivery-outcome",
)


@dataclass(frozen=True)
class DeliveryCase:
    """Resolved semantic inputs for the test-only conformance evaluator.

    request_text identifies the conversational fixture but is deliberately not
    interpreted by the evaluator. The Playbook owns semantic classification;
    this harness checks composition after those semantic inputs are resolved.
    """

    request_text: str
    produces_prompt: bool
    complete_executable: bool
    operator_viewer: str
    execution_recipient: str
    recipient_class: str
    capability_resolved: bool = True
    qualified_file_capability: bool = False
    permitted_file_destination: bool = False
    inline_fallback_permitted: bool = False


def decision_trace(case):
    """Evaluate the documented stage table without parsing request phrases."""

    production = "prompt-produced" if case.produces_prompt else "no-prompt"
    classification = (
        "complete-executable"
        if case.produces_prompt and case.complete_executable
        else "conceptual-fragment"
    )

    if classification == "conceptual-fragment":
        route = "not-applicable"
    elif case.recipient_class == "human":
        route = "inline-route"
    elif not case.capability_resolved:
        route = "blocked"
    elif case.qualified_file_capability and case.permitted_file_destination:
        route = "qualified-file-route"
    elif case.inline_fallback_permitted:
        route = "inline-fallback-permitted"
    else:
        route = "blocked"

    if classification == "conceptual-fragment":
        presentation = "lightweight"
    elif route == "qualified-file-route":
        presentation = "file-backed"
    elif route in ("inline-route", "inline-fallback-permitted"):
        presentation = "inline"
    else:
        presentation = "blocked"

    renderer = {
        "lightweight": "lightweight",
        "file-backed": "thin-handoff",
        "inline": "canonical-inline-two-block",
        "blocked": "none",
    }[presentation]
    outcome = {
        "lightweight": "lightweight-response",
        "file-backed": "dropbox-backed-thin-handoff",
        "inline": "inline-complete-prompt",
        "blocked": "blocked-no-renderer",
    }[presentation]

    return (
        (STAGES[0], production),
        (STAGES[1], classification),
        (STAGES[2], case.operator_viewer),
        (
            STAGES[3],
            f"{case.execution_recipient}:{case.recipient_class}",
        ),
        (STAGES[4], route),
        (STAGES[5], presentation),
        (STAGES[6], renderer),
        (STAGES[7], outcome),
    )


class PromptDeliveryDecisionModelTests(unittest.TestCase):
    def test_docs_define_one_ordered_model_with_explicit_stage_outputs(self):
        prompts = PROMPTS.read_text(encoding="utf-8")
        section = prompts[
            prompts.index("## Prompt Delivery Decision Model") : prompts.index(
                "## Cross-Executor Prompt Presentation"
            )
        ]
        normalized_section = " ".join(section.split())

        positions = [section.index(f"`{stage}`") for stage in STAGES]
        self.assertEqual(positions, sorted(positions))
        for output in (
            "`complete-executable`",
            "`machine-executor`",
            "`qualified-file-route`",
            "`inline-route`",
            "`file-backed`",
            "`canonical-inline-two-block`",
            "`blocked`",
        ):
            self.assertIn(output, section)
        self.assertIn(
            "must not re-read conversational wording to replace that output",
            normalized_section,
        )
        self.assertIn(
            "operator or viewer separate from the executable prompt's execution recipient",
            normalized_section,
        )

    def test_cold_start_prompt_variants_select_dropbox_codex_handoff(self):
        initial_instruction = (
            "I've cleared this project's memory and restarted the app. Let's "
            "discuss CAK-194 and prepare to hand its implementation to Codex. "
            "Do not start CAK-194, change its workflow state, or mutate "
            "provider/repository state yet."
        )
        self.assertIn("prepare to hand its implementation to Codex", initial_instruction)

        base = DeliveryCase(
            request_text="Prompt me for CAK-194.",
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
            qualified_file_capability=True,
            permitted_file_destination=True,
        )
        expected = (
            ("artifact-production", "prompt-produced"),
            ("artifact-classification", "complete-executable"),
            ("operator-viewer-resolution", "human-operator"),
            ("execution-recipient-resolution", "Codex:machine-executor"),
            ("capability-and-transport-resolution", "qualified-file-route"),
            ("presentation-selection", "file-backed"),
            ("renderer-selection", "thin-handoff"),
            ("delivery-outcome", "dropbox-backed-thin-handoff"),
        )

        for wording in (
            "Prompt me for CAK-194.",
            "Show me the Codex handoff for CAK-194.",
            "Give me the prompt for CAK-194.",
        ):
            with self.subTest(wording=wording):
                trace = decision_trace(replace(base, request_text=wording))
                self.assertEqual(trace, expected)
                self.assertNotIn(
                    "canonical-inline-two-block",
                    [output for _, output in trace],
                )

    def test_conceptual_human_fragment_remains_lightweight(self):
        case = DeliveryCase(
            request_text="What might a short stop boundary look like?",
            produces_prompt=True,
            complete_executable=False,
            operator_viewer="human-operator",
            execution_recipient="human",
            recipient_class="human",
        )

        trace = dict(decision_trace(case))
        self.assertEqual(trace["artifact-classification"], "conceptual-fragment")
        self.assertEqual(trace["presentation-selection"], "lightweight")
        self.assertEqual(trace["renderer-selection"], "lightweight")
        self.assertEqual(trace["delivery-outcome"], "lightweight-response")

    def test_inline_renderer_requires_selected_inline_fallback(self):
        base = DeliveryCase(
            request_text="Prepare the executable Codex handoff.",
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
        )

        fallback = dict(
            decision_trace(replace(base, inline_fallback_permitted=True))
        )
        self.assertEqual(
            fallback["capability-and-transport-resolution"],
            "inline-fallback-permitted",
        )
        self.assertEqual(fallback["presentation-selection"], "inline")
        self.assertEqual(
            fallback["renderer-selection"], "canonical-inline-two-block"
        )

        blocked = dict(
            decision_trace(replace(base, capability_resolved=False))
        )
        self.assertEqual(
            blocked["capability-and-transport-resolution"], "blocked"
        )
        self.assertEqual(blocked["presentation-selection"], "blocked")
        self.assertEqual(blocked["renderer-selection"], "none")
        self.assertEqual(blocked["delivery-outcome"], "blocked-no-renderer")


if __name__ == "__main__":
    unittest.main()
