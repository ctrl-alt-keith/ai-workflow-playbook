# Start Here

## Purpose

This page is the compact routing entry point for AI-assisted work whose
evidence, authority, review, or completion boundaries materially affect the
outcome. It identifies the general operating model first, then routes into the
workflow and domain guidance the task actually needs.

Ordinary chat, brainstorming, and conceptual discussion do not require this
startup contract or live source retrieval unless the answer depends on current
external state.

## Startup Contract

Before acting on work whose evidence, authority, review, or completion
boundaries materially affect the outcome:

1. Read the domain-independent operating principles and role boundaries in
   [`core-model.md`](core-model.md).
2. Define the intended outcome, scope, constraints, and completion boundary.
3. Identify the sources that control the relevant facts, instructions,
   ownership, and authority. Retrieve current state when the task depends on
   it; use recollection and summaries only for navigation.
4. Resolve overlapping instructions by authority and specificity. If a
   conflict cannot be resolved safely, stop and report it.
5. Select only the workflow guidance triggered by the task. Keep the path
   proportional to ambiguity, risk, authority sensitivity, and reversibility.
6. Hold a decision boundary before consequential execution when those factors
   warrant design, review, or approval separation.
7. Validate or verify the claims and effects that the outcome will rely on.
8. After consequential change, retrieve the resulting state and reconcile any
   separately owned system only when its workflow requires it.

Keep the current phase and next permitted action legible when they affect human
review or workflow authority. This is observable workflow state, not a request
for private reasoning or a universal phase machine.

### Connector availability is runtime evidence

Repository hydration and connector availability answer different questions.
Hydration retrieves repository instructions and state to establish working
context. Connector availability describes a current runtime capability.
Completing hydration neither proves nor disproves that a connector or action is
available, and it does not authorize assumptions about runtime connector state.

Treat connector availability as runtime evidence, not memory. Before stating
that a connector is unavailable, an integration is not connected, an action
cannot be performed because of connector availability, or any equivalent
claim, do one of the following:

1. Inspect the connector actions currently available.
2. Attempt the relevant connector operation.

Never explain inability to perform an operation by speculating about connector
availability. A successful connector invocation in the current conversation is
positive evidence that the connector remains available; successful use of a
specific capability is positive evidence that the capability remains
available. Do not contradict that evidence unless a subsequent connector
inspection or invocation demonstrates otherwise. Prior use of a different
action does not establish that a requested read or write capability exists, so
inspect or attempt the relevant operation before reaching that conclusion.

## Canonical Ownership

- [`core-model.md`](core-model.md) owns domain-independent operating principles,
  human and AI roles, authority, semantic phase boundaries, and durable
  continuity.
- Keep mechanisms with their narrowest canonical owner. A general principle
  should route to specialized workflow or domain guidance rather than copy its
  trigger lists, taxonomies, schemas, or execution procedures. Do not
  generalize domain mechanics merely because an analogy exists elsewhere.
- Domain and provider guidance owns concrete implementation. Repository Git,
  worktree, branch, validation, pull request, and planning-system behavior is a
  repository workflow, not a universal AI requirement.
- Tool adapters map shared guidance to an executor. They do not redefine the
  operating model.
- Repo-local `AGENTS.md` owns repository-specific execution policy and may
  narrow shared defaults for that repository.

## Task Routing

Use only the routes activated by the task:

- **Repository or software work:** continue with
  [Repository Workflow](#repository-workflow) below.
- **Evidence acceptance, integration, synthesis, or reporting:** use
  [`evidence-lifecycle.md`](evidence-lifecycle.md).
- **Material prompt review, recovery, or replay:** use
  [`prompt-contracts.md`](prompt-contracts.md).
- **Worker fan-out or orchestration:** use
  [`orchestration-and-parallelism.md`](orchestration-and-parallelism.md); use
  [`multi-agent-synthesis.md`](multi-agent-synthesis.md) for comparative
  discovery and synthesis.
- **Independent artifact review:** use
  [`external-ai-reviewer.md`](external-ai-reviewer.md) and the finding
  disposition contract in [`review-packet.md`](review-packet.md).
- **Cross-repository interfaces or architectural terminology:** use
  [`ai-workflow-ecosystem.md`](ai-workflow-ecosystem.md),
  [`repo-to-repo-interface-contracts.md`](repo-to-repo-interface-contracts.md),
  and [`cross-repo-glossary.md`](cross-repo-glossary.md) as applicable.
- **Recurring maintenance or governance automation:** use
  [`maintenance-automations.md`](maintenance-automations.md).
- **Reusable prompts and task envelopes:** use
  [`prompts.md`](prompts.md) after the governing workflow is clear.

## Repository Workflow

Repository work is one implementation domain for the general operating
principles. Apply the complete repository startup contract before repository-
scoped analysis, review, planning, advice, prompting, or mutation.

### Repository Read Order

- `docs/core-model.md` -> general operating principles and roles
- the target repository's `AGENTS.md` -> repo-local execution authority
- `docs/tool-adapters/<executor>.md` -> executor-specific deltas when a matching
  adapter exists; Codex runs must read `docs/tool-adapters/codex.md` and Claude
  runs must read `docs/tool-adapters/claude.md`
- `docs/engineering-baseline.md` -> foundational engineering expectations
- `docs/source-first-retrieval.md` -> repository triggers, retrieval ordering,
  verification gates, and recovery
- `docs/repo-readiness.md` -> interaction mode, governance operating model,
  command form, worktree, branch, validation, and PR expectations
- `docs/orchestration-and-parallelism.md` -> single-thread, worker fan-out,
  reconciliation, validation, and merge sequencing guidance
- `docs/multi-agent-synthesis.md` -> comparative discovery, convergence and
  divergence interpretation, and promotion boundaries
- `docs/authoritative-source-check.md` -> advisory source scanner workflow
- `docs/repo-awareness-onboarding-refresh.md` -> repository inventory refresh
- `docs/prompt-contracts.md` -> canonical semantics for versioned, hydrated,
  rendered, delivered, fresh, and replayed material prompts
- `docs/prompts.md` -> reusable prompt templates

The list is the baseline repository startup route. Additional documents remain
outside this baseline and load only when conditional routing activates them.
Do not load full maintenance, cross-repository, prompt-contract, or multi-agent
doctrine into an ordinary single-repository task that does not touch those
surfaces.

### Repository Instruction Hierarchy

Apply overlapping repository instructions in this order:

1. The human's explicit task, plus tool, safety, environment, and access
   constraints governing the run.
2. The target repository's repo-local `AGENTS.md` and other repo-local policy
   for repository-specific execution details.
3. The matching executor adapter, such as `docs/tool-adapters/codex.md` for
   Codex-specific behavior.
4. Shared Playbook docs as reusable workflow defaults.

Repo-local instructions are authoritative for allowed tools, Git usage,
validation, file placement, release posture, compliance notes, and other local
execution constraints. When repo-local policy intentionally disables, narrows,
or replaces a shared default, follow the repo-local rule for that repository.

Before selecting a workflow, distinguish repository or workspace purpose from
interaction mode. Purpose describes the workspace; interaction mode describes
whether the current task is implementation, review/audit, or
orchestration/prompt-authoring. Use both to select validation, review,
inspection, Git, PR, or non-Git behavior.

If instructions appear to conflict, use the narrowest applicable instruction
from the strongest source. If the conflict cannot be resolved safely, stop and
report it instead of silently choosing a side. Do not edit repo-local
`AGENTS.md` merely to reconcile the conflict unless that edit is explicitly in
scope.

When repo-local policy significantly changes the normal repository workflow,
explain the deviation briefly. Examples include skipping Git or PR delivery,
using inspection-only validation, changing worktree or branch behavior, or
treating the repository as a non-implementation workspace.

### Required Repository Startup Contract

Before repository-scoped code, documentation, research, planning, leadership,
read-only review, audit, advice, architecture/workflow analysis, PR or issue
recommendations, and "what changed?" or "what next?" requests:

1. Read this page and `docs/core-model.md`.
2. Read the target repository's repo-local `AGENTS.md`.
3. Apply the matching executor adapter. Codex runs must apply
   `docs/tool-adapters/codex.md`; Claude runs must apply
   `docs/tool-adapters/claude.md`.
4. Identify the repository or workspace's primary purpose.
5. Select the interaction mode from `docs/repo-readiness.md`: implementation,
   review/audit, or orchestration/prompt-authoring.
6. Identify the canonical source for the rule, behavior, or state being used.
7. Apply `docs/source-first-retrieval.md` before stateful repository reasoning.
   When connector capability matters, apply
   [Connector availability is runtime evidence](#connector-availability-is-runtime-evidence)
   without changing repository hydration or instruction discovery.
8. For policy-sensitive changes, apply the repo-family alignment check in
   `docs/repo-readiness.md`.
9. Confirm command form and execution settings for planned commands.
10. Identify the canonical validation, review, or inspection path.
11. Act only after these checks are clear, or report the blocker, uncertainty,
    capability gap, or missing context.

### Required Repository Invariants

- `ai-workflow-playbook` is the canonical source for reusable workflow rules.
- `docs/prompt-contracts.md` and its versioned machine-readable companions own
  shared prompt-contract meaning; implementing repositories own operational
  schemas, hydration, rendering, receipts, and validation code.
- Repo-local `AGENTS.md` is the repository execution layer. Playbook changes
  and `AGENTS.md` edits are separate work types; edit `AGENTS.md` only with
  explicit authorization or when that update is the task's primary purpose.
- Deterministic repository triggers run before conversational interpretation.
  Apply `docs/source-first-retrieval.md`; summaries, snapshots, memory, pasted
  descriptions, and generated notes are navigation rather than proof of
  current repository state.
- When referenced repository state was not directly verified, state
  `unknown → referenced repo state was not verified`. If retrieval was missed
  and remains available, recover by performing it and correcting or marking
  prior assumptions as unverified.
- If the human asks for a concrete operational action and the required tools,
  authority, and context are available, perform it before discussing
  speculative workflow improvements.
- Only documented files under `docs/tool-adapters/` are authoritative for
  executor-specific workflow behavior.
- Incubation, staging, runtime artifacts, generated snapshots, copied custom
  instructions, local workspace instructions, and temporary operational notes
  are noncanonical unless deliberately promoted into the Playbook.

### Conditional Repository Guidance

Read `docs/maintenance-automations.md` only when repository work touches
recurring automation design or review, automation prompt authoring, fleet-wide
maintenance, governance or drift automation, scheduled inspection or
correction, autonomous-maintenance architecture, or automation authority,
evidence, scope, and safety contracts.

Read `docs/ai-workflow-ecosystem.md`,
`docs/repo-to-repo-interface-contracts.md`, and
`docs/cross-repo-glossary.md` only when the work involves multiple
repositories, cross-repository interfaces, or architectural terminology.

Ordinary repository implementation, review, issue triage, and "what changed?"
work do not require those specialized documents unless their triggers also
apply.

### Repository Defaults

- Prefer small, scoped changes in the target repository, branch, and worktree.
- Follow `docs/repo-readiness.md` for interaction mode, command form,
  implementation isolation, validation, governance, and PR readiness.
- Treat Git, branch, worktree, validation, and PR guidance as repository
  implementation defaults only when repo policy and task type support them.
- Use `docs/orchestration-and-parallelism.md` before splitting work across
  workers or parallel PR lanes.
- Use `docs/multi-agent-synthesis.md` before treating independent agent output
  as promotion, planning, or implementation evidence.
- Open PRs ready for review by default when repo-local guidance calls for PR
  delivery and validation is complete; use draft status when the human or
  workflow explicitly requires an early review surface.
