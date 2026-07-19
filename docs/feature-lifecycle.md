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

### Proportional proposal-first delivery

Use a proposal-first path when implementation depends on material ambiguity,
cross-repository ownership, policy or authority boundaries, irreversible or
high-risk consequences, or a review cost that is meaningfully reduced by
agreeing on the change before mutation. A human or repo-local workflow may also
require this path explicitly.

Keep it proportional. Small, mechanical, low-risk changes with an obvious
owner, bounded diff, and ordinary validation can move directly from source
inspection to implementation. They do not need a proposal artifact,
independent review, or proposal-only pull request merely to follow a longer
example.

When the proposal-first path applies, preserve these semantic transitions:

1. retrieve the authoritative sources and identify owners, scope, exclusions,
   risks, and acceptance criteria;
2. prepare the bounded proposal and name its exact artifact identity;
3. obtain independent review when the human, task, or selected risk contract
   requires it;
4. disposition every substantive finding and decide whether the original
   review remains applicable using
   [`review-packet.md`](review-packet.md#independent-review-findings-and-re-review);
5. freeze the exact proposal identity and obtain human approval that states the
   implementation authority granted;
6. implement only the approved scope, then run canonical validation;
7. present the exact implementation head for final human review and separate
   merge authorization; and
8. after merge, retrieve the resulting integrated identity and reconcile any
   external authority that tracks completion.

These transitions do not require eight separate gates, branches, or pull
requests. A selected independent review is evidence for a human decision, not
approval or execution authority. A frozen proposal makes implementation more
bounded; it does not eliminate implementation judgment, validation, or final
review.

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

## Stage Boundary Receipts

For a material workflow stage, leave a durable receipt that makes the completed
boundary recoverable and reviewable. Record the applicable operational
contract, material inputs and outputs, validation performed, authority
consumed, any authority granted by the authorized decision-maker, the result,
and the exact next permitted action.

A receipt records a transition; it does not approve the transition or grant
authority. Stored status, successful validation, or receipt creation must not
be treated as permission to begin a later stage. Keep the form and storage
proportionate to the workflow: this is a semantic contract, not a required
schema or a receipt for every routine step.

Do not conflate a stage-boundary receipt with the append-only prompt attempt
receipt in [`prompt-contracts.md`](prompt-contracts.md). The latter records
selected and derived execution evidence under an immutable semantic prompt
contract and has explicit zero authority, zero state-transition, and zero
orchestration effects.

## Retrospective And Evolution

Substantial workflow runs and protocol-evolution efforts should preserve both
the intended work product and bounded operational evidence needed to understand
how the workflow behaved. This does not require retaining every intermediate
thought, transcript, or temporary artifact.

For substantial evolution work, review and freeze the observation set before
implementing doctrine from it. Keep the retrospective evidence artifact
separate from the later implementation lifecycle: implementation proceeds
through its own issue, branch, pull request, review, and authority boundaries.
A frozen retrospective supports traceability; it does not authorize execution.

Preserve these as independent decisions:

1. Observation: what was observed and the evidence supporting it.
2. Maturity: how strongly the evidence supports the observation.
3. Disposition: what should happen to the observation.
4. Target: which owner or destination should act on it.
5. Implementation: the bounded change, experiment, rejection, archive, or
   other follow-through.

Do not collapse evidence strength into priority or implementation preference.
Keep a validated problem separate from a proposed solution; each needs the
evidence and review appropriate to its claim. Keep open questions visible until
a reviewed decision answers, supersedes, rejects, archives, or intentionally
retires them.

Classify retrospective outputs by owner and disposition before follow-up. Make
clear which outputs are reusable doctrine, workflow improvements, operational
improvements, research findings, experiments, rejections, or archives without
requiring one repository name or ticket per item. Doctrine promotion should
trace back to the reviewed evidence and decisions that support it; use the
[`review packet`](review-packet.md#doctrine-provenance) for that boundary.

Evolve protocols incrementally from evidence-supported changes. The existing
promotion criteria in [`trust-topology.md`](trust-topology.md) and the staging
and cleanup boundaries in [`notes-repositories.md`](notes-repositories.md)
remain the owners of their respective vocabularies; do not create a competing
promotion track here.

Preserve useful information long enough for an explicit retention or retirement
decision. Preservation is not indefinite retention and does not override
security, privacy, licensing, legal, repository-local, or other applicable
retention policy.

Apply this discipline proportionately. Small routine changes with direct source
evidence, a bounded diff, and ordinary validation do not require a frozen
retrospective or heavyweight evolution ceremony.

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

Every semantic phase boundary requires an explicit review and authority
boundary. After a phase merges, start a new branch and PR for the next lifecycle
phase. This keeps the review surface narrow and preserves clean checkpoints.

Implementation and approval may share one PR only when the approval is anchored
to the exact reviewed commit or bytes and downstream authority remains
fail-closed until that approval is recorded. Any semantic change after the
reviewed identity requires a new review. This narrow same-PR allowance does not
remove a lifecycle phase, reduce a required gate, or permit another semantic
phase boundary to pass without explicit review and authority.

For proposal-first work, a proposal-only draft PR can be a proportionate,
durable collaboration surface. When repository policy permits, the exact
proposal may be approved on that branch and bounded implementation may continue
on the same branch and PR. Keep the proposal approval and final implementation
review distinct: proposal approval authorizes only the stated implementation,
and merge still requires separate authorization against the exact reviewed
implementation head. This topology is recommended only when it improves
traceability or review; it is not required for small changes or repositories
whose local policy uses another review surface.

Record two different identities when merge follows. The implementation head is
the pre-merge commit reviewed for merge authorization. The resulting integrated
identity is the commit actually present on the base branch after the repository's
allowed merge method runs. Retrieve the latter after merge instead of assuming
that it is a merge commit or that it equals the reviewed head.

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

After merge, reconcile live authority instead of replaying the pre-merge plan.
Retrieve the actual integrated identity, current GitHub issue and PR state, and
the current external planning state. Add the integrated identity or durable
backlink and update external status only when the owning workflow still needs
it, then retrieve the final state again. If an integration already performed
an automatic transition, verify it and do not repeat it. External planning
state remains separately owned and cannot override repository state.

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

Use the canonical implementation-isolation rule in
[`repo-readiness.md`](repo-readiness.md#pr-readiness): one repository, one
branch, one dedicated repo-local worktree, and one PR per change. Keep the main
checkout clean, fetch before creating task worktrees so `origin/main` is
current, and do issue work only inside the task worktree unless the work is
read-only or the human explicitly says not to modify files.

For Codex-specific worktree creation, reuse, cleanup, parallel-batch handling,
and blocked cleanup reporting, follow
[`tool-adapters/codex.md`](tool-adapters/codex.md#worktrees). For
other executors, follow the matching adapter when one documents stricter
worktree handling.

The expected pattern is:

1. Merge the current phase
2. Open a new branch for the next phase
3. Open a new PR for that phase
4. Complete post-release capture before starting the next major arc

When overlapping PRs touch the same shared surface, merge behavior, workflow, or other source-of-truth changes before formatting, restructuring, or cleanup. Let cleanup absorb the settled state last.

When concurrent PRs have no file overlap and no open review concerns, merge order
is flexible. Say that explicitly in the review packet instead of inventing a
false dependency.

Do not roll multiple lifecycle phases into one long-running branch unless there
is a strong reason and the review surface remains clear. The same-PR
implementation-and-approval allowance above is not a blanket exception to this
sequential lifecycle discipline.
