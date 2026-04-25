# Feature Lifecycle

The delivery lifecycle is:

1. Design
2. Contract tests
3. Implementation
4. Hardening
5. Release
6. Capture

Each phase should have a clear goal, a clear review surface, and a natural stopping point before the next phase begins.

Use [`alignment-checkpoints.md`](alignment-checkpoints.md) to decide when to pause or split work, and use [`review-packet.md`](review-packet.md) to prepare the review surface before merge or release.

## Phase Guidance

### Design

Define the intended behavior, constraints, risks, and acceptance shape. The goal is alignment, not code volume.

### Contract tests

Write or update the tests, checks, or examples that define what must be true. This anchors implementation to an explicit contract.

Prefer semantic assertions over formatting-sensitive assertions when formatting is not the contract. For user-facing output, favor behavior-oriented assertions, stable substrings, or shared helpers.

### Implementation

Build only what is needed to satisfy the contract. Keep feedback loops short and avoid mixing extra polish into the first pass.

For same-repo runs, anchor implementation to one fetched `origin/main` snapshot at task start and treat that snapshot as the canonical base for the duration of the run. Check mergeability against current `main` at the end as a separate release-readiness concern rather than repeatedly re-anchoring mid-run.
A clean local branch at the end means the run stayed coherent against that anchored base; it does not by itself prove that a remote PR is still mergeable after `main` moves.

### Hardening

Address edge cases, refactors, failure handling, review findings, and CI quality. This is where robustness catches up to correctness.

### Release

Prepare the work to ship with a clean review packet, validation evidence, and any final release checks. If the repo does not have a formal validation path yet, record the lightweight validation that was used instead.
If GitHub shows `BLOCKED` or pending status at this stage, check the underlying cause before reacting: pending checks or reviews usually mean wait, while failed required checks or true merge conflicts require action.

### Capture

Record what should become reusable guidance before the next delivery arc starts.

## Project Maps

When a repository has multiple active or upcoming arcs, keep a lightweight
project map to show the current direction of travel. Use it when GitHub issues
alone no longer make the overall sequence or priorities easy to see. Do not add
one for tiny repositories, one-off work, or repos whose near-term direction is
already obvious from a small issue and PR set.

A project map should stay lightweight and focus on the arc-level view:

- current state
- active arc
- next arcs
- deferred or usage-driven work
- guiding principles or constraints

Keep project-map maintenance tied to the work that changes arc state. When a PR
completes an arc or changes the current sequencing, update the project map in
that same PR so the map reflects the shipped state instead of drifting behind
it. Avoid separate project-map-only PRs unless creating the initial map, doing
a planning checkpoint, or handling a major roadmap reshuffle. Keep map edits
minimal and directly tied to the real change.

Treat release PRs the same way. A release is a state checkpoint, so include any
needed project map updates in the release PR itself: reflect completed arcs in
current state, set the next active arc where appropriate, and avoid separate
project-map-only PRs for release updates.

## Branch And PR Rules

After each merged phase, start a new branch and PR for the next lifecycle phase. This keeps the review surface narrow and preserves clean checkpoints.

Start same-repo arcs from fresh `origin/main`. Do not reuse an old feature branch unless intentionally continuing that PR.

For mixed-purpose repos that contain code, docs, tests, and release or
workflow content, keep purpose-based branch prefixes such as `feat/`, `fix/`,
`docs/`, `chore/`, `refactor/`, and `test/`. Reserve broad tool-oriented
prefixes such as `codex/` for doc-only repos, scratch experiments, or repos
whose branch convention explicitly allows them. Branch names should describe
the change, not the tool that made it; for example
`feat/minimal-cli-baseline`, `docs/project-map`, `chore/release-v0.7.0`, and
`fix/run-ctrl-c-skip`.

For same-repo parallel work, prefer isolated Git worktrees over multiple arcs
sharing one checkout. Keep the main checkout clean and on `main`, fetch before
creating task worktrees so `origin/main` is current, create one worktree per
issue or task from that current `origin/main`, and do the issue work only
inside its worktree.

Before starting a same-repo worktree run, inspect existing worktree metadata and
clear stale entries so an old attempt does not distort the new setup. Reuse an
existing same-repo worktree only when it is clearly the same active issue, PR,
or arc and its state is still clean and intelligible; otherwise recreate from
current `origin/main`, especially when the worktree belongs to a different arc,
the state is stale or unclear, or cleanup and recovery would be more confusing
than starting fresh. Bias toward clarity over clever reuse.

After merge, cleanup succeeds when the experiment or task worktrees created for
that run are removed or clearly accounted for. Do not treat unrelated
pre-existing worktrees as cleanup failures. If removal is blocked or deferred,
report that clearly, avoid deleting unrelated worktrees, and leave the repo in
a known, intelligible state.

The expected pattern is:

1. Merge the current phase
2. Open a new branch for the next phase
3. Open a new PR for that phase
4. Complete post-release capture before starting the next major arc

When overlapping PRs touch the same shared surface, merge behavior, workflow, or other source-of-truth changes before formatting, restructuring, or cleanup. Let cleanup absorb the settled state last.

When concurrent PRs have no file overlap and no open review concerns, merge order
is flexible. Say that explicitly in the review packet instead of inventing a
false dependency.

Do not roll multiple lifecycle phases into one long-running branch unless there is a strong reason and the review surface remains clear.
