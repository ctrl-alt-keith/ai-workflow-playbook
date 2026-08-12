from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class ChatGPTAdapterTests(unittest.TestCase):
    def test_start_here_activates_chatgpt_work_and_rechecks_sources(self):
        contents = (DOCS / "start-here.md").read_text(encoding="utf-8")

        self.assertIn("ChatGPT/Work runs must read", contents)
        self.assertIn("docs/tool-adapters/chatgpt.md", contents)
        self.assertIn("Repository operating-mode persistence does not freeze", contents)
        self.assertIn("re-evaluate activation routing", contents)
        self.assertIn("Reuse still-current verified sources", contents)

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
