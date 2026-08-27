from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def markdown_section(path, heading):
    text = path.read_text(encoding="utf-8")
    start = text.index(heading)
    tail = text[start + len(heading) :]
    next_heading = re.search(r"\n#{1,3} ", tail)
    end = start + len(heading) + (next_heading.start() if next_heading else len(tail))
    return text[start:end]


class IssueOwnedPromptHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = normalized(DOCS / "prompt-contracts.md")
        cls.evidence = normalized(DOCS / "evidence-lifecycle.md")
        cls.prompts = normalized(DOCS / "prompts.md")
        cls.codex = normalized(DOCS / "tool-adapters" / "codex.md")
        cls.claude = normalized(DOCS / "tool-adapters" / "claude.md")
        cls.chatgpt = normalized(DOCS / "tool-adapters" / "chatgpt.md")
        cls.adapter_profiles = (
            markdown_section(
                DOCS / "tool-adapters" / "codex.md",
                "### Issue-Owned Durable Prompt Retrieval",
            ),
            markdown_section(
                DOCS / "tool-adapters" / "claude.md",
                "### Issue-Owned Durable Prompt Retrieval",
            ),
            markdown_section(
                DOCS / "tool-adapters" / "chatgpt.md",
                "### Issue-Owned Durable Prompt Capture And Handoff",
            ),
        )
        cls.delivery_envelope = markdown_section(
            DOCS / "prompts.md",
            "## Issue-Owned Durable Prompt Delivery Envelope Add-On",
        )
        cls.presentation = markdown_section(
            DOCS / "prompts.md",
            "## Cross-Executor Prompt Presentation",
        )
        cls.chatgpt_presentation = markdown_section(
            DOCS / "tool-adapters" / "chatgpt.md",
            "### Recipient-Capability Prompt Presentation",
        )

    def test_prompt_contract_is_the_profile_owner(self):
        heading = "## Issue-Owned Durable Rendered-Prompt Handoff Profile"
        self.assertIn(heading, self.contract)
        self.assertNotIn(heading, self.evidence)
        self.assertIn(
            "prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile",
            self.evidence,
        )
        for projection in (self.prompts, self.codex, self.claude, self.chatgpt):
            self.assertIn(
                "prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile",
                projection.lower(),
            )

    def test_admission_and_capture_are_exact_and_fail_closed(self):
        for phrase in (
            "all six conditions are affirmative",
            "Routine prompts remain non-durable by default",
            "Redaction produces a different rendered-prompt identity",
            "one immutable issue-owned destination",
            "absent-create semantics",
            "no overwrite",
            "no autorename",
            "UTF-8 without a byte-order mark",
            "LF line endings",
            "explicit final-newline rule",
            "Immediately retrieve the raw stored bytes",
            "Provider content hashes stay distinct from whole-file SHA-256",
        ):
            self.assertIn(phrase, self.contract)

    def test_model_a_delivery_and_evidence_boundaries(self):
        for phrase in (
            "There is no separate durable exchange, handoff, inbox, registry, or transport root",
            "one private OS-managed executor-owned attempt-local retrieval",
            "Copy/paste is not an exact-byte route",
            "Fallback changes delivery only",
            "the durable rendered prompt",
            "the delivery operation",
            "executor acknowledgement",
            "executor attempt",
            "attempt receipt",
            "executor output",
            "human disposition",
            "PRESERVED",
            "UNKNOWN",
        ):
            self.assertIn(phrase, self.contract)

    def test_delivery_envelope_is_external_to_rendered_prompt_identity(self):
        self.assertIn(
            "## Issue-Owned Durable Prompt Delivery Envelope Add-On",
            self.prompts,
        )
        self.assertNotIn(
            "## Issue-Owned Durable Prompt Handoff Add-On",
            self.prompts,
        )
        for phrase in (
            "This envelope is not part of the referenced rendered-prompt bytes or rendered-prompt digest",
            "add-on to the delivery packet",
            "derive final size, SHA-256, provider identity evidence, and delivery route only after the rendered prompt is frozen",
            "never embed a placeholder self-digest",
        ):
            self.assertIn(phrase, " ".join(self.delivery_envelope.split()))

        for phrase in (
            "Freeze the exact rendered-prompt bytes before deriving their final size",
            "The envelope is not part of the referenced rendered-prompt bytes or rendered-prompt digest",
            "Do not embed a placeholder digest",
            "A copied, reformatted, or otherwise changed prompt is not byte-identical",
        ):
            self.assertIn(phrase, self.contract)

    def test_claude_retrieval_verification_does_not_narrow_execution(self):
        for phrase in (
            "Retrieval and byte verification require only the minimum read capability",
            "After prompt acceptance, choose Claude's tools and permission mode from the bounded task's authorized execution requirements",
            "Read-only tools are mandatory only when",
            "Disable session persistence only when",
            "Prompt handoff alone does not prohibit write tools, tests, repository mutation, output creation, or session persistence",
        ):
            self.assertIn(phrase, self.claude)

        retrieval_section = self.adapter_profiles[1]
        self.assertNotIn("disable session persistence; grant only", retrieval_section)
        self.assertNotIn("grant only the narrow read-only tools", retrieval_section)

    def test_provider_revision_evidence_is_capability_conditional(self):
        for phrase in (
            "Record provider revision when the owning provider exposes it",
            "record explicitly that revision evidence is unavailable",
            "never fabricate a revision",
        ):
            self.assertIn(phrase, self.contract)
        self.assertIn("provider revision when exposed", self.chatgpt)
        self.assertIn("record that unavailability explicitly", self.chatgpt)
        self.assertNotIn(
            "provider identity, provider revision, provider content hash when available",
            self.contract,
        )
        self.assertNotIn(
            "object identity, revision, size, SHA-256",
            self.prompts,
        )

    def test_producing_receipt_and_state_predicates_are_distinct(self):
        self.assertIn("exactly one distinct producing receipt", self.contract)
        self.assertIn("It is not the rendered prompt, delivery evidence", self.contract)
        for state in (
            "`PRESERVED`",
            "`DELIVERED`",
            "`ACCEPTED`",
            "`STARTED`",
            "`COMPLETED`",
            "`FAILED`",
            "`UNKNOWN`",
        ):
            self.assertIn(state, self.contract)
        for boundary in (
            "prior ambiguous absent-create was reconciled exact",
            "One delivery operation identifies the exact rendered prompt, selected route, intended target, and observed delivery result",
            "A bounded failure class, attempt or delivery identity, and last verified state are recorded",
            "delivery alone is insufficient",
            "acknowledgement alone is insufficient",
            "does not imply correctness, human acceptance, merge, release, or adoption",
            "no later state is inferred",
        ):
            self.assertIn(boundary, self.contract)
        self.assertNotIn(
            "The smallest sufficient coordination evidence may report `PRESERVED`",
            self.contract,
        )

    def test_recovery_cleanup_and_authority_remain_bounded(self):
        for phrase in (
            "freshly retrieves current repository, provider, planning, and authority",
            "Historical prompt bytes and receipts remain historical evidence",
            "This profile creates no durable transport object to clean",
            "Remove only the private attempt-local retrieval",
            "Never delete or rewrite the durable prompt as transport cleanup",
            "transfer zero authority",
        ):
            self.assertIn(phrase, self.contract)

    def test_adapters_project_actual_route_without_provider_configuration(self):
        self.assertIn(
            "Do not use a locally synchronized provider mount as provider identity",
            self.codex,
        )
        self.assertIn("controller-bound digest evidence plus exact read evidence", self.claude)
        self.assertIn("Extracted text alone is not exact-byte readback", self.chatgpt)
        for adapter in self.adapter_profiles:
            self.assertIn("provider", adapter.lower())
            self.assertIn("concrete provider", adapter.lower())
            self.assertNotRegex(adapter, re.compile(r"\b\d{8,}\b"))
            self.assertNotRegex(
                adapter,
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            )

        for reusable_section in (self.delivery_envelope, *self.adapter_profiles):
            self.assertNotRegex(reusable_section, re.compile(r"ns:\d+//"))
            self.assertNotRegex(reusable_section, re.compile(r"\bid:[A-Za-z0-9_-]+"))
            self.assertNotRegex(
                reusable_section,
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            )

    def test_chatgpt_creation_fails_closed_on_collision(self):
        for phrase in ("Overwrite", "autorename", "destination collision", "fails closed"):
            self.assertIn(phrase, self.chatgpt)

    def test_qualified_machine_recipient_uses_file_first_presentation(self):
        presentation = " ".join(self.presentation.split())
        route = presentation.index("qualified Dropbox retrieval route")
        file = presentation.index("Dropbox-backed file")
        handoff = presentation.index("target-shaped retrieval handoff")
        self.assertLess(route, file)
        self.assertLess(file, handoff)

    def test_preview_does_not_gate_machine_handoff(self):
        presentation = " ".join(self.presentation.split())
        chatgpt_presentation = " ".join(self.chatgpt_presentation.split())
        self.assertIn("does not block the handoff or require prompt approval", presentation)
        self.assertNotIn("explicit approval", presentation)
        self.assertIn("Do not wait for prompt approval", chatgpt_presentation)

    def test_human_or_unqualified_recipient_uses_inline_presentation(self):
        presentation = " ".join(self.presentation.split())
        self.assertIn("For a human recipient", presentation)
        self.assertIn("no qualified Dropbox route", presentation)
        self.assertIn("present the complete prompt inline", presentation)
        self.assertIn("consecutive copyable code blocks", self.chatgpt)

    def test_material_governance_layers_without_capturing_routine_prompts(self):
        presentation = " ".join(self.presentation.split())
        self.assertIn("issue-owned durable rendered-prompt handoff profile", presentation)
        self.assertIn("A routine prompt delivered through a file does not", presentation)
        self.assertIn("use inline presentation rather than inventing a storage surface", presentation)
        self.assertIn("two-block inline presentation", self.chatgpt_presentation)


if __name__ == "__main__":
    unittest.main()
