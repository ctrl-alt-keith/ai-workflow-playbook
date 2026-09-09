from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AirtableHandoffContractTests(unittest.TestCase):
    def test_single_canonical_inline_transport_limit(self) -> None:
        matches = []
        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        for relative_path in tracked:
            path = ROOT / relative_path
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for value in re.findall(
                r"inline_prompt_transport_byte_limit\s*=\s*(\d+)",
                content,
            ):
                matches.append((relative_path, int(value)))
        self.assertEqual(matches, [("docs/prompts.md", 4096)])
