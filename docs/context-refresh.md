# Context Refresh

## Purpose

Context refresh rebuilds current repository-state context for fresh-thread
handoff, lost context, or meaningful repo drift. For new threads, start with the
[Thread Initialization](thread-init.md) pattern, then refresh context when
verified current state matters.

## Primary Workflow

Run the executable target from the repository root:

```sh
make context-refresh
```

Use `dist/context-refresh.md` as the generated current-state snapshot. It is a
convenience artifact for handoff and orientation, not a canonical document.

## Source of Truth

Repository code, issues, pull requests, and docs remain authoritative. GitHub
and the local repository state outrank generated snapshots and prior briefs.

Do not edit generated snapshots to make them true. Regenerate them after repo
state changes or before using an old snapshot to guide action.

## Interpretation

- `blocked` or `unavailable` repo entries mean inspection failed. Do not guess
  the missing state from prior context, summaries, or expectations.
- Stale snapshots should be regenerated before acting on their conclusions.
- Generated output can summarize verified state, but it does not replace direct
  inspection when decisions require current evidence.

## Boundaries

This page describes the principles for using and interpreting context refresh.
Executable behavior lives in `make context-refresh` and
`scripts/generate_context_refresh.py`.
