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
thread and ship the smallest coherent change.

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

## Worker Envelope

Every worker lane needs a self-contained task envelope. Do not rely on hidden
conversation history, implicit role inheritance, or broad instructions such as
"continue from the same context."

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

Workers should implement the assigned lane, run canonical validation, commit the
scoped change, open or prepare the requested PR surface, report evidence, and
stop. They should not merge, enable auto-merge, update other branches, absorb
unassigned issues, or decide the next lane unless the human explicitly grants
that authority for the specific step.

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
