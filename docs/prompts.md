# Reusable Workflow Prompt Templates

This file holds reusable, executor-neutral prompt shapes. Keep workflow rules
in the core playbook docs, executor-specific execution guidance in the matching
tool adapter, and repo-local execution rules in `AGENTS.md`.

Prompts should remain routing and execution envelopes, not duplicated workflow
doctrine. For the rationale, see
[`sparse-rehydration-and-source-grounding.md`](sparse-rehydration-and-source-grounding.md).

For repository-scoped prompts, route through current
[`start-here.md`](start-here.md) and hydrate established state from
authoritative Repository or History artifacts instead of copying doctrine into
the prompt. Every generated prompt or handoff is a complete drop-in artifact:
it is self-contained for its intended receiving context and directly usable.
Thread routing and still-current context may reduce duplicated background, but
never produce a partial executable artifact. Apply the governing
[complete-prompt rule](repo-readiness.md#interaction-mode-preflight) rather
than reconstructing the requested action from conversation history or another
prompt.

Keep exact values prompt-local when identity, authority, safety, validation, or
unambiguous retrieval requires them. Complete does not mean reproducing all
doctrine, history, or durable state. Reducing redundant context is execution
engineering, not methodology or architecture evidence.

## Task-Shape Surface Selection And Thin Handoffs

Apply the core model's
[`interactive and execution surface`](core-model.md#interactive-and-execution-surfaces)
roles. Keep discussion, judgment, clarification, steering, review, and
disposition interactive. Use an execution surface once a bounded outcome needs
tools, mutation, validation, or evidence production. When that requires a
transition from an interactive surface, apply the shared
[consent boundary](core-model.md#interactive-to-execution-transition-consent).
The matching adapter owns each concrete product mapping; difficulty, model
choice, and product identity do not select the role.

Keep these dimensions distinct:

| Dimension | Meaning |
| --- | --- |
| Surface role | Interactive or execution. |
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
role-specific envelope remains a complete current handoff while pointing to
that state instead of reproducing it. Include, as applicable:

- target surface or executor role;
- bounded requested outcome;
- exact self-describing governed manifest or sealed-package identity;
- current human direction and bounded authority declaration, its owning
  authority reference, and prohibited actions;
- mutable sources that the target must refresh from their owners;
- required locality and tools;
- validation, outputs, and completion or stop boundary.

These are semantic fields, not a package schema. Verify the exact identity
required by the owning package contract before relying on its payload; a mutable
directory or bare folder path is navigation only. The envelope declares bounded
authority and its live owning reference but creates none. If package identity
or current authority is unavailable, stale, mismatched, or ambiguous, stop the
affected execution rather than reconstructing it from conversation.

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

### Repository mutation and decision-boundary check

Before a generated prompt or handoff requires implementation mode or Git
mutation, identify the current human direction or narrower owning-workflow rule
that authorizes it. Apply the canonical decision rule in
[`repo-readiness.md#repository-mutation-and-decision-boundaries`](repo-readiness.md#repository-mutation-and-decision-boundaries).

A direct request to implement and open a pull request should produce one
focused implementation branch and pull request unless the human explicitly
requests another artifact or a narrowly applicable workflow requires one.
Materiality, design work, or an independent-review requirement may add a
semantic decision or review boundary, but does not independently add a design
document, staging branch, or proposal-only pull request. Put required review or
approval against the exact implementation artifact when the owning workflow
permits it.

When current intent asks only for discussion, design, a specification, or a
review, select review/audit or orchestration/prompt-authoring mode and omit
implementation topology. Create a separate repository artifact only when it is
explicitly requested or narrowly required, and keep its authority distinct
from later implementation authority. Do not infer current repository mutation
from recorded future intent.

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

Thread routing never relaxes prompt completeness:

- A `FRESH THREAD` receives a complete prompt suitable for its fresh receiving
  context.
- A `SAME THREAD` receives the complete instruction for its next bounded
  action. It may reference still-current established state available to that
  thread, but remains directly usable without another prompt.
- A `CHILD TASK` receives a complete bounded child prompt.

The [prompt delivery decision model](#prompt-delivery-decision-model) applies
to every complete prompt across these routing modes.

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

For material execution that may be reviewed, recovered, or replayed, apply
[`prompt-contracts.md`](prompt-contracts.md). It owns the separation among the
immutable semantic contract, rendered bytes, append-only attempt receipt,
authority references, fresh selection, and replay. This template layer does not
redefine those identities or turn them into authority.

Use lint-safe placeholders such as `[repository]`, `[validation_path]`, or
backticked tokens in Markdown templates. Angle-bracket placeholders can be
interpreted as inline HTML by Markdown tooling.

## Complete Prompt Shape

When inline presentation is selected for a complete generated prompt, that
selection controls the final response surface. Emit exactly two consecutive
fenced code blocks: one shared operator-metadata block, then one complete
executable block. Do not emit assistant-authored prose, headings, labels,
separators, or postambles before, between, or after those blocks. Preserve
ordinary line breaks inside both blocks; do not introduce Markdown
line-continuation backslashes or equivalent escaping artifacts. The executable
block must remain complete and actionable without the metadata, so the operator
can copy only that block. Matching executor adapters own concrete metadata
fields and client presentation mechanics.

```text
Operator metadata (do not include in prompt)
Thread routing: [FRESH THREAD | SAME THREAD | CHILD TASK]
Recommended model: [matching executor adapter selection]
Recommended reasoning/thinking: [matching executor adapter selection]

Reason:
[one concise task-specific explanation]
```

## Produced-Artifact Classification

Classify the artifact actually produced before choosing presentation. Explicit
human readiness language is authoritative input, but request words such as
`example`, `sample`, `roughly`, `preview`, or `demo` do not make an otherwise
complete or substantially executable artifact conceptual. A substantially
executable artifact supplies enough task, scope, constraints, sources,
validation, and stop information for a downstream executor to act.

Resolve known prompt-local values and classify complete or substantially
executable output as a complete prompt before applying the delivery decision
model below. Later recipient, capability, presentation, or renderer selection
cannot downgrade it. If missing facts prevent a truthful ready-to-run artifact,
resolve them or return the owning blocked result. Genuine discussion, quoted
material, isolated snippets, and incomplete fragments remain lightweight.

## Prompt Delivery Decision Model

Keep prompt delivery small and deterministic. Classify the produced artifact,
resolve the execution recipient independently from the human viewer, and then
select one presentation:

- no prompt: no delivery action;
- conceptual fragment: lightweight conversational presentation;
- complete prompt for a human recipient: the canonical inline two-block
  presentation;
- qualifying small canonical-text prompt for a ChatGPT or Claude machine
  recipient with a permitted Airtable route: the Airtable record handoff below;
  or
- missing, unresolved, or mismatched recipient, route, destination, or required
  identity: a clear blocked result with no alternate renderer.

Do not use request wording, operator visibility, or an available file provider
to override the resolved recipient and route. A file provider is not a fallback
for a qualifying small canonical-text handoff. A separately authorized workflow
may select file-backed delivery only when its payload actually requires
arbitrary bytes or provider file identity, revision, or checksum behavior.

### Airtable canonical-text handoff

This section owns the shared ChatGPT/Claude handoff contract. Adapters map its
operations to the connector actions exposed by each executor; they do not copy
or redefine these rules.

A handoff qualifies as small canonical text when the frozen payload fits
unchanged in one `Payload` long-text field and within the current connector's
single-record request and response limits. The permitted Airtable route owns
that runtime limit check. Payloads that do not qualify remain outside this
normal text route; they do not trigger a fallback from it.

Use one new Airtable record per producer attempt with these required fields:

- `Handoff Key`
- `Payload`
- `Payload Bytes`
- `SHA-256`
- `Producer`

Freeze `Payload` as UTF-8 without a BOM, with LF line endings and an explicitly
declared final-newline state. `Payload Bytes` is the length of those exact bytes
and `SHA-256` is their lowercase whole-payload digest. Create the record once
and never update it. A correction creates a new key and record; its external
envelope names the predecessor when applicable.

After creation, hand over an external envelope containing the exact base ID,
table ID, returned record ID, expected handoff key, text format and final-
newline rule, expected byte length, expected SHA-256, producer executor and
attempt identity, and predecessor identity when applicable. Airtable's shared
user identity and the declared `Producer` field do not authenticate the
executor; executor attribution remains external attempt evidence.

The consumer retrieves by exact record ID, never by fuzzy search or key lookup,
and requires exactly one result with the expected key and field set. It
re-encodes the returned payload under the declared text rules, independently
recomputes byte length and SHA-256, and requires agreement among the recomputed
values, stored fields, and external envelope. Missing, multiple, stale,
transformed, truncated, or mismatched content fails closed. Key lookup is
diagnostic only.

This protocol relies on append-only behavior rather than Airtable-enforced key
uniqueness or record immutability. It creates no extra lifecycle states,
approval gate, fallback ladder, or storage abstraction.

## Cross-Executor Prompt Presentation

This section applies the decision model symmetrically when one executor
produces a complete prompt for another: each direction is governed by the same
shared presentation and handoff contract.

For a qualifying small canonical-text ChatGPT/Claude machine handoff, apply the
[Airtable contract](#airtable-canonical-text-handoff) and provide the target-
shaped thin envelope without reproducing the complete prompt in chat. For a
human execution recipient, use the matching adapter's canonical inline
presentation. Inspect unknown connector capability before selection; if the
required Airtable route or identity is unavailable, fail clearly rather than
switching to file-backed delivery or reconstructing the prompt in chat.

Prompt governance remains a separate selection. A material prompt that passes
its admission test additionally applies the
[`issue-owned durable rendered-prompt handoff profile`](prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile).
Complete that profile before reporting preservation or providing an
exact-identity handoff. Routine handoffs do not acquire material-prompt
governance merely because Airtable carries them.

## Quick Navigation

- [Task-Shape Surface Selection And Thin Handoffs](#task-shape-surface-selection-and-thin-handoffs)
- [Prompt Delivery Decision Model](#prompt-delivery-decision-model)
- [Airtable Canonical-Text Handoff](#airtable-canonical-text-handoff)
- [Cross-Executor Prompt Presentation](#cross-executor-prompt-presentation)
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
- Apply
  `docs/source-first-retrieval.md#minimum-sufficient-retrieval`: state the claim
  or decision and its evidence boundary, then retrieve only the authoritative
  state needed to support it. Do not prescribe speculative provider-object
  inventories.
- For overlap or collision risk, inspect current `main`, relevant pull
  requests, target files, and specifically identified refs as needed. Do not
  inventory every branch, ref, workflow, or provider object unless that
  inventory is materially necessary to the decision.

Scope:
- In scope: [files, behavior, or workflow area]
- Out of scope: [explicit non-goals]

Constraints:
- Keep the change minimal, scoped, and structurally local.
- Follow existing repo patterns and canonical validation.
- Follow `docs/repo-readiness.md`, the matching executor adapter, and
  repo-local `AGENTS.md` for interaction mode, command form, worktree,
  validation, and delivery.
- Surface blockers, validation failures, unresolved risks, and material
  uncertainty.

Tasks:
1. Inspect the existing structure and relevant source material.
2. Make the smallest scoped change that satisfies the goal.
3. Update nearby docs or tests only when they are part of the same change.

Validation:
- Run [validation_path].
- Report the canonical outcome and any material validation exception.

Delivery:
- [branch, commit, push, and PR expectation, or explicit exclusion]
- Apply `docs/core-model.md#successful-completion-projection` to the final
  report.

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
- Workers stop at PR readiness and report to the coordinating orchestrator the
  changed files, validation, overlap, blockers, residual risk, and merge-order
  dependencies needed for lane reconciliation.
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
the permitted Airtable base and table from that narrower owner; do not embed
them in the referenced rendered prompt. This envelope is not part of the
referenced rendered-prompt bytes or rendered-prompt digest.

```text
External issue-owned durable prompt delivery envelope:
- Boundary: this envelope is not part of the referenced rendered-prompt bytes or rendered-prompt digest
- Governing issue and authority reference: [planning identity and current human authority]
- Airtable identity: base [base ID]; table [table ID]; record [exact returned record ID]
- Expected handoff key: [key]
- Canonical payload: UTF-8; no BOM; LF line endings; final newline [present | absent]
- Expected payload bytes: [byte count]
- Expected SHA-256: [lowercase digest]
- Producer attempt: [executor and attempt identity]
- Predecessor: [none or prior record and attempt identity]
- Admission result: [six conditions passed, with privacy, visibility, retention, and natural owner]
- Identity timing: derive the key, byte length, SHA-256, and record identity only after the rendered prompt is frozen

Receiver verification:
- Retrieve exactly one record by the exact record ID; do not use fuzzy search or key lookup as retrieval.
- Require the expected key and five-field record, re-encode the payload, and independently verify byte length, SHA-256, UTF-8, no BOM, LF endings, and the declared final-newline rule before acceptance.
- Re-read current authority and mutable repository, provider, and planning state from their owners before execution.
- Fail closed on a missing, multiple, stale, transformed, truncated, or mismatched record, prohibited retention, unsupported required capability, or ambiguous authority.

Evidence:
- Keep operator metadata, this envelope, Airtable record, rendered prompt, producing receipt, delivery evidence, executor attempt, attempt receipt, output, and human disposition as separate identities when required.
- Every admitted prompt write has exactly one distinct producing receipt.
- The shared Airtable user and `Producer` field do not authenticate the executor; keep executor attribution in external attempt evidence.
- Every prompt, record, hash, delivery, receipt, validation result, and successful execution transfers zero authority.

Correction:
- Never update or delete the frozen record. Create a new record and key and carry predecessor lineage in this external envelope.
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
- At successful completion, apply the
  `docs/core-model.md#successful-completion-projection` rule. Report the
  completed outcome, reviewable repository result and status, canonical
  validation and review summary, useful exact implementation identity, and
  stop boundary.
  Add changed-file, risk, or evidence detail only when it materially affects
  operator review or action.
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
- Apply `docs/review-packet.md#direct-pr-inspection`, including its
  connector-sufficient review latch.
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
