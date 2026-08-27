# Reusable Workflow Prompt Templates

This file holds reusable, executor-neutral prompt shapes. Keep workflow rules
in the core playbook docs, executor-specific execution guidance in the matching
tool adapter, and repo-local execution rules in `AGENTS.md`.

Prompts should remain routing and execution envelopes, not duplicated workflow
doctrine. For the rationale, see
[`sparse-rehydration-and-source-grounding.md`](sparse-rehydration-and-source-grounding.md).

For a fresh repository-scoped thread, explicitly route through current
[`start-here.md`](start-here.md) and hydrate established state from
authoritative Repository or History artifacts instead of replaying it in the
prompt. The prompt carries the current delta: goal, governing authority or
issue, authoritative artifact references, authorization, constraints,
completion boundary, and stop rules.
Self-contained means complete routing and authorization, not embedding every
referenced artifact.

A same-thread continuation may carry only the changed delta while established
source state remains current. Keep exact values prompt-local when required for
identity, authority, safety, validation, or unambiguous retrieval. Reducing
redundant context is execution engineering, not methodology or architecture
evidence.

## Task-Shape Surface Selection And Thin Handoffs

Select a target surface or execution role by semantic role, execution locality,
required tools, and deliverable. Keep work with an interactive controller while
the next useful result is discussion, judgment, clarification, steering, or
review. Move to a general-purpose bounded executor when a bounded multi-step
outcome or non-repository deliverable has emerged. Move to a repository
executor when completion materially depends on repository locality, terminal
commands, tests, version control, worktrees, commits, pull requests, or code
review.

Difficulty, model tier, and reasoning setting do not select a surface. A task
changes surface only after a bounded outcome and execution contract have
emerged. Ordinary discussion, brainstorming, and conceptual work remain
lightweight and do not inherit repository ceremony. The matching target adapter
owns each concrete product or executor projection.

Keep these dimensions distinct:

| Dimension | Meaning |
| --- | --- |
| Interaction surface | Where a human discusses, steers, reviews, or delegates. |
| Executor identity | The runtime or agent that performs the bounded work. |
| Task shape | Interactive reasoning, a general delegated outcome, or repository execution. |
| Model or reasoning choice | An execution setting that does not by itself change semantic role. |
| Handoff contract | Current sources, authority declaration and owning reference, constraints, locality, validation, outputs, and stop boundary. |
| Durable package pointer | The exact external manifest or sealed-package identity used to hydrate recoverable state. |
| Durable continuity | The owning authoritative sources and records from which the work can be recovered. |

An interface change does not create a new durable executor identity or
authority contract when the underlying executor identity and authority remain
the same. A transition to a distinct repository executor is a repository-
execution handoff and must make repository, locality, tools, validation,
delivery, and stop boundaries explicit. Shared application chrome, project
membership, conversation history, product branding, or a folder name does not
prove that context or authority transferred.

### Surface-transition check

At a surface transition, re-evaluate context sufficiency and any materially
changed source, authority, locality, acting identity, tool, validation, output,
or completion boundary. Retrieve newly activated owners and refresh mutable
repository, planning-system, and provider facts from the systems that own them
before relying on those facts. Reuse still-current verified context; a surface
change does not require blanket rehydration or replay of unchanged doctrine.

### Thin semantic handoff envelope

When complete recoverable state is held outside the conversation, a thin
role-specific envelope carries only the current routing delta. Include, as
applicable:

- target surface or executor role;
- bounded requested outcome;
- exact self-describing governed manifest or sealed-package identity;
- current human direction and bounded authority declaration, its owning
  authority reference, and prohibited actions;
- mutable sources that the target must refresh from their owners;
- required locality and tools;
- validation, outputs, and completion or stop boundary.

These are semantic fields, not an operational package schema. The pointed
package may preserve the complete contract, accepted inputs, source and
artifact identities, prior decisions, receipts, validation evidence, and a
recorded next permitted action. The target must retrieve and verify the exact
manifest or sealed-package identity before relying on that payload. For
material execution, use the exact identity evidence required by the owning
package contract, such as an immutable path plus digest, file identity, attempt
identity, or version. A mutable issue directory, package root, or bare folder
path is navigation only; it is not the governing package identity.

The envelope declares human direction, bounded authority, and the owning
authority reference but creates zero authority itself. Stored contracts,
next-action statements, paths, digests, packages, prompts, receipts,
validation, and successful retrieval also create or transfer zero authority. A
recorded next action remains historical or asserted instruction until the
current acting identity and live authority are verified from their owner.

If the exact package identity is inaccessible, unresolved, stale, mismatched,
or ambiguous, stop before affected execution or return an explicit
non-authorizing partial result. Do not reconstruct missing contract, authority,
or evidence from conversation memory.

### Target-shaped projections

Shape the thin envelope through the matching target adapter rather than sending
one generic prompt. A general-purpose bounded-executor projection emphasizes
the delegated outcome, permitted sources and tools, source refresh, output
form, quality checks, and return boundary. A repository-executor projection
also makes repository identity and locality, repository tools, canonical
validation, delivery, and the stop-before-merge boundary explicit.

## Explicit Kickoff Mutation Boundary

Every generated kickoff or orchestration prompt must declare an explicit,
task-appropriate mutation boundary. Apply the three-class model in
[`core-model.md`](core-model.md#kickoff-mutation-boundaries); do not use vague
blanket phrases such as `read-only first response`, `no mutation on kickoff`,
`do not touch anything yet`, or `do not mutate the planning or artifact system
in the first response` as substitutes for the actual boundary.

Use this provider-neutral projection and resolve each field for the task:

```text
Kickoff mutation boundary:
- Orchestration/evidence mutations: [task-owned writes allowed now, their
  prerequisites, and the authority that permits them; or none]
- Delegated substantive execution: [work reserved for a later executor or
  phase and prohibited here, or work separately authorized here under its own
  bounded authority]
- Human-gated transitions: [decisions that still require a separate exact
  human authorization]
- Unrelated state: [planning items, repositories, providers, and execution
  state that remain untouched]
- Blocked kickoff: [do not falsely advance the governing task; record the exact
  blocker only when that task-owned write is useful and authorized]
```

When the kickoff is genuinely fully read-only, say why, name the actor and
mutation surfaces covered, and keep the restriction no broader or longer than
the owning workflow requires. When orchestration or evidence writes are
allowed, state that they do not authorize delegated substantive execution or a
human-gated transition. Prompt text, digests, receipts, artifacts, planning
status, successful calls, storage objects, comments, validation, retrieval,
review, branches, commits, and pull requests create zero authority.

This prompt projection does not redefine interactive-control or target-surface
routing, artifact storage admission, transport, delivery, retention, cleanup,
or replay, or operator-visible progress and client behavior. It governs the
controller's declared boundary, not prompt-contract machinery: hydrators,
adapters, renderers, validators, receipts, and checkpoints remain unable to
drive lifecycle state or orchestration.

### Provider-neutral examples

| Situation | Explicit kickoff boundary |
| --- | --- |
| Ready kickoff | Current authority and prerequisites pass, so the controller may advance the governing task, preserve the exact downstream prompt and receipt under the applicable evidence contract, verify their identities, and return the handoff. It performs none of the delegated repository execution. |
| Blocked kickoff | A prerequisite or authority check fails. The controller does not falsely advance the task; it may record the exact blocker when that task-owned write is useful and authorized. No downstream execution is implied. |
| Architecture thread | The controller may write and preserve the task-owned decision package. Architecture adoption remains a separate human decision against the reviewed package identity. |
| Destructive workflow | The controller may produce and preserve a read-only manifest. Deletion remains separately human-approved and is not authorized by the manifest. |
| Delegated repository implementation | The controller may preserve the downstream prompt and task-owned planning evidence. The repository executor owns repository mutation only under its own bounded authority and prerequisites. |

## Thread Routing And Configuration Continuity

Model selection, reasoning or thinking configuration, and thread routing are
separate decisions. Declare one of these routing values in operator metadata:

- `FRESH THREAD`: select the task-appropriate model and separately select a
  supported reasoning or thinking configuration through the executor adapter.
- `SAME THREAD`: preserve the current thread's model and configuration by
  default. Preserve the requested parent configuration; observe and account for
  any effective runtime substitution. A lower-cost setting being sufficient for
  the next sub-phase does not itself authorize or justify changing an
  already-running task.
- `CHILD TASK`: select the lowest-cost sufficient configuration for the bounded
  child, and preserve its model/configuration, inputs, execution identity,
  durable result, and authority boundary where the workflow requires it.

Use the executor adapter for vendor-specific routing. For an existing task that
exceeds its assigned capability, prefer a bounded stronger child or an explicit
fresh-thread transition over an untracked parent configuration change. For an
existing stronger task's deterministic follow-up, prefer a bounded cheaper
child where worthwhile rather than downgrading the parent in place. Continuity
preserves context, decision provenance, reproducibility, and qualification
boundaries; it does not prevent justified escalation.

Requested configuration is the operator's selected model and supported
reasoning/thinking setting. Effective configuration is what the runtime reports
as serving the work. Record requested and effective values separately where the
runtime exposes them, along with a fallback or substitution event. If the
effective value is not observable, say so; requested configuration alone does
not prove execution identity. A runtime change is not automatically fatal, but
requalify, escalate, or stop when it fails a minimum-capability or exact-model
requirement.

## Operator Metadata And Executable Prompts

Generated task prompts serve two audiences:

- **Operator metadata** is for the human/operator or an orchestration layer
  that instantiates the task. It may state thread routing, a recommended model
  and reasoning/thinking setting, a selection reason, and other runtime
  guidance the downstream agent cannot control.
- **Executable prompt** is for the downstream execution agent. It contains
  only task authority, repository and workflow instructions, scope,
  constraints, decision rules, validation, stop boundaries, and information
  the agent can observe, control, or must use to make a task decision.

Copy or deliver only the executable prompt to the downstream agent unless its
execution surface separately consumes metadata. Operator metadata must never
be semantically required by the task body: removing it must leave one complete,
actionable prompt.

Use this drafting test for every executable instruction: include it only when
the downstream agent can observe it, control it, or must use it to make a task
decision. Thread creation, parent-model selection, reasoning configuration,
subscription or usage-budget considerations, and instructions to preserve an
already-created parent's configuration normally belong only in operator
metadata. They are immutable runtime facts, not task authority.

Apply the rule to routing as follows:

- For a `FRESH THREAD`, the operator selects the thread, model, and
  reasoning/thinking setting before prompt delivery. The executable body does
  not repeat those selections.
- For a `SAME THREAD`, operator metadata may preserve current configuration;
  the executable body states only task-relevant continuity, such as preserving
  repository authority, durable state, or the current branch/PR.
- For a `CHILD TASK`, the executable body may authorize bounded delegation
  only where the active executor can perform it. Keep vendor model matrices,
  effort mapping, and selection rationale in the adapter or orchestration
  configuration rather than copying them into every child prompt.

This boundary does not remove runtime evidence that the task itself requires.
An executable prompt may require recording or verifying requested/effective
runtime model evidence, detecting a disallowed substitution, or writing an
execution receipt when that information is part of the task's validation or
qualification boundary.

### Executor-Applied Visible Thread Names

Use a visible thread name only as human navigation. It is not task authority,
durable continuity, execution identity, or evidence of current planning,
repository, branch, pull-request, validation, or review state. Retrieve each
of those facts from its owning current source.

The name is an executor action, not an operator configuration. Do not put a
`Recommended thread name` field in operator metadata. Whether an executable
prompt can contain an executor-applied naming section is established only by
the matching downstream target executor adapter, not by the client or executor
that authors or presents the prompt.

When one planning item governs the current intent and completion boundary, use
`[planning-id] — [short bounded task]`. Preserve the planning identifier exactly
as represented by its owning planning system. When there is no governing
planning identifier, use only the concise bounded task name. When several
identifiers are related, use only the identifier governing the current intent
and completion boundary; keep predecessors, related items, implementation
references, and secondary identifiers in normal prompt context. If no single
governing identifier can be selected without inventing precedence, omit the
identifier. This convention is planning-system-neutral and does not require
Linear.

Route eligibility does not establish executor capability:

- `FRESH THREAD` may receive the adapter-owned naming section when its
  downstream target executor explicitly supports executor-applied naming.
- `CHILD TASK` may receive it only when the child has its own separately
  visible, nameable thread or task and its downstream target executor
  explicitly supports executor-applied naming.
- `SAME THREAD`: preserve the established visible name unless an explicit
  rename is part of the task; do not inject a routine naming section.

During prompt construction, replace `[resolved thread-name section when
applicable]` through the matching downstream target executor adapter. The
adapter resolves it to its complete naming section and exact computed name only
for a supported `FRESH THREAD` or eligible separately visible `CHILD TASK`.
Resolve it to nothing when the target adapter does not explicitly establish an
executor-applied visible-thread naming capability, and for an ordinary `SAME
THREAD`. Do not leave the placeholder in a final generated prompt or ask the
downstream executor to infer or recover the name from planning or repository
context.

When a complete prompt materially changes, emit a complete replacement
operator-metadata block and executable prompt. Do not emit a partial prompt
patch that requires the operator to splice text into an older prompt.

## Prompt Contract Identity

For material execution that may be reviewed, recovered, or replayed, apply the
canonical semantics in [`prompt-contracts.md`](prompt-contracts.md). Keep the
immutable semantic prompt contract separate from the append-only attempt
receipt and from the exact rendered prompt bytes.

The immutable semantic contract is created and hashed before hydration or
rendering. It defines meaning, compatibility, validation, authority-reference,
reasoning, transport, evidence, and fail-closed requirements without including
selected or derived digests. The attempt receipt references that contract and
records selected sources, derived identities, delivery, current safety-policy
observation, live-authority outcome, validation, and execution evidence.

The prompt carries bounded instruction and evidence; it does not own canonical
doctrine, durable workflow state, evidence acceptance, or approval. Prompt
text, contract digests, validation success, receipts, checkpoints, and
transport delivery cannot grant authority. The execution or adoption layer
must re-read live durable authority immediately before action.

Fresh attempts select compatible inputs once and keep them immutable. Replay
resolves the recorded contract and exact inputs without reading current mutable
sources or silently upgrading an adapter, renderer, validator, reasoning
recommendation, or fallback policy. Replay reproduces authorized inputs, not
deterministic model output.

The Playbook-owned machine-readable anchors and canonicalization vectors are:

- [`prompt-contract-semantic-anchors-v2.json`](prompt-contract-semantic-anchors-v2.json)
- [`prompt-contract-canonicalization-vectors-v1.json`](prompt-contract-canonicalization-vectors-v1.json)

They encode semantic anchors and conformance evidence only. They are not an
operational schema, prompt generator, hydrator, renderer, receipt, or workflow
engine.

Use lint-safe placeholders such as `[repository]`, `[validation_path]`, or
backticked tokens in Markdown templates. Angle-bracket placeholders can be
interpreted as inline HTML by Markdown tooling.

## Complete Prompt Shape

For a complete generated prompt, emit one shared operator-metadata block and
one complete executable block consecutively. The executable block must remain
complete and actionable without the metadata, so the operator can copy only
that block. Matching executor adapters own concrete metadata fields and client
presentation mechanics.

```text
Operator metadata (do not include in prompt)
Thread routing: [FRESH THREAD | SAME THREAD | CHILD TASK]
Recommended model: [matching executor adapter selection]
Recommended reasoning/thinking: [matching executor adapter selection]

Reason:
[one concise task-specific explanation]
```

## Material Cross-Executor Prompt Presentation

Use this presentation sequence when the output is one complete prompt or task
envelope for a different thread, child task, or execution surface; exact
identity, operator review, recovery, citation, or replay materially matters;
the six-condition issue-owned durable-prompt admission test passes; ownership,
privacy, visibility, retention, and destination are unambiguous; and currently
qualified absent-create, raw-readback, operator-preview, and downstream-
delivery routes are available. Routine short prompts, brainstorming,
incomplete fragments, and ordinary same-thread deltas remain lightweight and
inline.

The required order is:

```text
render -> admit -> absent-create -> raw verify -> operator preview ->
explicit approval -> fresh delivery route -> thin bootstrap ->
executor exact verification -> execution
```

Raw provider readback and exact identity verification must finish before the
preview is presented. The preview route and the executor-delivery route are
distinct operations: preview must not prefetch, unfurl, scan, or consume a
bounded delivery URL, and the executor route is not minted until explicit
approval.

After raw verification, normally present compact removable operator metadata,
the provider-backed preview or file object, the semantic filename and
issue-owned path, exact byte size and whole-file SHA-256, provider object ID
and revision when available, the downstream executor or prompt role, and one
explicit `Approve`, `Revise`, or `Reject` boundary. Do not print the full
executable prompt inline by default after this path succeeds. The operator may
request the complete prompt inline without changing the durable identity, and
removing the operator metadata must still leave the executable prompt
complete.

Preview is a human-readable convenience surface. It is not raw-byte
verification; does not prove size, SHA-256, provider content hash, revision,
or equality; does not imply approval; is not delivery, acknowledgement,
execution start, or attempt completion; creates no coordination state; and
transfers zero authority.

An operator revision leaves the previewed version immutable and unsent. Record
predecessor lineage, absent-create the next semantic version at a unique
immutable identity, repeat raw verification and preview, and obtain fresh
explicit approval. If rejected v1 is followed by approved v2, the eventual
bootstrap names only v2. Never overwrite or silently reuse v1, and never add a
mutable `latest`, `current`, or `final` locator.

Only after approval, mint a fresh bounded delivery route and emit a thin
target-shaped bootstrap that omits the full prompt body. Name the approved
durable path, provider object ID and revision when available, expected byte
size and whole-file SHA-256, provider content hash when available and
applicable, retrieval mechanism, lifetime, consumption behavior, and the
requirement to verify exact bytes before reading or execution. Expiry, prior
consumption, or failed retrieval requires a new delivery operation for the
same durable prompt, not a new prompt version. Never reconstruct missing bytes
from the bootstrap, conversation history, or memory.

If any required capability or admission condition is unavailable or
unqualified, stop before provider creation when admission has not passed, name
the precise gap, and make no capture, readback, preview, approval, or delivery
claim. Use the complete inline presentation only when the prompt is safe to
display and the operator can review every byte before manual send; keep
operator metadata outside that executable prompt. Otherwise stop with a
non-authorizing capability blocker.

## Quick Navigation

- [Task-Shape Surface Selection And Thin Handoffs](#task-shape-surface-selection-and-thin-handoffs)
- [Material Cross-Executor Prompt Presentation](#material-cross-executor-prompt-presentation)
- [Repository Implementation Task](#repository-implementation-task)
- [Parallel Batch Add-On](#parallel-batch-add-on)
- [Orchestration Handoff](#orchestration-handoff)
- [Operator-Visible Progress Add-On](#operator-visible-progress-add-on)
- [Governed Artifact Capture Add-On](#governed-artifact-capture-add-on)
- [Issue-Owned Durable Prompt Delivery Envelope Add-On](#issue-owned-durable-prompt-delivery-envelope-add-on)
- [Implementation Delivery Add-On](#implementation-delivery-add-on)
- [PR Review](#pr-review)

## Repository Implementation Task

Use this template only when the intended interaction mode is direct
implementation. For review or orchestration, use the matching template instead.
Use the matching executor adapter to select model and reasoning/thinking
configuration. For a complete generated prompt, precede this executable body
with the shared operator-metadata block in [Complete Prompt Shape](#complete-prompt-shape).

```text
Role:
- You are implementing a scoped repository change in [repository].
- Work layer: implementation.

Goal:
- [desired outcome]

Success criteria:
- [observable condition that proves the goal is met]
- The diff is limited to the intended repository and scope.
- Canonical validation has run or any inability to run it is reported.
- PR delivery is complete unless explicitly excluded.

Context:
- Repository: [repository]
- Working directory: [working_directory]
- Relevant background: [short context]
- GitHub issues or planning references: [none or identifiers]
- Dependencies: [none or required predecessors, inputs, or services]

[resolved thread-name section when applicable]

Retrieval:
- Read `ai-workflow-playbook/docs/start-here.md`, the target repo's
  `AGENTS.md`, and any required tool adapter before acting.
- Retrieve or revalidate authoritative repository, issue, PR, file, CI, log, or
  artifact state before relying on it.
- Stop broad search once the target files, constraints, validation path, and
  delivery expectation are clear.

Scope:
- In scope: [files, behavior, or workflow area]
- Out of scope: [explicit non-goals]

Constraints:
- Keep the change minimal, scoped, and structurally local.
- Follow existing repo patterns and canonical validation.
- Follow `docs/repo-readiness.md`, the matching executor adapter, and
  repo-local `AGENTS.md` for interaction mode, command form, worktree,
  validation, and delivery.
- Report blockers, validation failures, residual risks, and uncertainty.

Tasks:
1. Inspect the existing structure and relevant source material.
2. Make the smallest scoped change that satisfies the goal.
3. Update nearby docs or tests only when they are part of the same change.

Validation:
- Run [validation_path].
- Report the exact result.

Delivery:
- [branch, commit, push, and PR expectation, or explicit exclusion]
- Include a concise summary, validation results, and residual risks.

Permissions and completion boundary:
- Authorized actions: [local edits, validation, commit, push, PR, or narrower]
- Kickoff mutation boundary:
  - Orchestration/evidence mutations: [task-owned writes allowed now, their
    prerequisites, and the authority that permits them; or none]
  - Delegated substantive execution: [work separately authorized here under
    its own bounded authority, or reserved for a later executor or phase]
  - Human-gated transitions: [decisions requiring separate human authorization]
  - Unrelated state: [planning items, repositories, providers, and execution
    state that remain untouched]
  - Blocked kickoff: [do not falsely advance the governing task; record the
    exact blocker only when useful and authorized]
- Completion ends at: [validated artifact, review packet, draft PR, or other]

Stop rules:
- Stop before merge, release, tag, destructive, externally visible, or
  permissions-sensitive actions unless explicitly authorized.
- Stop and report if required source state cannot be retrieved, the repo
  context is mismatched, or validation failure implies broader work.
```

## Parallel Batch Add-On

Use this compact add-on when asking an implementation agent to coordinate a
parallel batch. Keep the concrete lane count and topology task-specific.
Use [`orchestration-and-parallelism.md`](orchestration-and-parallelism.md) to
decide whether the work should be split at all.

```text
Parallel execution:
- Separate lanes by repository, file area, behavior surface, or risk surface.
- Define any merge-order dependencies before launch.
- Keep one repository, one branch, one worktree, and one PR per lane.
- Validate each lane with the repository's canonical validation path.
- Workers stop at PR readiness and report changed files, validation, overlap,
  blockers, residual risk, and merge-order dependencies.
- The orchestrator inspects outputs directly, reconciles sequentially, reruns
  canonical validation after updates, and stops before merge unless explicitly
  authorized.
```

## Orchestration Handoff

Use this prompt when the deliverable is a complete downstream task envelope, not
direct mutation by the current agent.

A compact fresh-thread handoff can use this shape when the named artifacts
already carry the established state:

```text
Startup:
- Retrieve current `docs/start-here.md` through GitHub source access when
  available and follow its repository startup route.
Governing issue:
- [issue identifier or durable authority source]
[resolved thread-name section when applicable]
Authoritative state:
- [Repository or History artifact locations and exact identities when needed]
Authorized action:
- [the new bounded action]
Constraints:
- [only task-specific constraints not already owned by the referenced sources]
Completion and stop boundary:
- [required result, validation, delivery, and conditions that require stopping]
Kickoff mutation boundary:
- Orchestration/evidence mutations: [task-owned writes allowed now, their
  prerequisites, and the authority that permits them; or none]
- Delegated substantive execution: [work reserved for a later executor or
  phase and prohibited here, or work separately authorized here under its own
  bounded authority]
- Human-gated transitions: [decisions requiring separate human authorization]
- Unrelated state: [planning items, repositories, providers, and execution
  state that remain untouched]
- Blocked kickoff: [do not falsely advance the governing task; record the exact
  blocker only when useful and authorized]
```

Required inputs:

- `repository`
- `working_directory`
- `canonical_source`
- `source_evidence`
- `interaction_mode`
- `kickoff_mutation_boundary`
- `validation_path`
- `delivery_expectation`

Use the matching executor adapter to select model and reasoning/thinking
configuration. For a complete generated prompt, precede this executable body
with the shared operator-metadata block in [Complete Prompt Shape](#complete-prompt-shape).

```text
Role:
- You are a downstream agent completing a bounded task for [repository].
- Work layer: [research, design, implementation, review, or coordination]

Goal:
- [clear user-visible outcome]

Success criteria:
- [what must be true before final response]
- The work stays within the named repository and scope.
- Required validation has run or a blocker is reported.
- The final answer includes the requested artifact, PR, review packet, or
  handoff evidence.

Inputs:
- Repository: [repository]
- Working directory: [working_directory]
- Canonical source: [canonical_source]
- Repo-local guidance: [AGENTS.md or equivalent]
- Source evidence: [source_evidence]
- Interaction mode: [implementation, review/audit, or orchestration]
- Validation path: [validation_path]
- Delivery expectation: [delivery_expectation]
- Dependencies: [none or required predecessors, inputs, or services]

[resolved thread-name section when applicable]

Retrieval:
- Read the shared playbook startup guidance and repo-local `AGENTS.md` first.
- Retrieve authoritative state from only the files, issues, PRs, docs, or
  artifacts needed for the goal; treat summaries as navigation only.
- Stop once the target surface, constraints, validation path, and delivery
  expectation are clear.

Scope:
- In scope: [files, behavior, docs, or workflow area]
- Out of scope: [explicit exclusions]

Constraints:
- Keep changes minimal, scoped, and structurally local.
- Do not rely on staging, runtime, generated, or local instruction surfaces as
  policy unless the rule has been promoted into the canonical source.
- Follow the referenced playbook, adapter, and repo-local guidance.
- Report blockers, validation failures, residual risks, and uncertainty.

Tasks:
1. [ordered task]
2. [ordered task]
3. [ordered task]

Validation:
- Run [validation_path], or report why it cannot run.

Delivery:
- [branch, commit, push, PR, review packet, or report expectation]
- Include summary, validation, source evidence, and residual risks.

Permissions and completion boundary:
- Authorized actions: [read-only inspection, local edits, delivery, or narrower]
- Kickoff mutation boundary:
  - Orchestration/evidence mutations: [task-owned writes allowed now, their
    prerequisites, and the authority that permits them; or none]
  - Delegated substantive execution: [work reserved for a later executor or
    phase and prohibited here, or work separately authorized here under its own
    bounded authority]
  - Human-gated transitions: [decisions requiring separate human authorization]
  - Unrelated state: [planning items, repositories, providers, and execution
    state that remain untouched]
  - Blocked kickoff: [do not falsely advance the governing task; record the
    exact blocker only when useful and authorized]
- Completion ends at: [artifact, review packet, PR, report, or other]

Stop rules:
- Stop before merge, release, tag, destructive, externally visible, or
  permissions-sensitive actions unless explicitly authorized.
- Ask for human input when required evidence is unavailable or the next step
  depends on a human judgment call.
```

## Operator-Visible Progress Add-On

Append this only when the task needs an explicit progress-presentation
contract. Apply the shared
[`Operator Observability`](core-model.md#operator-observability) rule without
copying its material-event taxonomy. Resolve the task-specific aggregate
milestones, durable item-evidence location, supported mid-run presentation
preferences, and any client-forced output limitation. This add-on changes
presentation only; it does not weaken approval, permission, destructive,
collision, overwrite, drift, privacy, retention, authority, scope, blocker, or
validation boundaries.

## Governed Artifact Capture Add-On

Append this only when the producing task's owning workflow activates
[`evidence-lifecycle.md#governed-artifact-capture`](evidence-lifecycle.md#governed-artifact-capture).
Name that workflow and any narrower storage constraints. After storage
admission, capture the complete artifact directly, verify its exact identity,
leave the proportionate permitted producing receipt, and return only a compact
conversation summary. The add-on grants no acceptance or downstream authority.

## Issue-Owned Durable Prompt Delivery Envelope Add-On

Attach this external delivery envelope only after the executable rendered
prompt has been deterministically frozen and the six-condition admission test in
[`prompt-contracts.md`](prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile)
passes and the owning storage contract permits exact durable retention. Resolve
provider, account, namespace, and issue-path values from that narrower owner;
do not embed them in the referenced rendered prompt. This envelope is not part
of the referenced rendered-prompt bytes or rendered-prompt digest. It is an
add-on to the delivery packet, not an instruction to append self-identity to the
executable prompt.

```text
External issue-owned durable prompt delivery envelope:
- Boundary: this envelope is not part of the referenced rendered-prompt bytes or rendered-prompt digest
- Governing issue and authority reference: [planning identity and current human authority]
- Exact durable identity: [immutable human locator, provider locator, object identity, size, SHA-256, provider revision when exposed or explicit unavailable status, and provider content hash when available]
- Admission result: [six conditions passed, with privacy, visibility, retention, and natural owner]
- Delivery policy: retrieve the durable object directly through a qualified route; otherwise use one private executor-owned attempt-local exact retrieval
- Prohibited delivery: no exchange root, mutable alias, shadow durable copy, or copy/paste claim of byte identity
- Identity timing: derive final size, SHA-256, provider identity evidence, and delivery route only after the rendered prompt is frozen; never embed a placeholder self-digest

Receiver verification:
- Verify raw or attempt-local bytes, size, SHA-256, UTF-8, no BOM, LF endings, and the declared final-newline rule before acceptance.
- Re-read current authority and mutable repository, provider, and planning state from their owners before execution.
- Fail closed on collision, mismatch, missing identity, prohibited retention, unsupported required capability, or ambiguous authority.

Evidence:
- Keep operator metadata, this envelope, durable prompt, producing receipt, delivery evidence, acknowledgement, executor attempt, attempt receipt, output, and human disposition as separate identities.
- Every admitted prompt write has exactly one distinct producing receipt.
- Record only observed PRESERVED, DELIVERED, ACCEPTED, STARTED, COMPLETED, FAILED, or UNKNOWN states under the minimum predicates in the canonical profile; never infer acceptance from delivery, start from acceptance, or human acceptance or authority from completion.
- Every prompt, path, hash, delivery, receipt, validation result, and successful execution transfers zero authority.

Cleanup:
- Preserve required delivery and attempt evidence, then remove only the private attempt-local retrieval when the attempt no longer depends on it.
- Revalidate containment and identity and fail closed on the shared cleanup conditions in `repo-readiness.md#repo-local-workflow-state`.
- Do not delete or rewrite the durable prompt and do not create recurring cleanup automation.
```

## Implementation Delivery Add-On

Append this only when the task is implementation mode and normal PR delivery is
expected.

```text
Delivery:
- Follow the branch, worktree, validation, and PR delivery rules in
  `docs/repo-readiness.md`, the matching executor adapter, and repo-local
  `AGENTS.md`.
- Stage, commit, push, and open or update the intended PR only with relevant
  changes.
- Include expected GitHub issue closing keywords and planning references when
  those identifiers are provided.
- Report the PR link, files changed, validation results, and residual risks.
```

## PR Review

Use this prompt when the task is to review, check, assess, approve, or comment
on an existing pull request.

Required inputs:

- `repository`
- `pull_request`
- `task_or_issue_context` (`none` when unavailable)
- `summary_only` (`yes` or `no`)

Use the matching executor adapter to select model and reasoning/thinking
configuration. For a complete generated prompt, precede this executable body
with the shared operator-metadata block in [Complete Prompt Shape](#complete-prompt-shape).

```text
Task:
Review pull request [pull_request] in [repository].

Inputs:
- Repository: [repository]
- Pull request: [pull_request]
- Task or issue context: [task_or_issue_context]
- Summary-only requested: [summary_only]

[resolved thread-name section when applicable]

Success criteria:
- Review feedback is grounded in direct PR evidence.
- Findings are severity-ordered and distinguish blockers from non-blocking
  risks or follow-ons.
- Merge readiness is stated only when supported by current PR evidence.

Retrieval:
- Inspect the PR through the GitHub connector first when available and not
  explicitly forbidden.
- Use local checkout, `git diff`, and `gh` only as supplemental evidence.
- Stop once PR metadata, changed files, relevant diffs, discussion, checks,
  mergeability, and task fit are clear enough for the requested depth.

Instructions:
- Apply `docs/review-packet.md#direct-pr-inspection`.
- Stay in review/audit mode unless the human explicitly changes the task.
- Treat user summaries, completion reports, and pasted excerpts as navigation,
  not PR evidence.
- If required PR evidence is unavailable, state that blocker and caveat any
  feedback from already-present information.

Kickoff mutation boundary:
- Orchestration/evidence mutations: [none for review-only, or the exact
  separately authorized PR comment or review action]; this reviewer otherwise
  only inspects and reports in chat because the task is review/audit mode.
- Delegated substantive execution: none; implementation is outside this review.
- Human-gated transitions: PR comments, approvals, change requests, merge, and
  every other PR mutation require separate authorization.
- Unrelated state: the repository, planning items, providers, and execution
  state remain untouched.
- Blocked kickoff: report missing evidence without mutating state or inferring
  readiness.

Output format:
1. Review findings: severity-ordered findings with file or PR references where
   possible.
2. Scope and evidence notes: inspected PR surface, checks, mergeability, and
   task fit.
3. Recommendation: `ready to merge`, `needs decision`, or `blocked`, only when
   direct PR evidence supports it.
```
