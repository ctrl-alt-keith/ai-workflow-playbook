from dataclasses import dataclass
import unittest


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
            DeliveryCase(
                recipient="codex",
                qualifying_small_canonical_text=True,
                airtable_route_permitted=True,
            ),
            DeliveryCase(recipient=None),
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(decide(case), "blocked")

if __name__ == "__main__":
    unittest.main()
