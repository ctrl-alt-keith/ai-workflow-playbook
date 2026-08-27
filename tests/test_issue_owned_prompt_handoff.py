from pathlib import Path
import json
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
        cls.anchor = json.loads(
            (DOCS / "prompt-contract-semantic-anchors-v2.json").read_text(
                encoding="utf-8"
            )
        )
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
            "## Material Cross-Executor Prompt Presentation",
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

    def test_material_prompt_presentation_order_is_mechanically_explicit(self):
        order = (
            "render -> admit -> absent-create -> raw verify -> operator preview -> "
            "explicit approval -> fresh delivery route -> thin bootstrap -> "
            "executor exact verification -> execution"
        )
        self.assertIn(order, " ".join(self.presentation.split()))
        for phrase in (
            "Raw provider readback and exact identity verification must finish before the preview",
            "preview route and the executor-delivery route are distinct operations",
            "executor route is not minted until explicit approval",
        ):
            self.assertIn(phrase, " ".join(self.presentation.split()))

    def test_preview_is_convenience_not_evidence_approval_or_state(self):
        for phrase in (
            "human-readable convenience surface",
            "not raw-byte verification",
            "does not prove size, SHA-256, provider content hash, revision, or equality",
            "does not imply approval",
            "is not delivery, acknowledgement, execution start, or attempt completion",
            "creates no coordination state",
            "transfers zero authority",
        ):
            self.assertIn(phrase, " ".join(self.presentation.split()))

    def test_preview_revision_and_delivery_retry_preserve_identities(self):
        presentation = " ".join(self.presentation.split())
        for phrase in (
            "previewed version immutable and unsent",
            "rejected v1 is followed by approved v2",
            "bootstrap names only v2",
            "Never overwrite or silently reuse v1",
            "new delivery operation for the same durable prompt, not a new prompt version",
            "mutable `latest`, `current`, or `final` locator",
        ):
            self.assertIn(phrase, presentation)

    def test_default_omits_prompt_body_but_routine_and_fallback_stay_inline(self):
        presentation = " ".join(self.presentation.split())
        for phrase in (
            "Do not print the full executable prompt inline by default",
            "thin target-shaped bootstrap that omits the full prompt body",
            "Routine short prompts, brainstorming, incomplete fragments, and ordinary same-thread deltas remain lightweight and inline",
            "complete inline presentation only when the prompt is safe to display",
            "keep operator metadata outside that executable prompt",
            "stop before provider creation when admission has not passed",
        ):
            self.assertIn(phrase, presentation)

    def test_chatgpt_examples_cover_default_revision_retry_and_fallback(self):
        for phrase in (
            "Material ChatGPT to Codex prompt",
            "Rejected v1 remains immutable and unsent",
            "before any executor URL exists",
            "replacement for the same durable file",
            "Preview or raw readback unavailable",
            "Routine or same-thread prompt",
            "Stop before Dropbox creation",
            "Claude or another executor",
        ):
            self.assertIn(phrase, self.chatgpt)

    def test_chatgpt_preview_link_effect_is_bounded_and_product_dependent(self):
        for phrase in (
            "always generates a private shared link",
            "provider-side preview effect",
            "not universal Dropbox behavior",
            "effective audience",
            "view or edit access",
            "download setting",
            "persistence or reuse behavior",
            "preview changed file bytes or revision",
            "`audience=no_one`, view access, and downloads permitted",
            "product-dependent runtime evidence to revalidate",
        ):
            self.assertIn(phrase, self.chatgpt)

    def test_approval_and_thin_bootstrap_remain_separate_identities(self):
        for phrase in (
            "Only after approval",
            "without the full prompt body",
            "approved durable path",
            "file ID",
            "whole-file SHA-256",
            "Dropbox content hash",
            "preview operation, human approval, delivery operation",
            "executor acknowledgement, attempt, receipt, output, and human disposition",
        ):
            self.assertIn(phrase, self.chatgpt)

    def test_codex_single_use_retrieval_verifies_before_interpretation(self):
        for phrase in (
            "Perform exactly one intended `GET`",
            "do not send `HEAD`, range probes, previews, unfurlers, scanners",
            "Before reading or executing the prompt",
            "expected byte size and whole-file SHA-256",
            "UTF-8, no BOM, LF-only line endings",
            "Verify the Dropbox content hash when",
            "Fail closed before prompt interpretation",
            "Never reconstruct the payload",
            "replacement URL is a new delivery operation for the same durable prompt",
        ):
            self.assertIn(phrase, self.codex)

    def test_provider_action_contracts_are_not_universal_guarantees(self):
        for adapter in (self.chatgpt, self.codex):
            self.assertIn("60 through 900 seconds", adapter)
            self.assertIn("first HTTP request of any method", adapter)
            self.assertIn("not a universal Dropbox", adapter)

    def test_presentation_does_not_take_cak_168_or_semantic_anchor_ownership(self):
        presentation = " ".join(self.presentation.split())
        for cak_168_term in (
            "current receiving surface",
            "first downstream deliverable",
        ):
            self.assertNotIn(cak_168_term, presentation.lower())
        self.assertNotIn(
            "## Material Cross-Executor Prompt Presentation",
            self.contract,
        )
        self.assertNotIn("operator_preview", self.anchor)
        self.assertNotIn("operator_approval", self.anchor)


if __name__ == "__main__":
    unittest.main()
