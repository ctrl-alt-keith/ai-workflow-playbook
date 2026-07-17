# Start Here

## Purpose

This page is the routing entry point for AI-assisted repository work. Use it
to identify the governing docs, startup checks, and compact invariants before
acting.

## Read Order

- `docs/engineering-baseline.md` -> foundational engineering expectations
- `docs/source-first-retrieval.md` -> retrieve and revalidate authoritative
  state before stateful repository reasoning
- `docs/repo-readiness.md` -> interaction mode, governance operating model,
  command form, worktree, branch, validation, and PR expectations
- `docs/orchestration-and-parallelism.md` -> single-thread, worker fan-out,
  reconciliation, validation, and merge sequencing guidance
- `docs/multi-agent-synthesis.md` -> comparative discovery, convergence and
  divergence interpretation, and promotion boundaries
- `docs/tool-adapters/codex.md` -> required Codex-specific deltas for Codex
  executions
- `docs/tool-adapters/` -> adapter guidance for other executors when a
  matching adapter exists
- `docs/authoritative-source-check.md` -> advisory source scanner workflow
- `docs/repo-awareness-onboarding-refresh.md` -> repository inventory refresh
- `docs/prompts.md` -> reusable prompt templates

The ecosystem includes an autonomous maintenance layer for recurring, bounded
inspection, maintenance, and improvement. Its full doctrine is conditional;
ordinary repository work does not need to hydrate it unless the task touches
that layer.

## Conditional Guidance

Read these only when the work involves multiple repositories,
cross-repository interfaces, or architectural terminology:

- `docs/ai-workflow-ecosystem.md` -> repository roles, autonomous maintenance,
  state boundaries, and architectural direction
- `docs/repo-to-repo-interface-contracts.md` -> lightweight producer/consumer
  contract pattern for cross-repository interfaces
- `docs/cross-repo-glossary.md` -> qualified meanings for overloaded
  architecture terms across repositories

Read `docs/maintenance-automations.md` when work involves any of these surfaces:

- recurring automation design or review
- automation prompt authoring
- fleet-wide maintenance
- governance or drift automation
- scheduled inspection or correction
- architecture analysis of the autonomous maintenance layer
- changes to automation authority, evidence, scope, or safety contracts

Ordinary repository implementation, review, issue triage, and “what changed?”
work do not require the full maintenance doctrine unless the task also touches
one of those surfaces.

## Instruction Hierarchy

Repository work combines reusable workflow guidance with local execution
policy. Apply instructions in this order when they overlap:

1. The human's explicit task, plus any tool, safety, environment, or access
   constraints that govern the current run.
2. The target repository's repo-local `AGENTS.md` and other repo-local policy
   for repository-specific execution details.
3. The matching executor adapter, such as `docs/tool-adapters/codex.md` for
   Codex-specific behavior.
4. The shared playbook docs as global workflow defaults and reusable operating
   guidance.

Repo-local instructions are the authoritative source for repository-specific
policy: allowed tools, Git usage, validation path, file placement, release
posture, compliance notes, and other local execution constraints. When
repo-local instructions intentionally disable, narrow, or replace a global
default, follow the repo-local rule for that repository.

Before selecting a workflow, distinguish repository or workspace purpose from
interaction mode. Purpose describes what kind of workspace this is:
implementation, documentation, research, planning, leadership, knowledge
management, experimentation, enforcement, tooling, or a mix of those surfaces.
Interaction mode describes what kind of work the agent is doing there:
implementing, reviewing, auditing, planning, advising, orchestrating, or
authoring prompts.

Purpose and mode are related, but they are not the same. A documentation
repository can have a review or audit task. An implementation repository can
have a planning task. A leadership workspace can have a prompt-authoring task.
A tooling repository can have an implementation task. Use both purpose and
mode to choose the appropriate validation, review, inspection, Git, PR, or
non-Git workflow from repo-local policy and the interaction mode.

If instructions appear to conflict, resolve them by authority and specificity:
use the narrowest applicable instruction from the strongest source. If the
conflict cannot be resolved safely from the available sources, stop and report
the conflict instead of silently choosing a side. Do not edit repo-local
`AGENTS.md` merely to reconcile the conflict unless that edit is explicitly in
scope.

When following repo-local policy causes a significant deviation from the normal
playbook workflow, explain it briefly. Significant deviations include skipping
Git or PR workflow, using inspection-based validation, avoiding a normal
validation command, changing worktree or branch behavior, or treating a
repository as documentation, research, planning, leadership, or other non-code
work rather than implementation code.

## Required Startup Contract

Before repository-scoped work, including code, documentation, research,
planning, leadership, read-only review, audit, advisory,
architecture/workflow analysis, PR/issue/branch recommendations, and "what
changed?" or "what should we do next?" requests:

1. Read this page.
2. Read the target repository's repo-local `AGENTS.md`.
3. Apply the matching executor adapter. Codex runs must apply
   `docs/tool-adapters/codex.md`.
4. Identify the repository or workspace's primary purpose.
5. Select the interaction mode from `docs/repo-readiness.md`: implementation,
   review/audit, or orchestration/prompt-authoring.
6. Use the purpose and mode to choose the appropriate workflow path.
7. Identify the canonical source for the rule, behavior, or state being used.
8. For policy-sensitive changes, apply the repo-family alignment check in
   `docs/repo-readiness.md`.
9. Confirm command form and execution settings for planned repository commands,
   if commands are needed.
10. Identify the repository's canonical validation, review, or inspection path.
11. Act only after those checks are clear, or report the blocker, uncertainty,
   or missing context.

## Required Core Invariants

- `ai-workflow-playbook` is the canonical source for reusable workflow rules.
- `AGENTS.md` is the repo-local execution layer. Repo-local rules override
  shared playbook defaults for repo-specific behavior.
- Playbook changes and `AGENTS.md` edits are separate work types. Edit
  `AGENTS.md` only with explicit authorization or when the task's primary
  purpose is an `AGENTS.md` update, rollout, or enforcement.
- Deterministic repository triggers run before conversational interpretation:
  retrieve or revalidate authoritative source state before claims about current
  PRs, issues, branches, commits, CI, validation, files, runtime state, or
  external provider/API behavior.
- Advisory summaries, generated snapshots, staged notes, memory, pasted
  descriptions, and conversational context can help find what to inspect. They
  are not proof of current repository state.
- If referenced repository state was not directly verified, state
  `unknown → referenced repo state was not verified` before answering from
  that state.
- When retrieval was missed and remains available, recovery starts by doing
  the missed retrieval or revalidation, then correcting or marking prior
  assumptions as unverified.
- If the human asks for a concrete operational action and the needed tools and
  context are available, do the action before discussing workflow intent,
  philosophy, or speculative improvements.
- Only documented adapter files under `docs/tool-adapters/` are authoritative
  for executor-specific workflow behavior.
- Incubation, staging, runtime artifacts, generated snapshots, copied custom
  instructions, local workspace instructions, and temporary operational notes
  are noncanonical unless a durable rule is explicitly promoted into the
  playbook.

## Defaults And Recommendations

- Prefer small, scoped changes.
- Keep changes in the target repository, branch, and worktree.
- Follow `docs/repo-readiness.md` for implementation isolation, governance
  operating model, command form, interaction mode, validation, and PR readiness.
- Treat Git, branch, worktree, validation, and PR guidance as implementation
  defaults when the repository's policy and task type support them; do not
  force those workflows onto repositories that intentionally use another
  operating model.
- Use `docs/orchestration-and-parallelism.md` before splitting a task across
  workers or parallel PR lanes.
- Use `docs/multi-agent-synthesis.md` before treating independent agent outputs
  as promotion, planning, or implementation evidence.
- Open PRs ready for review by default when repo-local guidance calls for PR
  delivery and validation is complete.
