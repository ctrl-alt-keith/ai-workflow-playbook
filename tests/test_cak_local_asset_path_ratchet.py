#!/usr/bin/env python3
"""Ratchet CAK local placement across active code, policy, and guidance."""

from __future__ import annotations

import re
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

OPERATOR_HOME_PATTERN = re.compile(r"/(?:Users|home)/[^/\s`\"']+")


class CakLocalAssetPathRatchetTests(unittest.TestCase):
    def test_active_surfaces_do_not_hardcode_the_operator_home(self) -> None:
        observed: list[tuple[str, int]] = []

        for search_root in OPERATOR_PATH_SURFACES:
            self.assertTrue(search_root.exists(), f"missing surface: {search_root}")
            paths = tracked_files(search_root)
            self.assertTrue(paths, f"no tracked files for surface: {search_root}")
            for path in paths:
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                relative = path.relative_to(ROOT).as_posix()
                for line_number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), start=1
                ):
                    if OPERATOR_HOME_PATTERN.search(line):
                        observed.append((relative, line_number))

        self.assertEqual([], observed)


if __name__ == "__main__":
    unittest.main()
