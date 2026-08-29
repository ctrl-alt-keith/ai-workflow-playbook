#!/usr/bin/env python3
"""Read-only validation for Playbook-owned provider-global bootstrap blocks."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PROJECTIONS = ROOT / "distributions" / "global-bootstrap"
CANONICAL_ROUTER = PROJECTIONS / "bootstrap-router.md"
START_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:start -->"
END_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:end -->"


@dataclass(frozen=True)
class Check:
    provider: str
    actual: Path


def extract_managed_body(contents: str, path: Path) -> str:
    """Return the single marked router body with one final newline."""
    if contents.count(START_MARKER) != 1 or contents.count(END_MARKER) != 1:
        raise ValueError(
            f"{path}: expected exactly one global-bootstrap start/end marker pair"
        )

    start = contents.index(START_MARKER)
    end_start = contents.index(END_MARKER)
    if end_start < start:
        raise ValueError(f"{path}: global-bootstrap markers are out of order")
    body_start = start + len(START_MARKER)
    return contents[body_start:end_start].strip("\n") + "\n"


def validate(check: Check) -> str | None:
    if not check.actual.is_file():
        return f"{check.provider}: missing local instruction file {check.actual}"

    expected = CANONICAL_ROUTER.read_text(encoding="utf-8")
    actual_contents = check.actual.read_text(encoding="utf-8")
    try:
        actual = extract_managed_body(actual_contents, check.actual)
    except ValueError as error:
        return f"{check.provider}: {error}"

    if actual != expected:
        return (
            f"{check.provider}: managed body differs from canonical router "
            f"{CANONICAL_ROUTER}"
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
        Check("Codex", args.codex_file),
        Check("Claude", args.claude_file),
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
