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
        cls.complete_prompt_shape = markdown_section(
            DOCS / "prompts.md",
            "## Complete Prompt Shape",
        )
        cls.presentation = markdown_section(
            DOCS / "prompts.md",
            "## Cross-Executor Prompt Presentation",
        )
        cls.chatgpt_prompt_presentation = markdown_section(
            DOCS / "tool-adapters" / "chatgpt.md",
            "### Prompt presentation",
        )
        cls.chatgpt_presentation = markdown_section(
            DOCS / "tool-adapters" / "chatgpt.md",
            "### Recipient-Capability Prompt Presentation",
        )
        cls.chatgpt_dropbox_bootstrap = markdown_section(
            DOCS / "tool-adapters" / "chatgpt.md",
            "### Dropbox Widget Preview And Compact Executor Bootstrap",
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
        self.assertIn(
            "For any complete prompt, select presentation by the recipient's "
            "currently qualified capability, independently of prompt materiality",
            presentation,
        )
        route = presentation.index("qualified Dropbox retrieval route")
        file = presentation.index("Dropbox-backed file")
        handoff = presentation.index("target-shaped retrieval handoff")
        self.assertLess(route, file)
        self.assertLess(file, handoff)

    def test_two_block_format_is_conditional_on_inline_presentation(self):
        complete_shape = " ".join(self.complete_prompt_shape.split())
        chatgpt_prompt = " ".join(self.chatgpt_prompt_presentation.split())
        self.assertIn(
            "When inline presentation is selected for a complete generated prompt",
            complete_shape,
        )
        self.assertIn(
            "When the shared recipient-capability selector chooses inline "
            "presentation for a complete, copy-ready prompt or downstream handoff",
            chatgpt_prompt,
        )

    def test_preview_does_not_gate_machine_handoff(self):
        presentation = " ".join(self.presentation.split())
        chatgpt_presentation = " ".join(self.chatgpt_presentation.split())
        self.assertIn("does not block the handoff or require prompt approval", presentation)
        for gate_phrase in ("Approve", "Revise", "Reject", "explicit approval", "before sending"):
            self.assertNotIn(gate_phrase, presentation)
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

    def test_chatgpt_write_metadata_does_not_claim_a_visible_preview(self):
        preview = " ".join(self.chatgpt_dropbox_bootstrap.split())
        self.assertIn(
            "A successful `create_file` result is write-produced file metadata, "
            "not evidence that an operator-visible preview rendered",
            preview,
        )
        self.assertIn(
            "Connector success or returned preview metadata does not prove that "
            "the active ChatGPT client displayed the widget",
            preview,
        )
        self.assertIn("Claim visible rendering only when the active client visibly rendered it", preview)
        self.assertIn("do not call the preview successful", preview)

    def test_chatgpt_file_preview_uses_qualified_locator_precedence(self):
        preview = " ".join(self.chatgpt_dropbox_bootstrap.split())
        self.assertIn("Invoke Dropbox `file_preview` with `file_paths`", preview)
        file_id = preview.index("exact returned Dropbox `file_id` first")
        namespace = preview.index("exact returned namespace path only when `file_id` is unavailable")
        display = preview.index("human display path only when neither qualified identifier is available")
        self.assertLess(file_id, namespace)
        self.assertLess(namespace, display)
        self.assertIn("Never truncate or convert a namespace path", preview)
        self.assertIn("stripping its `ns:[id]//` prefix", preview)

    def test_chatgpt_preview_widget_precedes_single_use_download_link(self):
        preview = self.chatgpt_dropbox_bootstrap
        create = preview.index("1. Create the file.")
        verify = preview.index("2. Exact-verify the durable object")
        widget = preview.index("3. Invoke Dropbox `file_preview`")
        render = preview.index("4. Let the tool result render as the file surface.")
        download = preview.index("5. Mint the fresh single-use raw-download URL")
        bootstrap = preview.index("6. Emit the compact executor bootstrap.")
        self.assertEqual(sorted((create, verify, widget, render, download, bootstrap)), [
            create,
            verify,
            widget,
            render,
            download,
            bootstrap,
        ])
        normalized_preview = " ".join(preview.split())
        self.assertIn("Preview uses the durable file identity", normalized_preview)
        self.assertIn("never the executor's single-use raw-download URL", normalized_preview)

    def test_chatgpt_uses_the_tool_widget_without_manual_link_substitution(self):
        preview = " ".join(self.chatgpt_dropbox_bootstrap.split())
        self.assertIn("Use the tool-produced preview widget itself as the preview surface", preview)
        for substitute in (
            "`open_in_dropbox_url`",
            "`copy_link_url`",
            "`thumbnail_url`",
            'an "Open in Dropbox" substitute',
        ):
            self.assertIn(substitute, preview)
        self.assertIn("Do not replace or narrate it", preview)

    def test_chatgpt_preview_remains_optional_and_non_blocking(self):
        preview = " ".join(self.chatgpt_dropbox_bootstrap.split())
        self.assertIn(
            "Preview remains optional, non-authorizing, non-verifying, and non-gating",
            preview,
        )
        self.assertIn("does not block the machine-recipient handoff", preview)
        for gate_phrase in ("Approve", "Revise", "Reject preview", "before sending"):
            self.assertNotIn(gate_phrase, preview)

    def test_chatgpt_bootstrap_is_one_allowlisted_eight_line_code_block(self):
        section = self.chatgpt_dropbox_bootstrap
        blocks = re.findall(r"```[^\n]*\n(.*?)\n```", section, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        lines = [line for line in blocks[0].splitlines() if line.strip()]
        self.assertLessEqual(len(lines), 8)
        self.assertEqual(
            [line.split(":", 1)[0] for line in lines],
            [
                "Download",
                "Dropbox ID",
                "Prompt",
                "Expected bytes",
                "Expected SHA-256",
                "Execute",
                "Stop",
            ],
        )
        self.assertNotRegex(blocks[0], re.compile(r"\]\(https?://"))
        for forbidden_heading in (
            "Role:",
            "Goal:",
            "Context:",
            "Tasks:",
            "Constraints:",
            "Validation:",
            "Delivery:",
        ):
            self.assertNotIn(forbidden_heading, blocks[0])

    def test_chatgpt_bootstrap_rejects_prompt_restatement_and_url_unfurling(self):
        bootstrap = " ".join(self.chatgpt_dropbox_bootstrap.split())
        self.assertIn("Selecting the Dropbox-backed prompt route is a conversation-minimization boundary", bootstrap)
        self.assertIn("The complete prompt remains in Dropbox", bootstrap)
        self.assertIn("The bootstrap is not a task summary", bootstrap)
        self.assertIn("exceeds the field allowlist or line ceiling", bootstrap)
        for forbidden_heading in (
            "`Role:`",
            "`Goal:`",
            "`Context:`",
            "`Tasks:`",
            "`Constraints:`",
            "`Validation:`",
            "`Delivery:`",
        ):
            self.assertIn(forbidden_heading, bootstrap)
        self.assertIn("a wall-of-text bootstrap is noncompliant", bootstrap)
        self.assertIn("literal text inside the code block", bootstrap)
        self.assertIn("do not intentionally unfurl, preview, scan, or preflight it", bootstrap)


if __name__ == "__main__":
    unittest.main()
