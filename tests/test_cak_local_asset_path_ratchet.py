#!/usr/bin/env python3
"""Ratchet CAK local placement across active code, policy, and guidance."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tracked_files(search_root: Path) -> list[Path]:
    """Return files Git tracks under ``search_root``.

    The ratchet governs the repository's committed active surfaces. Walking the
    filesystem instead would also read untracked local artifacts — editor state,
    build output, or OS metadata such as ``.DS_Store`` — which are not part of
    those surfaces and are not necessarily valid UTF-8.
    """

    result = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "ls-files",
            "-z",
            "--",
            search_root.relative_to(ROOT).as_posix(),
        ],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return [ROOT / entry for entry in result.stdout.split("\0") if entry]

# These are the reviewed active references at the CAK-178 implementation
# baseline. New entries require an explicit ownership review rather than
# silently extending local placement.
EXPECTED_LOCAL_REFERENCES = {
    (
        "docs/tool-adapters/claude.md",
        "runtime `HOME` recorded in the attempt receipt and prove that `.local`,",
    ),
    (
        "docs/tool-adapters/codex.md",
        "~/.local/bin/codex-safe-rm -rf -- TARGET [TARGET ...]",
    ),
    (
        "docs/tool-adapters/codex.md",
        "installer publishes the stable command `~/.local/bin/claude-review` with one",
    ),
    (
        "docs/tool-adapters/codex.md",
        "`~/.local/bin/.claude-review.json`. The content digest remains in that record",
    ),
    (
        "scripts/install-claude-review",
        'return effective_user_home() / ".local" / "bin"',
    ),
    (
        "scripts/install-codex-safe-rm",
        'return resolved_home / ".local" / "bin" / CONTROL_NAME',
    ),
}

# Executable sources, reusable guidance, and checked-in Codex policy/templates
# are the active surfaces that can establish CAK-managed production placement.
# Tests, fixtures, and historical evidence are intentionally outside this
# placement-ownership guarantee.
ACTIVE_SURFACE_ROOTS = (ROOT / "scripts", ROOT / "docs", ROOT / ".codex")

OPERATOR_PATH_SURFACES = ACTIVE_SURFACE_ROOTS + (
    ROOT / "distributions",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / "README.md",
)


class CakLocalAssetPathRatchetTests(unittest.TestCase):
    def test_active_code_policy_and_guidance_local_references_do_not_expand(self) -> None:
        observed: set[tuple[str, str]] = set()

        for search_root in ACTIVE_SURFACE_ROOTS:
            for path in tracked_files(search_root):
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                relative = path.relative_to(ROOT).as_posix()
                for line in path.read_text(encoding="utf-8").splitlines():
                    if ".local" in line:
                        observed.add((relative, line.strip()))

        self.assertEqual(EXPECTED_LOCAL_REFERENCES, observed)

    def test_active_surfaces_do_not_hardcode_the_operator_home(self) -> None:
        observed: list[tuple[str, int]] = []

        for search_root in OPERATOR_PATH_SURFACES:
            for path in tracked_files(search_root):
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                relative = path.relative_to(ROOT).as_posix()
                for line_number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), start=1
                ):
                    if "/Users/keith" in line:
                        observed.append((relative, line_number))

        self.assertEqual([], observed)


if __name__ == "__main__":
    unittest.main()
