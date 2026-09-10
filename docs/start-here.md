# Start Here

## Purpose

Route work whose evidence, authority, review, or completion boundaries materially
affect its outcome. Ordinary chat, brainstorming, and conceptual discussion need no
startup or live retrieval unless the answer depends on current external state.

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

Apply the core model's
[`Operator Observability`](core-model.md#operator-observability) guidance when
an execution-state transition materially affects human review, workflow
authority, or subsequent behavior.

### Global bootstrap persistence

Bootstrap before the first project action and when the task/repository
materially changes. At that trigger, applying this contract is a hard
precondition: do not respond, reason about the task, or invoke another tool
first.

After successful bootstrap, reuse still-current repository operating mode and
verified sources. A response, reasoning step, follow-up, tool call, or elapsed
turn alone does not restart bootstrap. Apply [active bounded-task continuity](core-model.md#active-bounded-task-continuity)
before treating a strongly unrelated instruction as a task change. Re-route
when repository, interaction mode, workflow, authoritative-source requirements,
execution locality, or authority boundary materially changes.

The [global-bootstrap distribution](../distributions/global-bootstrap/README.md)
owns copy-ready provider projections and the read-only drift check. Repo-local
instruction files remain independent; do not copy the global router into them.

### Connector availability is runtime evidence

Hydration establishes repository context, not connector capability. Before
claiming a connector, integration, or action is unavailable, inspect current
actions or attempt the relevant operation. Do not infer availability from memory
or hydration.

Reuse successful current-context capability evidence without rediscovery or
re-probing. Recheck only after failure, identity/connection change, a materially
different required capability, or provider-reported drift. Success of one action
does not establish another action's availability.

## Canonical Ownership

- [`core-model.md`](core-model.md) owns domain-independent operating principles,
  human and AI roles, authority, semantic phase boundaries, and durable
  continuity.
- [`product-status.md`](product-status.md) owns the current accepted Product
  status for each identity it lists. Records under
  [`product-promotion-decisions/`](product-promotion-decisions/) own durable
  provenance for the distinct human governance events that established those
  states.
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

For a workflow symptom or intended fix, the compact
[change-routing map](change-routing.md) connects canonical doctrine to the
implementation surface and nearby wrong layers to avoid.

Use only the routes activated by the task:

- **Repository or software work:** continue with
  [Repository Workflow](#repository-workflow) below.
- **Current accepted Product status:** use
  [`product-status.md`](product-status.md); use records under
  [`product-promotion-decisions/`](product-promotion-decisions/) for the
  distinct human governance events that established those states.
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
  adapter exists; Codex runs must read `docs/tool-adapters/codex.md`, Claude
  runs must read `docs/tool-adapters/claude.md`, and repository-scoped
  ChatGPT runs must read `docs/tool-adapters/chatgpt.md`
- `docs/engineering-baseline.md` -> foundational engineering expectations
- `docs/source-first-retrieval.md` -> repository triggers, retrieval ordering,
  verification gates, and recovery
- `docs/repo-readiness.md` -> interaction mode, governance operating model,
  workflow-state ownership and lifecycle, command form, worktree, branch,
  validation, and PR expectations
- `docs/orchestration-and-parallelism.md` -> single-thread, worker fan-out,
  reconciliation, validation, and merge sequencing guidance
- `docs/multi-agent-synthesis.md` -> comparative discovery, convergence and
  divergence interpretation, and promotion boundaries
- `docs/authoritative-source-check.md` -> advisory source scanner workflow
- `docs/repo-awareness-onboarding-refresh.md` -> repository inventory refresh
- `docs/prompt-contracts.md` -> canonical semantics for hydrated, rendered,
  delivered, fresh, and replayed material prompts
- `docs/prompts.md` -> reusable prompt templates

This is the ordered universe of potential startup sources, not a full-read
requirement. Before governed planning or action, read the required repository
floor, matching executor adapter, and documents activated by
[Task Routing](#task-routing),
[Conditional Repository Guidance](#conditional-repository-guidance), or a
narrower owner trigger, in the order above. Advisory documents govern only
their specialized actions. Do not load unactivated maintenance,
cross-repository, prompt-contract, or multi-agent guidance.

### Repository Instruction Hierarchy

Resolve overlapping instructions by authority, then specificity:

1. Explicit human task and governing tool, safety, environment, and access
   constraints.
2. Target repo-local `AGENTS.md` and policy for repository execution details.
3. Matching executor adapter.
4. Shared Playbook defaults.

Repo-local policy controls allowed tools, Git, validation, placement, release,
compliance, and intentional local overrides. Apply the narrowest applicable
instruction from the strongest source. Stop and report an unresolved conflict;
do not edit `AGENTS.md` to resolve it unless explicitly authorized or that edit
is the primary task.

Distinguish workspace purpose from interaction mode before choosing workflow.
Briefly explain significant local deviations, such as non-Git delivery,
inspection-only validation, or different worktree behavior.

### Required Repository Startup Contract

Before repository-scoped code, documentation, research, planning, leadership,
read-only review, audit, advice, architecture/workflow analysis, PR or issue
recommendations, and "what changed?" or "what next?" requests:

1. Read this page, `docs/core-model.md`, and
   `docs/engineering-baseline.md`.
2. Read the target repository's repo-local `AGENTS.md`.
3. Apply the matching executor adapter. Codex runs must apply
   `docs/tool-adapters/codex.md`; Claude runs must apply
   `docs/tool-adapters/claude.md`; repository-scoped ChatGPT runs must apply
   `docs/tool-adapters/chatgpt.md`.
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

Controller-owned context sufficiency is determined from canonical routing for
the current task. The controller or other workflow owner must establish that
the repository floor and every activated document are present; a child or
delegated worker's own selection or belief that it has enough context cannot
establish sufficiency.

### Required Repository Invariants

- `ai-workflow-playbook` is the canonical source for reusable workflow rules.
- Successful repository hydration is a mode transition, not only an
  information-retrieval event. After the required repository startup contract
  succeeds, repository operating mode remains active for the rest of the
  repository work. Plans, reviews, implementation prompts, validation
  summaries, completion reports, and other artifacts must continue to use the
  repository-native conventions established by the governing repository
  sources without requiring the human to restate them. This invariant does not
  freeze a specific template or layout; the canonical artifact conventions may
  evolve. Repository operating mode ends only when the interaction clearly
  leaves repository work or the human explicitly requests a different artifact
  style. Moving to another repository requires applying that repository's
  startup contract before assuming its native conventions.
- Repository operating-mode persistence does not freeze the task-specific
  activated source set. When a task materially changes interaction mode,
  artifact type, workflow, authoritative-source requirements, execution
  locality, target executor, or authority boundary, re-evaluate activation
  routing and compare the changed task's required-source set with the currently
  activated set. Reuse the still-current repository floor and owners, retrieve
  only newly required owners before answering, planning, drafting, or acting,
  and do not blanket-rehydrate ordinary follow-ups. If a newly required owner
  cannot be retrieved, fail closed for the affected conclusion or artifact;
  memory, summaries, and convenient examples are not substitutes.
- Activation and application are separate stages. Successfully retrieving an
  owner does not prove its contract was applied. Validate the resulting
  behavior against the activated contract, and if a later prerequisite blocks
  the preferred path, preserve the owner's failure, fallback, or presentation
  contract rather than degrading into unconstrained prose.
- `docs/prompt-contracts.md` owns shared prompt-contract meaning; implementing
  repositories own operational schemas, hydration, rendering, receipts, and
  validation code.
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
recurring automation design or review, execution-locality classification,
automation prompt authoring, fleet-wide maintenance, governance or drift
automation, scheduled inspection or correction, autonomous-maintenance
architecture, or automation authority, evidence, scope, and safety contracts.

Read `docs/feature-lifecycle.md` when the current authorized action first enters
feature-delivery planning or execution; use its activation boundary to
distinguish intent, prerequisite workflow ownership, and implementation
eligibility.

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
- Select draft or ready status through
  [PR Readiness](repo-readiness.md#pr-readiness).
