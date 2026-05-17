# Multi-Agent Synthesis

Use multi-agent synthesis when independent perspectives can reveal better
options than one agent would find alone. This is discovery and judgment support,
not automatic authority transfer.

## When To Use It

Multi-agent synthesis is appropriate when the work benefits from meaningfully
different perspectives, such as architecture review, backlog discovery,
workflow-risk analysis, repo-ecosystem scanning, or comparison of alternative
implementation strategies.

It is usually not worth the coordination cost when the task is a small coherent
implementation change, a direct bug fix, a tightly coupled edit, or a decision
that needs one source-grounded answer rather than multiple speculative views.

Use multiple agents to widen the idea surface. Use source inspection,
validation, and human judgment to decide what becomes work.

## Phase Boundaries

Keep these phases separate:

- idea generation: ask agents to inspect sources and propose opportunities,
  risks, or options
- synthesis: compare outputs for convergence, divergence, missing evidence, and
  unresolved assumptions
- execution planning: choose a bounded lane, owner, validation path, and stop
  condition
- implementation: make repository changes in the normal branch, worktree,
  validation, and PR flow

Do not let an agent-generated synthesis become the execution plan until a human
or orchestrator has verified the relevant sources and selected the next action.
Do not let a synthesis artifact become canonical merely because it is polished.

## Reading Convergence And Divergence

Convergence is a strong signal that a pattern, risk, or opportunity deserves
attention. It is not proof. Before promotion or implementation, verify the
claim against the authoritative source: repository files, current PRs, issues,
official provider documentation, validation output, or the relevant system of
record.

Divergence is useful evidence. Treat it as a signal of ambiguity, hidden
coupling, underspecified goals, stale context, model-specific bias, or
legitimate tradeoff space. The response should be reconciliation, source
verification, or a narrower decision prompt, not a vote-counting exercise.

Record unresolved divergence when it affects architecture, policy, execution
sequence, safety, or trust boundaries. Do not bury it in a blended summary.

## Promotion Readiness

Classify findings before moving them into durable workflow doctrine:

- experimental: interesting observation, but source evidence or repeatability is
  still weak
- candidate: plausible reusable pattern with named evidence gaps and promotion
  criteria
- evidence-supported: repeated source-verified examples show the pattern is
  useful beyond one run
- playbook-ready: generalized, repeatable, source-verified guidance that can be
  stated without raw experiment detail

Only promote playbook-ready findings into this repository. Keep raw experiment
logs, comparative model behavior, failed synthesis attempts, and evolving
heuristics in an incubator or staging repository until the durable rule is
clear.

## Human Checkpoints

Preserve human-in-the-loop checkpoints for:

- architectural decisions
- cross-repo policy or governance changes
- destructive, externally visible, credentialed, or permissions-sensitive work
- promotion from experiment to playbook doctrine
- reconciliation where agent outputs disagree about scope, risk, or sequencing

The human checkpoint should decide the next bounded action, not merely approve a
generated narrative.

## Solo-Operator Leverage

The goal is to reduce human bottlenecking without hiding decisions that still
need judgment. A useful synthesis should identify:

- safe autonomous lanes that can proceed with clear ownership, validation, and
  stop conditions
- decisions that need architectural review before mutation
- reconciliation needs between agent outputs or work lanes
- source evidence still missing before implementation or promotion
- follow-up that belongs in an incubator rather than the playbook

Use the playbook for generalized repeatable rules. Use an incubator for raw
experiment logs, comparative observations, synthesis notes, and promotion
candidates that need more proof.
