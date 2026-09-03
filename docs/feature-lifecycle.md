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

## Activation

Feature-lifecycle guidance becomes required when the current authorized action
first enters feature-delivery planning or execution. Establish the current
delegated action and interaction mode, then the governing workflow and current
authorized action, before deciding whether lifecycle planning or execution is
current.

Related nouns, recorded future intent, explicit implementation intent, and
implementation eligibility do not activate this guidance by themselves. When a
prerequisite workflow owns the current completion boundary, it remains the
governing workflow until the current authorized action transitions into
feature-delivery planning or execution.

Lifecycle planning includes defining intended behavior, constraints, risks, or
acceptance shape; preparing a proposal-first change; and defining contract
tests. Proposal-first planning therefore activates this guidance before
mutation. Activation does not grant implementation authority, and an
implementation blocker does not deactivate lifecycle planning that is already
the current authorized action.

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

Evolve protocols incrementally from evidence-supported changes. The trust-level
promotion criteria in [`trust-topology.md`](trust-topology.md) and the staging
and cleanup boundaries in [`notes-repositories.md`](notes-repositories.md)
remain the owners of their respective vocabularies; do not create competing
trust-level or notes-staging vocabulary here. This document owns the
human-authorized transition from candidate or revised guidance to accepted
doctrine and its materiality trigger.

Preserve useful information long enough for an explicit retention or retirement
decision. Preservation is not indefinite retention and does not override
security, privacy, licensing, legal, repository-local, or other applicable
retention policy.

Apply this discipline proportionately. Small routine changes with direct source
evidence, a bounded diff, and ordinary validation do not require a frozen
retrospective or heavyweight evolution ceremony.

## Doctrine Promotion

Doctrine promotion is the explicit human-authorized transition by which
candidate or revised reusable guidance becomes accepted Playbook doctrine.
Research, synthesis, review, validation, a pull request, and merge provide
evidence or implementation state; none supplies promotion authority.

Use the staging and cleanup vocabulary in
[`notes-repositories.md`](notes-repositories.md), the governed-review mode in
[`external-ai-reviewer.md`](external-ai-reviewer.md), and the finding
disposition, re-review, and doctrine-provenance contracts in
[`review-packet.md`](review-packet.md). This section owns only the
doctrine-promotion lifecycle and the trigger that makes governed independent
review mandatory.

### Material doctrine trigger

A proposed doctrine promotion is **material** when accepting it would have at
least one of these observable effects:

1. **Authority boundary:** assign, remove, or change who controls or may
   authorize a consequential human, AI, automation, source, approval,
   acceptance, merge, release, or promotion decision.
2. **Mandatory lifecycle gate:** add, remove, or change a required
   prerequisite, review, validation, approval, fail-closed, promotion,
   release, completion, or other lifecycle transition condition.
3. **Cross-boundary contract:** add, remove, or change a required semantic
   contract, canonical owner, or normative obligation at a boundary among
   Playbook canonical owners, repositories, or executor implementations.
4. **Architecture boundary:** promote an architecture foundation as doctrine,
   or add, remove, or change an accepted Product identity or status,
   cross-repository Repository boundary, or runtime boundary.
5. **Reverse doctrine transition:** demote accepted doctrine to candidate
   guidance, withdraw it, or explicitly replace it with named superseding
   doctrine.

The proposer must name the affected boundary and matching trigger in the
proposal or review packet. If none applies, the promotion is non-material and
uses proportional review. Scope, novelty, line count, file count, document
length, subjective importance, low confidence, and a request for extra
confidence are indicators that may justify closer inspection; they are not
materiality triggers.

A material promotion requires governed independent artifact review before the
human promotion decision. A non-material promotion remains eligible for
ordinary proportional review. Both paths still require explicit human
promotion of the exact reviewed artifact.

When classification is challenged, the challenge must identify a concrete
affected boundary and one of the triggers above. The human promotion authority
decides any unresolved classification before promotion. Until that decision is
recorded, the guidance remains candidate or revised guidance rather than
accepted doctrine. Uncertainty therefore fails closed at a concrete disputed
boundary without making an ungrounded request for more confidence an automatic
review gate.

### Promotion lifecycle

Use this lifecycle without creating a second staging, finding-disposition, or
provenance vocabulary:

1. Preserve the research, operational evidence, negative evidence, and
   competing hypotheses in their existing evidence or staging owner.
2. Prepare one bounded candidate synthesis with an exact artifact identity,
   scope, exclusions, proposed normative effect, and materiality
   classification.
3. For a material promotion, obtain governed independent review of that exact
   artifact. Record the selected reviewer identity and provider, and handle a
   named reviewer failure or proposed substitution under
   [`external-ai-reviewer.md`](external-ai-reviewer.md#reviewer-selection-and-failure).
   For a non-material promotion, select review proportionately.
4. Disposition every substantive independent-review finding and determine
   whether the original review remains applicable using
   [`review-packet.md`](review-packet.md#independent-review-findings-and-re-review).
   Use focused re-review when that contract selects it; do not require or skip
   re-review merely because bytes changed.
5. Prepare the
   [`doctrine-provenance`](review-packet.md#doctrine-provenance) review packet.
   Link the evidence, candidate identity, review record, finding dispositions,
   validation, open questions, and exact implementation artifact without
   copying the full evidence history into doctrine.
6. Obtain an explicit human promotion decision against the exact reviewed
   artifact. A reviewer verdict, finding resolution, validation result,
   approval capability, execution capability, or merge result does not grant
   that authority.
7. After the repository transition, retrieve the integrated identity and
   preserve the promotion decision and provenance. Rejected, demoted,
   withdrawn, and superseded material retains its historical status under the
   existing staging and preservation guidance.

The human promotion decision may share a pull request with implementation when
the approval-identity rules in
[`review-packet.md`](review-packet.md#approval-identity-and-ownership) are
satisfied. It must state that the exact artifact is promoted and what reusable
guidance becomes authoritative; ordinary approval or merge without that record
is not doctrine promotion.

### Classification examples

| Proposed effect | Classification and trigger | Required path |
| --- | --- | --- |
| Correct spelling, links, or formatting without changing meaning | Non-material; no trigger | Proportional review, validation, and explicit human promotion when accepted doctrine changes |
| Clarify wording without changing required behavior, authority, ownership, or a lifecycle condition | Non-material; no trigger | Proportional review and explicit human promotion |
| Revise a reusable prompt template while preserving its semantic contract | Non-material; no trigger; prompt-contract approval and versioning rules still apply | Proportional review, applicable prompt-contract evidence, and explicit human promotion |
| Change executor-specific adapter behavior without changing an authority boundary, mandatory gate, or cross-executor contract | Non-material; no trigger | Proportional review and explicit human promotion |
| Change a shared validation or completion requirement | Material; mandatory lifecycle gate | Governed independent review, finding disposition, applicable re-review, and explicit human promotion |
| Change a human or AI authority boundary | Material; authority boundary | Governed independent review, finding disposition, applicable re-review, and explicit human promotion |
| Create or change a required obligation between repositories | Material; cross-boundary contract | Governed independent review, finding disposition, applicable re-review, and explicit human promotion |
| Transfer a semantic contract between Playbook canonical owners | Material; cross-boundary contract | Governed independent review, finding disposition, applicable re-review, and explicit human promotion |
| Add a lifecycle or approval gate | Material; mandatory lifecycle gate | Governed independent review, finding disposition, applicable re-review, and explicit human promotion |
| Promote an architecture foundation, or change an accepted Product or cross-repository architecture boundary | Material; architecture boundary | Governed independent review, finding disposition, applicable re-review, and explicit human promotion |
| Demote accepted doctrine to candidate guidance, withdraw it, or explicitly replace it with named superseding doctrine | Material; reverse doctrine transition | Governed independent review, finding disposition, applicable re-review, and explicit human decision |

An executor-adapter change becomes material if its actual effect crosses one of
the listed triggers. Likewise, merely mentioning several repositories is not a
cross-boundary contract change; the trigger applies only when the proposal
changes a required contract, canonical owner, or obligation among the listed
owners or implementation boundaries.

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

Proposal-first names the semantic decision boundary above, not a proposal
branch or pull-request topology. Apply
[`repo-readiness.md#current-phase-mutation-authority-and-proposal-surfaces`](repo-readiness.md#current-phase-mutation-authority-and-proposal-surfaces)
before choosing the artifact surface. Without repository-mutation authority for
the current phase, create no worktree, branch, commit, repository document, or
pull request; return a compact proposal in the active interaction or, when its
exact durable identity qualifies and storage admission passes, use the existing
governed-artifact route selected by its owner.

A proposal-only draft PR can still be a proportionate collaboration surface
when the human or a narrower owning workflow explicitly authorizes that
repository artifact for the current phase and repository policy permits it.
The exact proposal may then be approved on that branch and bounded
implementation may continue on the same branch and PR. Keep proposal approval
and final implementation review distinct: proposal approval authorizes only the
stated implementation, and merge still requires separate authorization against
the exact reviewed implementation head. Materiality or an independent-review
requirement does not itself choose the proposal PR. Do not use an empty commit
to represent or freeze revisions of a mutable pull-request description.

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

For questions about repository implementation, GitHub is the authoritative
hosted source unless repo-local guidance explicitly defines another owner.
GitHub issues, pull requests, closing keywords, hosted CI, hosted review state,
and merge state determine the corresponding hosted issue, pull request,
validation, review, and merge facts. Implementation may exist in an inspected
local worktree before it is represented on GitHub, so implementation existence
remains a repository-state question rather than a hosted-state inference.

Planning systems such as Linear own their planning facts, including intent,
acceptance context, assignment, sequencing, and planning status. They do not
override repository implementation state, just as GitHub merge state does not
silently rewrite the planning intent or sequencing that produced the work. The
same boundary applies to similar planning systems, mirrors, or boards.

Before work discovered during or after completion of a planning item begins,
classify it against the item's existing acceptance context and completion
boundary. This rule applies to research, design, audit, and other planning
work, whether or not the work uses a branch, pull request, or merge. Work still
required to satisfy that boundary remains in the current item, which stays
open. If the item was completed on a factually invalid or incomplete basis,
reopen it to correct that planning state; do not create a successor merely to
rename unfinished original work.

When the existing boundary was legitimately completed, preserve that
completion. New human direction after that completion, or a newly selected
outcome with a materially new completion boundary, requires an explicit
successor disposition in the live planning or authority surface appropriate to
the work before execution begins. Do not reopen or extend the completed item
merely because related work was discovered later.

A successor disposition is one of: tracked now, deferred, declined, or
intentionally untracked. A tracked-now disposition identifies a bounded
outcome, owner, completion boundary, and relationship to the completed item in
a live planning or authority record. Deferred retains an outcome for possible
later selection; declined rejects it from the current follow-through; and
intentionally untracked records that neither execution nor durable successor
tracking is selected. These are non-execution dispositions, none requires a
ticket solely for bookkeeping, and later execution requires a new live
tracked-now disposition. The authority and durable-continuity rules in
`core-model.md` still control: recommendation text or conversational
continuity does not create this disposition, and the mere existence or state
of repository implementation, an issue, a pull request, review, or merge does
not supply it. An explicitly selected and bounded repository issue may serve
as the live record where the repository workflow assigns it that role.

Use one tracked successor when one record can preserve a coherent outcome,
owner, completion boundary, acceptance, sequencing, validation, risk, and
timing without obscuring an independent decision or completion claim. Split
successors when divergence in any of those factors would obscure an
independent decision or completion claim. Do not create one ticket per finding
or microstep when one bounded successor or a non-execution disposition
preserves the necessary boundary.

Immediately before starting a tracked successor, re-read its live disposition
and current human authority. Unless both the live bounded record and current
human authority support the work, stop.

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

Residual risks and follow-ups belong in the review packet and PR notes. Apply
the discovered-work disposition rule above when work remains after merge; do
not hide unfinished required work behind a completed planning status.

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
