# Orchestration And Parallelism

Use this page when deciding whether a repo task should stay in one Codex
thread, split into multiple worker lanes, or pause for sequencing. The goal is
solo-operator leverage, not ceremony: parallelism is useful only when it keeps
work easier to review, validate, and merge.

## Distributed-Systems Lens For Multi-Agent Work

Treat multi-agent repository work like a small distributed system. The analogy
is operational, not literal: each worker has partial local state, can drift from
current truth, and may conflict with other workers unless ownership, source of
truth, validation, and reconciliation rules are explicit.

Use the lens to reinforce the existing rules:

- authoritative repo, provider, issue, PR, and documentation state controls over
  agent context, memory, pasted summaries, and prior-thread reports
- worker lanes need explicit ownership, scope, exclusions, and stop conditions
- overlapping writes require sequencing or reconciliation before mutation
- commands and validation should be rerunnable enough for safe retry
- the orchestrator or human owns coordination, merge order, and trust-boundary
  decisions
- worker implementation stops at the assigned lane unless further authority is
  explicitly granted
- canonical validation is the health check before readiness or reconciliation
- review, rebase, validation, and merge sequencing are the reconciliation path

The worker count, lane layout, execution engine, and sequencing topology may
change only while the approved semantics, authority boundaries, isolation,
evidence identity, and validation contract remain intact. A topology change is
not authority to reinterpret the task or weaken a guarantee.

For comparative discovery and synthesis across multiple agents, use
[`multi-agent-synthesis.md`](multi-agent-synthesis.md). Convergence and
divergence can guide what deserves inspection, but source verification and
human judgment still decide what becomes doctrine, planning, or implementation.

## Default To One Thread

Prefer single-thread Codex work when the task has one coherent review surface.
This is the default for most repository changes.

Single-thread work is usually right when:

- one person or agent can inspect the relevant sources and complete the change
  without losing context
- the change touches one repository, one branch, one validation path, and one
  pull request
- the work depends on a shared semantic decision that should be made once
- the affected files are tightly coupled, such as one function, one command,
  one schema contract, one generated artifact family, or one user-facing
  wording surface
- validation or review cost would not shrink meaningfully by splitting

Do not split work merely because several agents are available. If the split
would create coordination work larger than the task itself, keep the task in one
thread and ship the smallest coherent change. For PR packaging guidance in
solo-operator or low-coordination contexts, use
[`repo-readiness.md`](repo-readiness.md#solo-operator-iteration-economics).

## Fan Out Deliberately

Fan out only when the lanes can be bounded before workers start. A useful
parallel batch has independent deliverables, clear ownership, and a known
reconciliation path.

Parallel work is a good fit when:

- lanes can be separated by repository, issue, file family, behavior surface,
  or risk surface
- each lane can produce one branch, one worktree, one validation result, and
  one pull request or review artifact
- expected overlap is named before launch
- a merge or review order is declared before branch state changes
- workers can stop at PR readiness without needing to inspect or update other
  lanes
- the orchestrator or human can reconcile outputs sequentially

For same-repository Codex fan-out, use repo-local `.worktrees/` and keep each
worker on its own branch. One issue, one branch, one worktree, and one PR per
worker is the preferred shape when issues already describe the work cleanly.
When several lanes belong to one batch, a short lane prefix can make the local
state easier to scan, for example `.worktrees/lane-a-fixtures` and
`.worktrees/lane-b-provider-normalization`. Treat lane prefixes as a worked
example, not a required naming taxonomy.

## Worker Envelope

Every worker lane needs a self-contained task envelope. Do not rely on hidden
conversation history, implicit role inheritance, or broad instructions such as
"continue from the same context."

Prompts intended for delegated execution should name the expected deliverable
whenever practical, such as research findings, an audit report, a design
proposal, an implementation plan, an implementation, or an implementation that
results in a pull request. When delegated work will modify a repository, the
default expected deliverable is a reviewable pull request unless another
artifact is explicitly requested.

Every delegated repository implementation prompt must explicitly identify the
target repository, even when the repository appears obvious from the working
directory or conversational context. Repository identity is part of the task's
scope and authority boundary; do not leave it implicit or rely on inherited
context to supply it.

Include:

- repository and working directory
- interaction mode and expected deliverable
- assigned issue, branch, worktree, and file or behavior surface
- goal, scope, and explicit exclusions
- source evidence or retrieval instructions
- canonical validation path
- expected overlap and dependency-stop conditions
- whether to open a draft or ready-for-review PR
- reporting expectations: changed files, validation, overlap, blockers,
  residual risk, and any merge-order dependency

For material work that must support recovery or replay, give the execution a
durable attempt identity separate from the worker, model, or tool that performs
it. Preserve that identity with the applicable contract and input identities,
produced artifacts, receipts, and outcome. Execution engines are replaceable;
changing an engine does not create authority, erase an attempt, or make its
inputs current.

Workers should implement the assigned lane, run canonical validation, commit the
scoped change, open or prepare the requested PR surface, report evidence, and
stop. They should not merge, enable auto-merge, update other branches, absorb
unassigned issues, or decide the next lane unless the human explicitly grants
that authority for the specific step.

The worker's final report is the lane stop receipt. It should make the stop
boundary easy to audit by naming changed files, validation results, overlap or
merge-order dependencies, blockers, residual risk, and any authority it did not
exercise.

The lane stop receipt records what the lane reports at its boundary. It does
not grant downstream authority and does not replace direct inspection of the
repository, pull request, validation, or other controlling source.

## Live Process Lifecycle

Launching an executor creates a live process obligation. The controller must
assign an attempt identity, record the exact process and process-group identity
with a start-time discriminator, and await observed terminal state. A tool-call
timeout, quiet output, partial output, detached terminal, lost polling session,
or soft liveness threshold is not process completion. Do not abandon the live
attempt, declare it failed while it may still run, or launch an overlapping
replacement.

While the process is live, keep these states distinct:

- `running`: continue observing the same process, including after soft
  thresholds;
- `awaiting operator disposition`: preserve the process and ask whether to keep
  waiting or terminate when the interactive contract requires that choice;
- `termination authorized`: record the exact authority and send the declared
  graceful signal to the recorded process group;
- `force escalation authorized`: only after a separately declared grace period
  and separate authority, send the declared force signal; and
- `terminal`: record observed exit or signal state, capture output, complete
  postflight, and write the terminal receipt before any successor attempt.

Interactive cancellation requires a current human decision for that exact live
attempt. An unattended workflow may act only under a predeclared,
human-approved cancellation policy with exact emergency conditions, signal
sequence, grace interval, and escalation authority. A generic timeout or the
controller's desire to make progress is not such a policy. If an unauthorized
mutation is a declared emergency condition, the controller may invoke only the
preauthorized response and must still await terminal state and perform
postflight; detection does not erase the attempt.

Termination is an infrastructure outcome, not a candidate verdict. Record
whether a signal was requested, delivered, declined, ineffective, or escalated,
and do not classify provider guarantees from an operating-system exit code
alone. A terminated attempt is never an eligible transient retry unless the
governing contract explicitly says so. Telemetry and operator-progress
rendering may observe these states, but they do not define the lifecycle or
create authority.

## Orchestrator Responsibilities

The orchestrator owns the batch-level view. In a solo-operator workflow this is
often the human plus one top-level Codex thread.

Before fan-out, the orchestrator should:

- verify the repository and issue set
- select a small lane count, usually one to three lanes
- assign one bounded lane to each worker
- serialize shared setup such as fetching, branch creation, and worktree
  creation when needed
- name expected overlap and the intended merge order
- define stop conditions for dependency, validation, or scope surprises

For batches that may need replay, interruption recovery, or a fresh-thread
handoff, the orchestrator may write a short plan note before fan-out. The note
can record lanes, ownership, expected overlap, intended merge order, validation
paths, stop conditions, and human gates. Treat the note as planning evidence,
not as authority over current repository, issue, PR, or validation state.

After workers report, the orchestrator should:

- inspect worker diffs, PRs, and validation evidence directly
- preserve or revise the merge order before changing branch state
- decide which lanes can proceed, wait, or need reconciliation
- update or rebase branches sequentially when earlier merges affect later lanes
- resolve conflicts with semantic judgment, not mechanical cleanliness alone
- rerun canonical validation after each reconciliation update
- keep implementation records separate from staging or promotion notes

When a batch needs later replay, the orchestrator may keep append-only local
telemetry for lane lifecycle events, source-verification transitions, and
reconciliation notes. Treat this as optional operational context, not canonical
workflow state; see
[`orchestration-telemetry.md`](orchestration-telemetry.md).

A lightweight reconciliation log can serve the same purpose for human-readable
review decisions: append what changed in the merge order, which source was
checked, which validation result was used, and which human gate remains. The
log is evidence for recovery and review; workers and orchestrators must still
re-fetch current source state before acting.

## Recovery And Replay

Recovery is contract-scoped. Apply the canonical fresh, replay, receipt, and
checkpoint semantics in [`prompt-contracts.md`](prompt-contracts.md) when a
material prompt contract exists. A checkpoint is reusable only when the
semantic and operational contracts that created it, the authority available
now, the recorded inputs, and the referenced artifact identities still apply.
A stale checkpoint may explain prior work, but it cannot silently authorize new
work or move a workflow across a boundary.

Distinguish the execution mode:

- Fresh execution creates a new attempt under current authority, selects exact
  compatible inputs once before hydration, and keeps them immutable for that
  attempt.
- Replay reproduces a previously authorized attempt from its recorded contract
  and exact inputs. It must not read current mutable semantic sources,
  rediscover scope, recompute input selection, widen the work, reinterpret
  approval, silently upgrade dependencies, or acquire new authority.

Replay reproduces contract identity and authorized inputs, not deterministic
model output. If the recorded contract, pinned validation identity, exact
prompt bytes, or other inputs cannot be reconstructed faithfully, stop rather
than presenting a new execution as replay. A later attempt should state whether
it is fresh execution, replay, or a contract-valid continuation.

## Reconciliation And Merge Sequence

Parallel execution ends at lane readiness. Integration is a sequential workflow.

Use this sequence when lanes will be merged or reviewed together:

1. Inspect each PR or review surface directly.
2. Confirm or revise the merge order.
3. Merge or update the first lane only after explicit merge authorization when
   the workflow requires human approval.
4. Fetch current `main` before each later lane.
5. Update, rebase, or recreate later branches only as needed for conflicts,
   branch protection, repo policy, or explicit human request.
6. Rerun the repository's canonical validation entrypoint after each
   reconciliation update.
7. Re-check readiness before continuing to the next lane.
8. Run final validation on the integrated result when the repository workflow
   calls for it or when the batch changed shared behavior.

Open PRs as draft when they are ready for orchestrator inspection but not yet
ready to merge. Mark them ready only when the implementation is complete,
validation passes, and the remaining overlap or sequencing risk is low.

## When Not To Parallelize

Keep the work single-threaded or staged sequentially when:

- lanes share mutation paths, safety-critical behavior, release state, schema
  contracts, generated artifacts, or fragile overlapping files
- the task needs one unresolved product, policy, security, or semantic decision
- worker prompts would need large hidden context to behave correctly
- the validation surface is global and expensive enough that each lane cannot
  be checked meaningfully on its own
- merge order cannot be described before launch
- the likely reconciliation work would be harder than doing the change once
- the work is destructive, externally visible, permissions-sensitive, or
  governed by a human approval step

Report-only exploration may still run in parallel for ambiguous areas, but
mutation should wait until the split is clear.
