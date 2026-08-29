#!/usr/bin/env python3
"""Read-only validation for Playbook-owned provider-global bootstrap blocks."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PROJECTIONS = ROOT / "distributions" / "global-bootstrap"
START_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:start -->"
END_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:end -->"


@dataclass(frozen=True)
class Check:
    provider: str
    actual: Path
    expected: Path


def extract_managed_block(contents: str, path: Path) -> str:
    """Return the single marked block, including markers and final newline."""
    if contents.count(START_MARKER) != 1 or contents.count(END_MARKER) != 1:
        raise ValueError(
            f"{path}: expected exactly one global-bootstrap start/end marker pair"
        )

    start = contents.index(START_MARKER)
    end_start = contents.index(END_MARKER)
    if end_start < start:
        raise ValueError(f"{path}: global-bootstrap markers are out of order")
    end = end_start + len(END_MARKER)
    return contents[start:end].rstrip("\n") + "\n"


def validate(check: Check) -> str | None:
    if not check.actual.is_file():
        return f"{check.provider}: missing local instruction file {check.actual}"

    expected = check.expected.read_text(encoding="utf-8")
    actual_contents = check.actual.read_text(encoding="utf-8")
    try:
        actual = extract_managed_block(actual_contents, check.actual)
    except ValueError as error:
        return f"{check.provider}: {error}"

    if actual != expected:
        return (
            f"{check.provider}: managed block differs from canonical projection "
            f"{check.expected}"
        )
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare local provider-global routers with canonical projections."
    )
    parser.add_argument(
        "--codex-file",
        type=Path,
        default=Path.home() / ".codex" / "AGENTS.md",
    )
    parser.add_argument(
        "--claude-file",
        type=Path,
        default=Path.home() / ".claude" / "CLAUDE.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checks = (
        Check("Codex", args.codex_file, PROJECTIONS / "codex-AGENTS.md"),
        Check("Claude", args.claude_file, PROJECTIONS / "claude-CLAUDE.md"),
    )
    failures = [failure for check in checks if (failure := validate(check))]

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        print(
            "Remediation: review the canonical projection, replace only the marked "
            "block in the local file, and rerun this check."
        )
        return 1

    for check in checks:
        print(f"PASS {check.provider}: {check.actual}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
