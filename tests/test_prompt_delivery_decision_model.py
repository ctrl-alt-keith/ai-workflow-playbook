from dataclasses import dataclass
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PROMPTS = DOCS / "prompts.md"


@dataclass(frozen=True)
class DeliveryCase:
    produces_prompt: bool = True
    complete: bool = True
    recipient: str | None = None
    qualifying_small_canonical_text: bool = False
    airtable_route_permitted: bool = False


def decide(case):
    if not case.produces_prompt:
        return "no-prompt"
    if not case.complete:
        return "lightweight"
    if case.recipient == "human":
        return "inline-two-block"
    if case.recipient in {"chatgpt", "claude"}:
        if case.qualifying_small_canonical_text and case.airtable_route_permitted:
            return "airtable-record-thin-handoff"
        return "blocked"
    return "blocked"


class PromptDeliveryDecisionModelTests(unittest.TestCase):
    def test_no_prompt_and_conceptual_outputs_stay_lightweight(self):
        self.assertEqual(decide(DeliveryCase(produces_prompt=False)), "no-prompt")
        self.assertEqual(decide(DeliveryCase(complete=False)), "lightweight")

    def test_human_recipient_gets_inline_complete_prompt(self):
        self.assertEqual(
            decide(DeliveryCase(recipient="human")),
            "inline-two-block",
        )

    def test_chatgpt_and_claude_use_airtable_for_qualifying_text(self):
        for recipient in ("chatgpt", "claude"):
            with self.subTest(recipient=recipient):
                self.assertEqual(
                    decide(
                        DeliveryCase(
                            recipient=recipient,
                            qualifying_small_canonical_text=True,
                            airtable_route_permitted=True,
                        )
                    ),
                    "airtable-record-thin-handoff",
                )

    def test_machine_handoff_fails_closed_without_exact_airtable_route(self):
        cases = (
            DeliveryCase(recipient="chatgpt"),
            DeliveryCase(
                recipient="claude",
                qualifying_small_canonical_text=True,
                airtable_route_permitted=False,
            ),
            DeliveryCase(
                recipient="chatgpt",
                qualifying_small_canonical_text=False,
                airtable_route_permitted=True,
            ),
            DeliveryCase(recipient=None),
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(decide(case), "blocked")

    def test_request_wording_does_not_override_recipient_route(self):
        expected = decide(
            DeliveryCase(
                recipient="claude",
                qualifying_small_canonical_text=True,
                airtable_route_permitted=True,
            )
        )
        for request_word in ("example", "sample", "preview", "demo"):
            with self.subTest(request_word=request_word):
                self.assertEqual(expected, "airtable-record-thin-handoff")

    def test_documented_model_is_small_and_has_no_fallback_ladder(self):
        text = PROMPTS.read_text(encoding="utf-8")
        model = text[
            text.index("## Prompt Delivery Decision Model") :
            text.index("## Cross-Executor Prompt Presentation")
        ].lower()
        self.assertIn("airtable record handoff", model)
        self.assertIn("file provider is not a fallback", model)
        self.assertIn("exact record id", model)
        for obsolete in (
            "re-entry",
            "alternate file route",
            "download-link",
            "transport-only latch",
            "connector confirmation",
        ):
            self.assertNotIn(obsolete, model)


if __name__ == "__main__":
    unittest.main()
