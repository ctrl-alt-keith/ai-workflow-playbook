# Context Refresh

## Purpose

Context refresh rebuilds durable repository orientation context for fresh-thread
handoff, lost context, or meaningful repo drift. For new threads, start with the
[Thread Initialization](thread-init.md) pattern, then refresh context when
verified repository identity and branch context matter.

## Primary Workflow

Run the executable target from the repository root:

```sh
make context-refresh
```

Use `dist/context-refresh.md` as the generated repository orientation snapshot.
It is a convenience artifact for handoff and orientation, not a canonical
document.

## Source of Truth

Repository code, issues, pull requests, and docs remain authoritative. GitHub
and the local repository state outrank generated snapshots and prior briefs.

Do not edit generated snapshots to make them true. Regenerate them after repo
state changes or before using an old snapshot to guide action.

Dynamic pull request and issue state is intentionally omitted from generated
context refresh output. Inspect GitHub directly before acting on current PR or
issue state.

## Interpretation

- `blocked` or `unavailable` repo entries mean inspection failed. Do not guess
  the missing state from prior context, summaries, or expectations.
- Stale snapshots should be regenerated before acting on their conclusions.
- Generated output can summarize durable orientation state, but it does not
  replace direct inspection when decisions require current evidence.

## Boundaries

This page describes the principles for using and interpreting context refresh.
Executable behavior lives in `make context-refresh` and
`scripts/generate_context_refresh.py`.
