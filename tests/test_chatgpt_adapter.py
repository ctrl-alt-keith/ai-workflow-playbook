from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class ChatGPTAdapterTests(unittest.TestCase):
    def test_start_here_activates_chatgpt_and_rechecks_sources(self):
        contents = (DOCS / "start-here.md").read_text(encoding="utf-8")
        normalized_start_here = " ".join(contents.split())

        self.assertIn(
            "repository-scoped ChatGPT runs must read", normalized_start_here
        )
        self.assertIn("docs/tool-adapters/chatgpt.md", contents)
        self.assertNotIn("ChatGPT/Work runs must read", contents)
        self.assertIn("Repository operating-mode persistence does not freeze", contents)
        self.assertIn("re-evaluate activation routing", normalized_start_here)
        self.assertIn(
            "Reuse the still-current repository floor and owners",
            normalized_start_here,
        )

    def test_start_here_reroutes_material_task_shape_without_blanket_rehydration(
        self,
    ):
        contents = (DOCS / "start-here.md").read_text(encoding="utf-8")
        chatgpt = (DOCS / "tool-adapters" / "chatgpt.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(contents.split())
        normalized_chatgpt = " ".join(chatgpt.split())

        for phrase in (
            "task-specific activated source set",
            "re-evaluate activation routing",
            "compare the changed task's required-source set with the currently activated set",
            "retrieve only newly required owners",
            "Reuse the still-current repository floor and owners",
            "do not blanket-rehydrate ordinary follow-ups",
            "target executor",
            "fail closed for the affected conclusion or artifact",
            "memory, summaries, and convenient examples are not substitutes",
            "Activation and application are separate stages",
            "Successfully retrieving an owner does not prove its contract was applied",
            "preserve the owner's failure, fallback, or presentation contract",
            "rather than degrading into unconstrained prose",
        ):
            self.assertIn(phrase, normalized)

        for incident_text in (
            "CAK-194",
            "CAK-195",
            "Let's begin CAK-194",
            "give me an example codex prompt to show the formatting you'd use",
        ):
            self.assertNotIn(incident_text, contents)

        for phrase in (
            "`prompt me`, `show me the Codex handoff`, and `give me the prompt`",
            "upstream semantic evidence rather than a transport selector",
            "frozen stage 5 record identifies a selected qualified Dropbox or file route",
            "classifies a new failure against that same route class and exact destination identity",
            "canonical decision model's bounded capability re-evaluation rule",
            "known non-disqualifying limitation is retained as diagnostic evidence",
            "Sequence the owned failure classification, the single downstream-only re-evaluation",
            "Record there that bounded re-evaluation was consumed",
            "exact identity differs from the failed route",
            "retain the old failure as prior evidence",
            "Reasserting the same failed identity cannot force another file-backed attempt",
            "stop blocked with that new reason",
            "superseded pre-re-evaluation record cannot restart the bound",
            "preserve the two-block complete-prompt shape",
            "Do not degrade the required prompt or handoff into unconstrained status prose",
        ):
            self.assertIn(phrase, normalized_chatgpt)

    def test_adapter_projects_boundaries_to_canonical_owners(self):
        contents = (DOCS / "tool-adapters/chatgpt.md").read_text(encoding="utf-8")

        for heading in (
            "Repository-bootstrap boundary",
            "Project and conversation context",
            "Persistent-context activation",
            "Chat, Work, and execution locality",
            "Connected apps, approvals, and consequential actions",
            "Workspace Agents",
            "Prompt and downstream-context projection",
            "Generated artifacts",
            "Scheduled and unattended execution",
            "Recovery after activation drift",
            "Evidence and provider-reference boundary",
        ):
            self.assertIn(heading, contents)

        for owner in (
            "start-here.md",
            "core-model.md",
            "source-first-retrieval.md",
            "repo-readiness.md",
            "prompts.md",
            "prompt-contracts.md",
            "orchestration-and-parallelism.md",
            "maintenance-automations.md",
        ):
            self.assertIn(owner, contents)

        self.assertIn("not separate authority contracts", contents)
        self.assertIn(
            "does not expand the human-authorized task", " ".join(contents.split())
        )
        self.assertIn("not symptom-by-symptom repair", contents)

    def test_adapter_keeps_chat_and_work_under_chatgpt(self):
        chatgpt = (DOCS / "tool-adapters/chatgpt.md").read_text(encoding="utf-8")
        codex = (DOCS / "tool-adapters/codex.md").read_text(encoding="utf-8")
        normalized_chatgpt = " ".join(chatgpt.split())
        normalized_codex = " ".join(codex.split())

        self.assertTrue(chatgpt.startswith("# ChatGPT Adapter\n"))
        self.assertNotIn("# ChatGPT/Work Adapter", chatgpt)
        self.assertIn("nested task-shape or capability modes", normalized_chatgpt)
        self.assertIn("under that one ChatGPT adapter", normalized_chatgpt)
        self.assertIn(
            "not separate durable executor identities or adapters", normalized_chatgpt
        )
        self.assertIn("not separate authority contracts", normalized_chatgpt)
        self.assertIn(
            "does not depend on how a particular client packages that surface",
            normalized_codex,
        )

    def test_workspace_agents_projection_preserves_existing_owners(self):
        contents = (DOCS / "tool-adapters/chatgpt.md").read_text(encoding="utf-8")
        normalized = " ".join(contents.split())

        self.assertEqual(contents.count("## Workspace Agents"), 1)
        self.assertFalse((DOCS / "tool-adapters" / "workspace-agents.md").exists())

        for anchor in (
            "API/event and scheduled Workspace Agent runs may begin without an interactive",
            "durable bounded authority envelope",
            "not automatically authoritative source state for another system",
            "fail closed or return an explicit non-authorizing partial or",
            "invoker/end user, API caller/token principal, Workspace",
            "end-user connections or agent-owned/shared",
            "do not widen human task authority",
            "Draft/Preview is candidate or test state, not proof of a published operational",
            "material operational transition requiring applicable explicit authority",
            "does not make sources current, grant arbitrary downstream authority",
            "completed run does not replace post-write re-observation",
        ):
            self.assertIn(anchor, normalized)

        for owner in (
            "core-model.md",
            "source-first-retrieval.md",
            "maintenance-automations.md",
        ):
            self.assertIn(owner, contents)

    def test_inline_complete_prompt_renderer_owns_the_entire_response_surface(self):
        contents = (DOCS / "tool-adapters/chatgpt.md").read_text(encoding="utf-8")
        prompts = (DOCS / "prompts.md").read_text(encoding="utf-8")
        normalized = " ".join(contents.split())
        complete_prompt_shape = " ".join(
            prompts[
                prompts.index("## Complete Prompt Shape") : prompts.index(
                    "## Produced-Artifact Classification"
                )
            ].split()
        )

        self.assertIn("complete, copy-ready prompt or downstream handoff", contents)
        self.assertIn("with no intervening prose", normalized)
        self.assertIn("shared canonical renderer controls the entire response surface", normalized)
        self.assertIn("no assistant-authored material before, between, or after", normalized)
        self.assertIn("copy instruction, navigation breadcrumb, Markdown separator", normalized)
        self.assertIn("prose label, or line-continuation escaping artifact", normalized)
        self.assertNotIn("ChatGPT thread: [exact canonical title]", contents)

        for phrase in (
            "exactly two consecutive fenced code blocks",
            "Do not emit assistant-authored prose, headings, labels, separators, or postambles",
            "Markdown line-continuation backslashes or equivalent escaping artifacts",
        ):
            self.assertIn(phrase, complete_prompt_shape)

        def is_canonical_inline_response(rendered):
            match = re.fullmatch(
                r"```[^\n]*\n(?P<metadata>.*?)```\n```[^\n]*\n(?P<prompt>.*?)```\n?",
                rendered,
                flags=re.DOTALL,
            )
            if not match:
                return False
            if not match.group("metadata").startswith("Thread routing:"):
                return False
            if not match.group("prompt").startswith("Outcome:"):
                return False
            return not any(
                prohibited in rendered
                for prohibited in (
                    "Here’s the drop-in Codex handoff.",
                    "---",
                    "Copy the block as-is",
                    "Reason:\\",
                    "Outcome:\\",
                    "Regression coverage:\\",
                    "Final report:\\",
                )
            )

        canonical_rendering = (
            "```text\nThread routing: FRESH THREAD\nReason:\nFocused implementation.\n```\n"
            "```text\nOutcome:\nImplement the bounded change.\n```\n"
        )
        self.assertTrue(is_canonical_inline_response(canonical_rendering))

        for malformed_rendering in (
            "Here’s the drop-in Codex handoff.\n" + canonical_rendering,
            canonical_rendering.replace("\n```\n```text", "\n```\n---\n```text"),
            canonical_rendering + "Copy the block as-is into a fresh Codex thread.\n",
            canonical_rendering.replace("Reason:\n", "Reason:\\\n"),
            canonical_rendering.replace("Outcome:\n", "Outcome:\\\n"),
        ):
            self.assertFalse(is_canonical_inline_response(malformed_rendering))

    def test_chatgpt_projects_frozen_delivery_model_before_inline_rendering(self):
        contents = (DOCS / "tool-adapters/chatgpt.md").read_text(encoding="utf-8")
        prompt_presentation = " ".join(
            contents[contents.index("### Prompt presentation") :].split()
        )
        recipient_start = contents.index(
            "### Recipient-Capability Prompt Presentation"
        )
        recipient_end = contents.index(
            "### Dropbox Preview And Minimal Executor Handoff"
        )
        recipient_projection = " ".join(
            contents[recipient_start:recipient_end].split()
        )

        frozen = prompt_presentation.index(
            "Consume the frozen stage outputs from the shared"
        )
        no_reclassification = prompt_presentation.index(
            "must not reclassify the produced artifact"
        )
        presentation = prompt_presentation.index(
            "unless `presentation-selection` produced `inline`"
        )
        renderer = prompt_presentation.index(
            "`renderer-selection` produced `canonical-inline-two-block`"
        )
        inline = prompt_presentation.index(
            "present the shared operator-metadata block"
        )

        self.assertLess(frozen, no_reclassification)
        self.assertLess(no_reclassification, presentation)
        self.assertLess(presentation, renderer)
        self.assertLess(renderer, inline)
        self.assertIn(
            "[prompt delivery decision model](../prompts.md#prompt-delivery-decision-model)",
            prompt_presentation,
        )
        self.assertIn(
            "operator or viewer and the executable prompt's execution recipient as independent stage outputs",
            recipient_projection,
        )
        self.assertIn("before inspecting capability", recipient_projection)
        self.assertIn("does not replace a resolved Codex", recipient_projection)
        self.assertIn("`qualified-with-known-limitation`", recipient_projection)
        self.assertIn(
            "do not reinterpret it as route disqualification",
            recipient_projection,
        )
        self.assertIn(
            "executes the selected file-backed, inline, lightweight, or blocked action",
            prompt_presentation,
        )
        self.assertIn("it cannot select another renderer", prompt_presentation)

    def test_executable_examples_use_complete_prompt_presentation(self):
        prompts = (DOCS / "prompts.md").read_text(encoding="utf-8")
        codex = (DOCS / "tool-adapters" / "codex.md").read_text(encoding="utf-8")
        classification = " ".join(
            prompts[
                prompts.index("## Produced-Artifact Classification") : prompts.index(
                    "## Cross-Executor Prompt Presentation"
                )
            ].split()
        )

        for framing in (
            "`example`",
            "`sample`",
            "`roughly`",
            "`formatting`",
            "`preview`",
            "`demo`",
            "`show me the format`",
            "`sample prompt`",
            "`example implementation prompt`",
        ):
            self.assertIn(framing, classification)
        self.assertIn("complete or substantially executable", classification)
        self.assertIn(
            "must not be reinterpreted by recipient, capability, presentation, or renderer selection",
            classification,
        )
        self.assertIn("qualified capability", prompts)
        self.assertIn("Dropbox-backed file", prompts)
        self.assertIn("two-block shape", classification)
        self.assertIn("known-value placeholder", classification)
        self.assertIn("genuinely conceptual discussion", classification)
        self.assertIn("GPT-5.6 Luna | GPT-5.6 Terra | GPT-5.6 Sol", codex)
        self.assertNotIn("Recommended model: Codex", codex)

    def test_explicit_ready_to_run_request_cannot_be_downgraded_before_routing(
        self,
    ):
        prompts = (DOCS / "prompts.md").read_text(encoding="utf-8")
        chatgpt = (DOCS / "tool-adapters" / "chatgpt.md").read_text(
            encoding="utf-8"
        )
        classification = " ".join(
            prompts[
                prompts.index("## Produced-Artifact Classification") : prompts.index(
                    "## Cross-Executor Prompt Presentation"
                )
            ].split()
        )
        presentation = " ".join(
            prompts[
                prompts.index("## Cross-Executor Prompt Presentation") : prompts.index(
                    "## Quick Navigation"
                )
            ].split()
        )
        chatgpt_presentation = " ".join(
            chatgpt[chatgpt.index("### Prompt presentation") :].split()
        )

        cold_start_request = (
            "Show me the exact Codex handoff you would use for CAK-194, "
            "including the operator metadata and the complete executable prompt. "
            "Treat it as ready to run, not as a conceptual example."
        )
        self.assertIn("exact Codex handoff", cold_start_request)
        self.assertIn("complete executable prompt", cold_start_request)
        self.assertIn("ready to run", cold_start_request)

        for phrase in (
            "authoritative input to this classification",
            "exact, complete, executable, ready to run, final, ready to paste, "
            "ready to execute, or complete runnable",
            "do not weaken that classification with assistant-authored framing",
            "`illustrative`",
            "`sample-only`",
            "`conceptual`",
            "`provisional`",
            "`rough`",
            "`not finalized`",
            "stronger safety, authority, or capability constraint",
            "explicit blocked result",
            "do not silently downgrade the artifact",
        ):
            self.assertIn(phrase, classification)

        self.assertLess(
            classification.index("authoritative input to this classification"),
            classification.index("Classify the artifact actually produced"),
        )
        self.assertIn("qualified Dropbox retrieval route", presentation)
        self.assertIn("Dropbox-backed file", presentation)
        self.assertIn("without reproducing the complete prompt", presentation)
        self.assertIn("present the complete prompt inline", presentation)
        self.assertIn("consecutive copyable code blocks", chatgpt_presentation)
