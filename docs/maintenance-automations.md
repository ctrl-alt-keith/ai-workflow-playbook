# Autonomous Maintenance Layer

## Purpose

The **autonomous maintenance layer** is the ecosystem capability that performs
recurring, bounded inspection, maintenance, and improvement across otherwise
independent repositories. It shortens the half-life of repository entropy by
turning drift and maintenance needs into durable evidence, reversible hygiene,
or review-ready proposals.

This layer is part of the ecosystem architecture, not merely a scheduler
convenience. Without it, independently owned repositories tend to diverge from
canonical doctrine, governance, documentation, workflow, and configuration
expectations between human review cycles.

The governed term is **autonomous maintenance layer**. “Autonomous” describes
recurring execution within a bounded authority envelope. It does not mean
unrestricted operation or authority to cross consequential approval boundaries.

## Architectural Position

The layer closes a continuous feedback loop:

```text
Canonical doctrine and contracts
        ↓
Human and AI executors
        ↓
Autonomous repositories
        ↓
Autonomous maintenance layer
        ↓
Evidence and review-ready proposals
        ↓
Human approval for consequential transitions
```

Doctrine and contracts define expected behavior. Executors perform explicit
work. Repositories retain local authority over implementation, validation, and
change acceptance. The autonomous maintenance layer periodically checks those
surfaces, performs only work within its declared authority, and returns
inspectable evidence to repository and human review paths.

The feedback loop is architectural even when its scheduler, runtime, prompts,
tools, and cadence vary by machine or operator.

## Responsibilities And Non-Responsibilities

The autonomous maintenance layer owns:

- recurring inspection for doctrine, governance, documentation, workflow,
  configuration, repository-scope, and automation drift
- bounded maintenance whose safety predicates and stop conditions are explicit
- focused improvement proposals when a repository has a high-leverage gap
- durable evidence for findings, actions, validation, skips, and uncertainty
- review-ready repository changes when correction is authorized
- periodic review of the maintenance layer itself

It does not own:

- canonical doctrine, repository-local policy, or producer/consumer semantics
- a repository's implementation decisions, validation contract, or acceptance
  decision
- silent correction of ambiguous state
- merge, release, publication, migration, credential, permission, or other
  consequential transitions without explicit human authorization
- a standing mandate to normalize every repository or eliminate intentional
  differences
- the live scheduler inventory or machine-specific runtime configuration

Recurring findings can reveal a missing or unclear canonical contract. The
layer should report that pattern for doctrine or contract work rather than
repairing the same symptom indefinitely or promoting its own prompt into
shadow canon.

## Capability Model

Describe maintenance capabilities by purpose and cadence class. The categories
below are architectural capability families, not a permanent inventory of
individual jobs.

### Periodic Inspection And Drift Detection

Inspection capabilities compare current source state with an owning contract or
policy and produce findings without assuming correction authority. Typical
purposes include:

- identifying oversized operational memory and proposing compact replacements
  without silently rewriting retained state
- detecting drift in repository guidance, canonical doctrine, governance,
  documentation, workflows, configuration, provider-facing policy, and
  repository inventory
- comparing staging or experimental guidance with canonical sources
- reviewing the automation fleet for accidental divergence while preserving
  intentional specialization

Inspection is normally read-only. A finding should identify the checked source,
expected authority, observed difference, scope, and any skipped or unknown
state.

### Periodic Repository Maintenance

Maintenance capabilities reduce known entropy while preserving repository
behavior and authority. Typical purposes include:

- removing branches only when the owning cleanup contract proves they are safe
  to delete, while escalating ambiguous ancestry or ownership
- reconciling documentation with verified implemented behavior
- removing obsolete or redundant code, configuration, dependencies, scripts,
  examples, and documentation when deletion is demonstrably safe

Maintenance may produce a review-ready change or perform narrowly bounded,
reversible hygiene. It must stop when safety depends on interpretation,
unverified state, or a broader product decision.

### Periodic Engineering Investment

Investment capabilities look for one focused improvement rather than broad
repository redesign. Typical purposes include:

- selecting and implementing one high-leverage improvement per active
  repository
- identifying the most valuable test gap and preparing a focused correction
- running exhaustive, stress, or chaos-oriented validation where the
  repository's risk and validation contract justify recurring verification

These capabilities do not create an evergreen backlog mandate. Each run must
justify its selected scope against current repository evidence and leave
unselected opportunities as findings rather than absorbing them into the same
change.

## Authority And Evidence Classes

Every recurring capability declares one of these authority classes before it
runs:

- **Observe and report**: read current sources and produce findings. Evidence
  identifies inspected sources, tested refs or versions when relevant, scope,
  results, skips, unknowns, and failures. No repository or hosted state changes.
- **Propose review-ready changes**: create a bounded branch and pull request.
  Evidence includes the diff, rationale, canonical validation result, residual
  risk, and any source uncertainty. Human review remains the acceptance and
  merge boundary.
- **Perform reversible hygiene**: execute only an explicitly documented,
  narrowly scoped operation whose safety predicates can be verified before
  mutation. Evidence records the predicate, action, outcome, and preserved or
  escalated cases. Ambiguity causes a skip, not a guessed correction.

No class silently crosses an irreversible or consequential approval boundary.
An automation that needs broader authority must stop and return evidence for a
separate human-authorized action.

Evidence should live in the owning repository's normal review surface when a
repository change is proposed. Report-only or cross-repository runs should use
the workspace's designated durable operational-record location. Runtime output
paths and notification routing remain local configuration.

## Repository Autonomy

The layer preserves repository autonomy by applying shared expectations through
each repository's own authority surfaces:

- repo-local `AGENTS.md` controls repository-specific execution
- the repository's canonical validation command controls local readiness
- each change remains one repository, one branch, one worktree, and one pull
  request when that workflow applies
- repository owners and human reviewers decide whether a proposal is accepted
- intentional local differences remain valid when they are explicit and do not
  violate a governing cross-repository contract

Cross-repository inspection may enumerate and compare repositories, but
mutation must remain decomposed into independently reviewable repository
changes. The layer coordinates convergence; it does not turn the fleet into one
shared working tree or centralized implementation.

## Shared Evolution Versus Shared Implementation

Recurring maintenance changes the economics of duplication because it can keep
small conventions, documentation, governance, and bounded implementation
patterns aligned across repositories. This can make independent implementations
cheaper to operate when their ownership and validation need to remain local.

That benefit has limits:

- semantic integration seams still require explicit owners, versioned
  contracts when compatibility must be negotiated, and producer/consumer
  validation
- automation is not a substitute for an interface contract
- similar code in multiple repositories does not automatically justify a
  shared library
- recurring repair is not evidence that drift is harmless

Choose a shared library only when stable shared semantics, centralized
ownership, compatibility needs, or maintenance economics justify the added
coupling. Keep implementations independent when repository-local ownership,
release cadence, failure isolation, or small surface area is more valuable and
recurring convergence can keep the bounded pattern aligned.

If the same finding repeatedly crosses a semantic boundary, requires coordinated
releases, or risks incompatible producer/consumer behavior, recurring
convergence is insufficient. Define or strengthen the formal cross-repository
contract instead; see
[`repo-to-repo-interface-contracts.md`](repo-to-repo-interface-contracts.md).

## Architecture Versus Local Configuration

Canonical playbook doctrine owns:

- the existence and purpose of the autonomous maintenance layer
- its responsibility and non-responsibility boundaries
- its authority classes, stop conditions, and evidence contract
- its relationship to doctrine, executors, repositories, contracts, and human
  approval
- its self-review and drift expectations

Local operational configuration owns unless a later, explicit contract promotes
a detail:

- exact execution times and weekdays
- scheduler product and execution runtime
- workstation paths and machine-specific credentials
- local automation identifiers
- notification routing
- per-machine concurrency settings
- the enabled job inventory, exact prompt content, and runtime history

Active local configuration is authoritative for live inventory, schedules,
enablement, runtime prompts, paths, and operator-controlled fields. It is not
canonical doctrine. Canonical docs should describe capability purposes and
safety contracts rather than mirror runtime configuration.

## Maintenance-Layer Health

The autonomous maintenance layer can drift and therefore requires its own
periodic review. Inspect for:

- overlapping or contradictory responsibilities
- duplicated checks whose semantics have diverged
- stale assumptions about repository scope or ownership
- accidental coupling to one scheduler, workstation, or execution order
- authority creep or weakened stop conditions
- recurring findings that indicate a missing canonical contract
- automations that repeatedly edit the same surfaces or undo one another
- capability gaps that leave important doctrine or repository risks unchecked

Preserve intentional differences between read-only inspection, proposal work,
reversible hygiene, and repository-specific validation. The goal is coherent
coverage, not identical prompts or implementations.

Health review may recommend consolidating responsibilities, clarifying a
canonical contract, retiring stale capabilities, or changing local runtime
configuration. Changes to doctrine or repository state still follow their
normal review paths.

## Operating Contract

- Retrieve authoritative repository, provider, contract, and runtime state
  before classifying drift or acting.
- Declare scope, authority class, safety predicates, stop conditions, and
  evidence destination before mutation.
- Invoke an owning module, CLI, workflow, or validation entrypoint directly
  when one already defines the behavior. Orchestration may enumerate targets,
  invoke canonical commands, and collate results; it must not fork semantics.
- Treat skipped, inaccessible, stale, and ambiguous state as reportable results,
  not clean passes.
- Keep report-only work read-only and proposal work review-ready.
- Preserve human approval for consequential or irreversible transitions.
- Revisit repository scope through the repository-awareness procedure instead
  of treating a local filesystem or stale allowlist as authoritative; see
  [`repo-awareness-onboarding-refresh.md`](repo-awareness-onboarding-refresh.md).
- Do not let recurring automation replace canonical validation, pull-request
  review, explicit interface contracts, or repository-local authority.

## Relationship To Other Guidance

- [`ai-workflow-ecosystem.md`](ai-workflow-ecosystem.md) places the layer in the
  ecosystem architecture.
- [`repo-readiness.md`](repo-readiness.md) owns interaction modes, repository
  isolation, validation, and governance posture.
- [`orchestration-and-parallelism.md`](orchestration-and-parallelism.md) owns
  worker-lane and reconciliation rules.
- [`repo-to-repo-interface-contracts.md`](repo-to-repo-interface-contracts.md)
  owns producer/consumer compatibility boundaries.
- [`source-first-retrieval.md`](source-first-retrieval.md) owns evidence
  ordering and source verification.
