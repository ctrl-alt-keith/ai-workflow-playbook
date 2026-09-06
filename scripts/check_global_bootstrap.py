#!/usr/bin/env python3
"""Validate, plan, and apply bounded local global-bootstrap reconciliation."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import difflib
import os
from pathlib import Path
import stat
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PROJECTIONS = ROOT / "distributions" / "global-bootstrap"
CANONICAL_ROUTER = PROJECTIONS / "bootstrap-router.md"
START_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:start -->"
END_MARKER = "<!-- ai-workflow-playbook:global-bootstrap:end -->"


@dataclass(frozen=True)
class Check:
    provider: str
    actual: Path


@dataclass(frozen=True)
class ManagedBlock:
    """One safe, existing managed block in a regular local instruction file."""

    body_start: int
    body_end: int
    body: str


@dataclass(frozen=True)
class Inspection:
    """The current observed local state for one qualified provider surface."""

    check: Check
    contents: str
    raw: bytes
    mode: int
    device: int
    inode: int
    block: ManagedBlock


def extract_managed_block(contents: str, path: Path) -> ManagedBlock:
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
    body = contents[body_start:end_start].strip("\n") + "\n"
    return ManagedBlock(body_start, end_start, body)


def normalize_router(contents: str) -> str:
    """Return router text with normalized outer newlines."""
    return contents.strip("\n") + "\n"


def inspect(check: Check) -> Inspection:
    """Read one regular local file without normalizing any unmanaged bytes."""
    try:
        descriptor = os.open(
            check.actual, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        )
    except FileNotFoundError as error:
        raise ValueError(f"missing local instruction file {check.actual}") from error
    except OSError as error:
        raise ValueError(
            f"unsupported local instruction file type {check.actual}"
        ) from error
    try:
        with os.fdopen(descriptor, "rb") as source:
            file_stat = os.fstat(source.fileno())
            if not stat.S_ISREG(file_stat.st_mode):
                raise ValueError(
                    f"unsupported local instruction file type {check.actual}"
                )
            raw = source.read()
        contents = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{check.actual}: expected UTF-8 local instruction text") from error
    try:
        block = extract_managed_block(contents, check.actual)
    except ValueError as error:
        raise ValueError(str(error)) from error
    return Inspection(
        check,
        contents,
        raw,
        stat.S_IMODE(file_stat.st_mode),
        file_stat.st_dev,
        file_stat.st_ino,
        block,
    )


def validate(check: Check, expected: str) -> str | None:
    try:
        actual = inspect(check).block.body
    except ValueError as error:
        return f"{check.provider}: {error}"

    if actual != expected:
        return (
            f"{check.provider}: managed body differs from canonical router "
            f"{CANONICAL_ROUTER}"
        )
    return None


def render_plan(inspection: Inspection, expected: str) -> str:
    """Render the exact normalized managed-body substitution for review."""
    if inspection.block.body == expected:
        return f"PASS {inspection.check.provider}: already current {inspection.check.actual}"
    diff = difflib.unified_diff(
        inspection.block.body.splitlines(keepends=True),
        expected.splitlines(keepends=True),
        fromfile=f"{inspection.check.actual} (managed body)",
        tofile=f"{CANONICAL_ROUTER} (canonical body)",
    )
    return (
        f"PLAN {inspection.check.provider}: replace managed body in "
        f"{inspection.check.actual}\n" + "".join(diff)
    )


def replacement_contents(inspection: Inspection, expected: str) -> str:
    """Replace exactly the existing managed body, preserving surrounding text."""
    block = inspection.block
    return inspection.contents[: block.body_start] + "\n" + expected + inspection.contents[block.body_end :]


def write_atomically(inspection: Inspection, expected: str) -> None:
    """Write one replacement in the target directory after a fresh safe read."""
    destination = inspection.check.actual
    current_stat = destination.lstat()
    if (
        not stat.S_ISREG(current_stat.st_mode)
        or current_stat.st_dev != inspection.device
        or current_stat.st_ino != inspection.inode
    ):
        raise ValueError(f"{destination}: changed before managed-body replacement")
    replacement = replacement_contents(inspection, expected).encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.global-bootstrap-", dir=destination.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as temporary:
            temporary.write(replacement)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_name, inspection.mode)
        os.replace(temporary_name, destination)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def apply(check: Check, expected: str) -> str:
    """Re-read, safely reconcile, and verify one existing managed local block."""
    initial = inspect(check)
    if initial.block.body == expected:
        return f"PASS {check.provider}: already current {check.actual}"

    current = inspect(check)
    if (
        initial.raw != current.raw
        or initial.device != current.device
        or initial.inode != current.inode
    ):
        raise ValueError(f"{check.actual}: changed before managed-body replacement")
    write_atomically(current, expected)

    verified = inspect(check)
    if verified.block.body != expected:
        raise ValueError(f"{check.actual}: verification failed after managed-body replacement")
    return f"APPLY {check.provider}: verified {check.actual}"


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
    parser.add_argument(
        "--require-claude",
        action="store_true",
        help="Fail when the broader-rollout Claude instruction file is absent.",
    )
    parser.add_argument(
        "--mode",
        choices=("check", "plan", "apply"),
        default="check",
        help="Use read-only validation, a read-only exact substitution plan, or apply.",
    )
    parser.add_argument(
        "--provider",
        choices=("codex", "claude"),
        action="append",
        help="Select one or more local file-backed provider surfaces (default: all).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected = set(args.provider or ("codex", "claude"))
    checks: list[Check] = []
    if "codex" in selected:
        checks.append(Check("Codex", args.codex_file))
    if "claude" in selected and (args.claude_file.is_file() or args.require_claude or args.provider):
        checks.append(Check("Claude", args.claude_file))
    elif "claude" in selected:
        print(
            f"SKIP Claude: broader-rollout instruction file not installed "
            f"at {args.claude_file}"
        )
    expected = normalize_router(CANONICAL_ROUTER.read_text(encoding="utf-8"))

    if args.mode == "check":
        failures = [failure for check in checks if (failure := validate(check, expected))]
        if failures:
            for failure in failures:
                print(f"FAIL {failure}")
            print(
                "Remediation: run make plan-local-bootstrap, review the managed-body "
                "diff, run make apply-local-bootstrap, and rerun this check."
            )
            return 1
        for check in checks:
            print(f"PASS {check.provider}: {check.actual}")
        return 0

    if args.mode == "apply":
        try:
            for check in checks:
                inspect(check)
        except (OSError, ValueError) as error:
            print(f"FAIL apply preflight: {error}")
            return 1

    for check in checks:
        try:
            if args.mode == "plan":
                plan = render_plan(inspect(check), expected)
                print(plan, end="" if plan.endswith("\n") else "\n")
            else:
                print(apply(check, expected))
        except (OSError, ValueError) as error:
            print(f"FAIL {check.provider}: {error}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
