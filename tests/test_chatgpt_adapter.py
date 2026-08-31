from pathlib import Path
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
            "blocked before a qualified prompt handoff is complete",
            "re-run the recipient-capability selector against the observed state",
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

    def test_copy_ready_prompt_breadcrumb_stays_outside_both_code_blocks(self):
        contents = (DOCS / "tool-adapters/chatgpt.md").read_text(encoding="utf-8")
        normalized = " ".join(contents.split())

        self.assertIn("complete, copy-ready prompt or downstream handoff", contents)
        self.assertIn("with no intervening prose", normalized)
        self.assertIn(
            "`ChatGPT thread: [exact canonical title]`",
            contents,
        )
        self.assertIn("outside both code blocks", contents)
        self.assertIn(
            "not task authority, execution identity, durable continuity, source evidence",
            normalized,
        )
        self.assertIn("or part of the downstream executable prompt", normalized)
        self.assertIn(
            "quoted prompts, source excerpts, incomplete fragments, or conceptual discussion",
            normalized,
        )
        self.assertIn("reuse that exact title in later complete prompts", normalized)
        self.assertIn("not verified or changed ChatGPT UI state", normalized)
        self.assertIn("downstream target executor adapter explicitly supports", normalized)
        self.assertIn("ChatGPT-targeted prompts resolve the shared naming placeholder to nothing", normalized)
        self.assertIn("does not ask ChatGPT to rename itself or report a naming limitation", normalized)
        self.assertNotIn("currently, that means an applicable Codex-targeted handoff", contents)
        self.assertIn("normal `SAME THREAD` or `CHILD TASK`", normalized)
