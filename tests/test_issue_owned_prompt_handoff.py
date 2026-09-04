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
        cls.profile_heading = "## Issue-Owned Durable Rendered-Prompt Handoff Profile"
        cls.profile_link = (
            "prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile"
        )
        cls.airtable_heading = "### Airtable canonical-text handoff"
        cls.airtable_link = "prompts.md#airtable-canonical-text-handoff"
        cls.airtable_contract = markdown_section(
            DOCS / "prompts.md", cls.airtable_heading
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

    def test_shared_rules_and_material_profile_each_have_one_owner(self):
        markdown = {
            path: path.read_text(encoding="utf-8") for path in DOCS.rglob("*.md")
        }
        profile_owners = [
            path.relative_to(DOCS).as_posix()
            for path, contents in markdown.items()
            if self.profile_heading in contents
        ]
        airtable_owners = [
            path.relative_to(DOCS).as_posix()
            for path, contents in markdown.items()
            if self.airtable_heading in contents
        ]
        self.assertEqual(profile_owners, ["prompt-contracts.md"])
        self.assertEqual(airtable_owners, ["prompts.md"])

        for relative_path in (
            "evidence-lifecycle.md",
            "prompts.md",
            "tool-adapters/codex.md",
            "tool-adapters/claude.md",
            "tool-adapters/chatgpt.md",
        ):
            contents = markdown[DOCS / relative_path].lower()
            self.assertIn(self.profile_link, contents, relative_path)

        for relative_path in (
            "tool-adapters/codex.md",
            "tool-adapters/claude.md",
            "tool-adapters/chatgpt.md",
        ):
            contents = markdown[DOCS / relative_path].lower()
            self.assertIn(self.airtable_link, contents, relative_path)

    def test_shared_contract_has_exact_fields_and_attempt_rules(self):
        fields = (
            "`Handoff Key`",
            "`Payload`",
            "`Payload Bytes`",
            "`SHA-256`",
            "`Producer`",
        )
        field_block = self.airtable_contract[
            self.airtable_contract.index("required fields:") :
            self.airtable_contract.index("Freeze `Payload`")
        ]
        for field in fields:
            self.assertEqual(field_block.count(field), 1, field)

        for requirement in (
            "one new Airtable record per producer attempt",
            "never update it",
            "correction creates a new key and record",
            "retrieves by exact record ID",
            "recomputes byte length and SHA-256",
            "fails closed",
        ):
            self.assertIn(requirement.lower(), self.airtable_contract.lower())

    def test_reusable_projections_do_not_embed_provider_configuration(self):
        delivery_envelope = markdown_section(
            DOCS / "prompts.md",
            "## Issue-Owned Durable Prompt Delivery Envelope Add-On",
        )
        for section in (
            self.airtable_contract,
            delivery_envelope,
            *self.adapter_profiles,
        ):
            self.assertNotRegex(section, re.compile(r"ns:\d+//"))
            self.assertNotRegex(section, re.compile(r"\bapp[A-Za-z0-9]{10,}\b"))
            self.assertNotRegex(section, re.compile(r"\btbl[A-Za-z0-9]{10,}\b"))
            self.assertNotRegex(
                section,
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            )

    def test_prompt_handoff_drops_file_delivery_ceremony(self):
        combined = "\n".join(
            (
                self.airtable_contract,
                markdown_section(
                    DOCS / "prompts.md",
                    "## Issue-Owned Durable Prompt Delivery Envelope Add-On",
                ),
                *self.adapter_profiles,
            )
        ).lower()
        for obsolete in (
            "download link",
            "attempt-local",
            "prompt preview",
            "provider file id",
            "transport-only latch",
        ):
            self.assertNotIn(obsolete, combined)


if __name__ == "__main__":
    unittest.main()
