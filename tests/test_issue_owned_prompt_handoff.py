from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


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
        cls.owner_heading = "## Issue-Owned Durable Rendered-Prompt Handoff Profile"
        cls.owner_link = (
            "prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile"
        )
        cls.adapter_profiles = tuple(
            markdown_section(DOCS / relative_path, heading)
            for relative_path, heading in (
                (
                    "tool-adapters/codex.md",
                    "### Issue-Owned Durable Prompt Retrieval",
                ),
                (
                    "tool-adapters/claude.md",
                    "### Issue-Owned Durable Prompt Retrieval",
                ),
                (
                    "tool-adapters/chatgpt.md",
                    "### Issue-Owned Durable Prompt Capture And Handoff",
                ),
            )
        )
        cls.bootstrap = markdown_section(
            DOCS / "tool-adapters/chatgpt.md",
            "### Dropbox Preview And Minimal Executor Handoff",
        )

    def test_prompt_contract_is_the_unique_profile_owner(self):
        owners = []
        for path in DOCS.rglob("*.md"):
            if self.owner_heading in path.read_text(encoding="utf-8"):
                owners.append(path.relative_to(DOCS).as_posix())
        self.assertEqual(owners, ["prompt-contracts.md"])

        for relative_path in (
            "evidence-lifecycle.md",
            "prompts.md",
            "tool-adapters/codex.md",
            "tool-adapters/claude.md",
            "tool-adapters/chatgpt.md",
        ):
            contents = (DOCS / relative_path).read_text(encoding="utf-8").lower()
            self.assertIn(self.owner_link, contents, relative_path)

    def test_reusable_projections_do_not_embed_provider_configuration(self):
        delivery_envelope = markdown_section(
            DOCS / "prompts.md",
            "## Issue-Owned Durable Prompt Delivery Envelope Add-On",
        )
        for section in (delivery_envelope, *self.adapter_profiles):
            self.assertNotRegex(section, re.compile(r"ns:\d+//"))
            self.assertNotRegex(section, re.compile(r"\bid:[A-Za-z0-9_-]+"))
            self.assertNotRegex(
                section,
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            )

    def test_chatgpt_handoff_has_one_bounded_bootstrap(self):
        block_start = self.bootstrap.index("```text")
        metadata = self.bootstrap[:block_start]
        blocks = re.findall(r"```[^\n]*\n(.*?)\n```", self.bootstrap, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        executable = blocks[0]

        for field in (
            "Thread routing:",
            "Recommended model:",
            "Recommended reasoning level:",
            "Reason:",
        ):
            self.assertIn(field, metadata)
            self.assertNotIn(field, executable)

        fields = dict(
            line.split(":", 1)
            for line in executable.splitlines()
            if ":" in line
        )
        self.assertLessEqual(len([line for line in executable.splitlines() if line]), 8)
        self.assertTrue(
            {"Download", "Attempt directory basename", "Local filename", "Execute"}
            <= fields.keys()
        )
        for key in ("Attempt directory basename", "Local filename"):
            self.assertRegex(fields[key].strip(), re.compile(r"\A[A-Za-z0-9._-]+\Z"))


if __name__ == "__main__":
    unittest.main()
