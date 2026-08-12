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
