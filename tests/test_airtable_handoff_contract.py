from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "docs" / "prompts.md"


def markdown_section(text: str, heading: str) -> str:
    start = text.index(heading)
    level = len(heading) - len(heading.lstrip("#"))
    following = text[start + len(heading) :]
    match = re.search(rf"(?m)^#{{1,{level}}} ", following)
    end = len(text) if match is None else start + len(heading) + match.start()
    return text[start:end]


class AirtableHandoffContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prompts = PROMPTS.read_text(encoding="utf-8")
        cls.delivery = markdown_section(
            cls.prompts,
            "## Prompt Delivery Decision Model",
        )
        cls.airtable = markdown_section(
            cls.prompts,
            "### Airtable canonical-text handoff",
        )
        cls.delivery_text = " ".join(cls.delivery.split())
        cls.airtable_text = " ".join(cls.airtable.split())

    def test_single_canonical_inline_limit_and_structural_routing(self) -> None:
        matches = []
        for path in (ROOT / "docs").rglob("*.md"):
            for value in re.findall(
                r"inline_prompt_transport_byte_limit\s*=\s*(\d+)",
                path.read_text(encoding="utf-8"),
            ):
                matches.append((path.relative_to(ROOT).as_posix(), int(value)))
        self.assertEqual(matches, [("docs/prompts.md", 4096)])
        self.assertRegex(
            self.delivery_text,
            r"structurally safe representation.*below it when structure "
            r"cannot be preserved safely.*Airtable route",
        )

    def test_shared_contract_owns_connector_and_producer_integrity(self) -> None:
        self.assertRegex(
            self.airtable_text,
            r"semantic connector before probing.*CLI, manual, or raw-API "
            r"fallback.*absence, unsupported capability, or failure.*account "
            r"and connection identity.*intended base",
        )
        self.assertRegex(
            self.airtable_text,
            r"derive byte length and SHA-256.*retrieve the exact returned "
            r"record.*recompute identity from its `Payload`.*stored metadata "
            r"cannot prove itself.*Mismatch blocks delivery",
        )

    def test_terminal_lf_mismatch_fails_producer_readback(self) -> None:
        self.assertRegex(
            self.airtable_text,
            r"final-newline state.*returned payload.*Mismatch blocks delivery",
        )
        for returned_size, frozen_size in ((5770, 5771), (13012, 13013)):
            with self.subTest(returned_size=returned_size, frozen_size=frozen_size):
                returned = b"x" * returned_size
                frozen = returned + b"\n"
                self.assertEqual(
                    (len(returned), len(frozen)),
                    (returned_size, frozen_size),
                )
                self.assertNotEqual(
                    hashlib.sha256(returned).digest(),
                    hashlib.sha256(frozen).digest(),
                )


if __name__ == "__main__":
    unittest.main()
