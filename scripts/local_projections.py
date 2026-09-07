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
CLAUDE_REVIEW = ROOT / "scripts" / "install-claude-review"


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
        choices=("global-bootstrap", "claude-review"),
        action="append",
        help="Select a component (default: every qualified component).",
    )
    parser.add_argument("--codex-file", type=Path)
    parser.add_argument("--claude-file", type=Path)
    parser.add_argument("--require-claude", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected = args.component or ["global-bootstrap", "claude-review"]
    selected = list(dict.fromkeys(selected))

    # Every selected component plan is read-only. Complete the full batch
    # preflight before the first component-owned mutation.
    if args.mode == "apply":
        preflight: list[CommandResult] = []
        if "global-bootstrap" in selected:
            preflight.append(
                run("global-bootstrap", global_bootstrap_arguments(args, "plan"))
            )
        if "claude-review" in selected:
            preflight.append(
                run(
                    "claude-review",
                    [sys.executable, str(CLAUDE_REVIEW), "--plan-installed"],
                )
            )
        for result in preflight:
            render(result)
        if any(result.returncode for result in preflight):
            print("FAIL apply preflight: a selected component is blocked")
            return 1

    results: list[CommandResult] = []
    if args.mode == "apply" and "claude-review" in selected:
        claude_arguments = [
            sys.executable,
            str(CLAUDE_REVIEW),
            "--reconcile-installed",
        ]
        claude_apply = run("claude-review", claude_arguments)
        render(claude_apply)
        if claude_apply.returncode:
            print("FAIL apply: claude-review reconciliation did not complete")
            return 1
    if "global-bootstrap" in selected:
        results.append(
            run(
                "global-bootstrap",
                global_bootstrap_arguments(args, args.mode),
            )
        )
    if "claude-review" in selected and args.mode != "apply":
        claude_operation = (
            "--plan-installed" if args.mode == "plan" else "--check-installed"
        )
        results.append(
            run(
                "claude-review", [sys.executable, str(CLAUDE_REVIEW), claude_operation]
            )
        )

    for result in results:
        render(result)

    if any(result.returncode for result in results):
        return 1
    if args.mode == "apply":
        verified: list[CommandResult] = []
        if "global-bootstrap" in selected:
            verified.append(
                run("global-bootstrap", global_bootstrap_arguments(args, "check"))
            )
        if "claude-review" in selected:
            verified.append(
                run(
                    "claude-review",
                    [sys.executable, str(CLAUDE_REVIEW), "--check-installed"],
                )
            )
        for result in verified:
            render(result)
        if any(result.returncode for result in verified):
            print("FAIL apply verification: a selected component did not reach current state")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
