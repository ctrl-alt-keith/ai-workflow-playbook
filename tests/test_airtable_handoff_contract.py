from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AirtableHandoffContractTests(unittest.TestCase):
    def test_single_canonical_inline_transport_limit(self) -> None:
        matches = []
        for path in (ROOT / "docs").rglob("*.md"):
            for value in re.findall(
                r"inline_prompt_transport_byte_limit\s*=\s*(\d+)",
                path.read_text(encoding="utf-8"),
            ):
                matches.append((path.relative_to(ROOT).as_posix(), int(value)))
        self.assertEqual(matches, [("docs/prompts.md", 4096)])
