#!/usr/bin/env python3
"""Compose the checked-in reconciliation contracts for local projections."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_BOOTSTRAP = ROOT / "scripts" / "check_global_bootstrap.py"


@dataclass(frozen=True)
class CommandResult:
    name: str
    returncode: int
    output: str


def run(name: str, arguments: list[str]) -> CommandResult:
    """Run a component-owned read or reconciliation command unchanged."""
    result = subprocess.run(
        arguments,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return CommandResult(name, result.returncode, result.stdout)


def global_bootstrap_arguments(args: argparse.Namespace, mode: str) -> list[str]:
    command = [sys.executable, str(GLOBAL_BOOTSTRAP), "--mode", mode]
    if args.codex_file is not None:
        command.extend(["--codex-file", str(args.codex_file)])
    if args.claude_file is not None:
        command.extend(["--claude-file", str(args.claude_file)])
    if args.require_claude:
        command.append("--require-claude")
    return command


def render(result: CommandResult) -> None:
    """Keep component output visible without interpreting its safety semantics."""
    output = result.output.rstrip("\n")
    if output:
        print(output)
    elif result.returncode:
        print(f"BLOCKED {result.name}: component returned no diagnostic output")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check, plan, or apply Playbook-managed local projections."
    )
    parser.add_argument("--mode", choices=("check", "plan", "apply"), default="check")
    parser.add_argument(
        "--component",
        choices=("global-bootstrap",),
        action="append",
        help="Select a component (default: every qualified component).",
    )
    parser.add_argument("--codex-file", type=Path)
    parser.add_argument("--claude-file", type=Path)
    parser.add_argument("--require-claude", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected = args.component or ["global-bootstrap"]
    if "global-bootstrap" not in selected:
        return 0
    result = run("global-bootstrap", global_bootstrap_arguments(args, args.mode))
    render(result)
    return int(result.returncode != 0)


if __name__ == "__main__":
    raise SystemExit(main())
