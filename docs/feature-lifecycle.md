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

For same-repo runs, fetch current `origin/main` at task start and anchor
implementation to that fetched baseline. Check mergeability against current
`main` before opening or updating the PR. Update or rebase only when there is a
conflict, overlapping upstream change, repo policy requirement, or explicit
human request, then rerun the repository's canonical validation entrypoint.
A clean local branch at the end means the run stayed coherent against its
anchored base; it does not by itself prove that a remote PR is still mergeable
after `main` moves.

### Hardening

Address edge cases, refactors, failure handling, review findings, and CI quality. This is where robustness catches up to correctness.

### Release

Prepare the work to ship with a clean review packet, validation evidence, and any final release checks. If the repo does not have a formal validation path yet, record the lightweight validation that was used instead.
If GitHub shows `BLOCKED` or pending status at this stage, check the underlying cause before reacting: pending checks or reviews usually mean wait, while failed required checks or true merge conflicts require action.

### Capture

Record any evidence-supported reusable lesson before the next delivery arc
starts. If the lesson is promoted into the playbook, include a notes cleanup
follow-up or state explicitly that no notes cleanup is needed.

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

Start same-repo arcs from freshly fetched `origin/main`. Do not reuse an old
feature branch unless intentionally continuing that PR.

### Repo Change Completion

After the interaction mode preflight in
[`repo-readiness.md`](repo-readiness.md#interaction-mode-preflight) selects
implementation mode, repo-changing work follows the normal delivery path.

For repo changes, "done" means all of the following are complete:

- change implemented
- local checks run
- branch created or confirmed
- commit created
- branch pushed
- ready-for-review PR opened against the intended base branch

Opening a PR is the default for repo changes. Passing checks validates the
change; opening the PR delivers it. Do not stop at "file created" or
"checks passed."
For completed work, the PR is ready for review by default. Draft PRs are only
allowed when the human explicitly requests one or when the work is
intentionally incomplete or early-feedback-only.

Skip commit or PR only when the user explicitly says local only, do not commit,
do not open a PR, or draft this but don't ship it.

For exploration, design, or review-only tasks that do not change repo files,
stop after the findings or recommendations unless the request also asks for
shipped changes. If those tasks do produce repo changes, follow the same
branch, validation, and PR flow before calling them complete.

### Issue And Planning Coordination

For repository implementation work, GitHub remains the implementation and
closure source of truth unless repo-local guidance explicitly defines a
different system of record. GitHub issues, pull requests, closing keywords, CI,
review state, and merge state determine whether repo work is complete.

Planning systems such as Linear are coordination layers by default. Use them to
track planning intent, status, assignment, sequencing, or stakeholder context,
but do not treat them as authoritative over repository implementation state
unless the target repository explicitly says so. The same rule applies to
similar planning mirrors or boards.

When both GitHub and planning identifiers exist, implementation PRs should
reference both. Keep the GitHub closing keyword tied to the GitHub issue and
include the planning identifier as coordination context, for example:

```text
Closes #163
Linear: CAK-5
```

Use GitHub closing keywords such as `Closes #163` as the preferred mechanism
for GitHub issue closure. Do not manually close the GitHub issue as a separate
coordination step unless the repository workflow or human explicitly asks for
it.

Planning tickets will usually remain open while the implementation PR is still
open unless the planning system's local workflow says otherwise. Usually mark
the planning ticket complete only after the PR has merged and the linked GitHub
issue closure has been confirmed. During the PR-open state, planning status
should reflect implementation in progress or in review, not merge-complete.

For multi-issue work, keep the mapping explicit: list every GitHub issue the PR
intends to close and every planning ticket it coordinates with. If one PR
resolves only part of a larger planning ticket, say that directly and leave the
remaining planning item or follow-up open.

Residual risks and follow-ups belong in the review packet and PR notes. Create
or keep separate follow-up issues or planning tickets only when work remains
after merge; do not hide unfinished required work behind a completed planning
status.

Use purpose-based branch prefixes that describe the change, not the tool that
made it. AI-agent branches should use concise, non-tool-branded names such as
`docs/<short-topic>`, `fix/<short-topic>`, `chore/<short-topic>`, or
`feat/<short-topic>`. Repo-local guidance may narrow the allowed prefixes, but
broad tool-name prefixes such as `codex/`, `claude/`, or `copilot/` should be
avoided unless a repository intentionally requires them.

Every implementation change must happen in a dedicated Git worktree: one
repository, one branch, one worktree, and one PR per change. Keep the main
checkout clean and on `main`, fetch before creating task worktrees so
`origin/main` is current, create one worktree per issue or task from that
current `origin/main`, and do the issue work only inside its worktree. The only
exceptions are read-only inspection or explicit human instruction not to modify
files.

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
