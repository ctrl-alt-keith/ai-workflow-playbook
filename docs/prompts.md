# Reusable Workflow Prompt Templates

This file holds reusable, executor-neutral prompt shapes. Keep workflow rules
in the core playbook docs, executor-specific execution guidance in the matching
tool adapter, and repo-local execution rules in `AGENTS.md`.

Apply the canonical
[agent-need test](engineering-baseline.md#agent-read-documentation)
when authoring prompt content.

Prompts should remain routing and execution envelopes, not duplicated workflow
doctrine. For the rationale, see
[`sparse-rehydration-and-source-grounding.md`](sparse-rehydration-and-source-grounding.md).

For repository-scoped prompts, apply the
[complete-prompt rule](repo-readiness.md#interaction-mode-preflight): carry the
execution delta and resolve inherited rules through current
[`start-here.md`](start-here.md). The templates below are authoring aids, not
checklists to copy wholesale. Resolve task-specific values and omit inherited
boilerplate and unused fields; keep the resulting action complete for its
intended receiving context.

## Task-Shape Surface Selection And Thin Handoffs

Apply the core model's
[surface roles](core-model.md#interactive-and-execution-surfaces): discussion,
judgment, clarification, steering, review, and disposition stay interactive;
bounded work needing tools, mutation, validation, or evidence production uses
execution. Apply its
[transition consent](core-model.md#interactive-to-execution-transition-consent)
when moving from interactive to execution. The matching adapter owns product
mappings; difficulty, model/reasoning choice, and product identity do not select
the role.

Keep surface role (interactive/execution), executor identity (acting runtime or
agent), task shape (interactive reasoning/general delegation/repository
execution), and model/reasoning settings distinct. Likewise distinguish the
handoff contract (current sources, authority declaration and owning reference,
constraints, locality, validation, outputs, stop boundary), durable package
pointer (exact external manifest/sealed-package identity), and durable
continuity (owning authoritative sources and recovery records).

Interface changes alone do not change durable executor identity or authority.
A distinct repository executor requires an explicit repository-execution
handoff covering repository, locality, tools, validation, delivery, and stop
boundaries. Shared chrome, project membership, history, branding, or folder
names do not prove context or authority transfer.

### Surface-transition check

At transitions, re-evaluate context sufficiency and materially changed source,
authority, locality, acting identity, tool, validation, output, or completion
boundaries. Retrieve newly activated owners; refresh mutable repository,
planning, and provider facts from their owners before use. Reuse still-current
verified context; the transition alone requires no blanket rehydration or
replay of unchanged doctrine.

### Thin semantic handoff envelope

A role-specific envelope may point to complete external recoverable state
instead of reproducing it. Include applicable semantic fields, not a package
schema: target surface/executor role; bounded outcome; exact self-describing governed
manifest/sealed-package identity; current human direction, bounded authority
declaration, live owning authority reference, and prohibited actions; mutable
sources to refresh from their owners; locality/tools; validation, outputs, and
completion/stop boundary.

Verify exact package identity under its owning contract before using the
payload; mutable directories or bare paths are navigation only. Envelopes create
no authority. If package identity or current authority is unavailable, stale,
mismatched, or ambiguous, stop affected execution; do not reconstruct from
conversation.

### Target-shaped projections

Use the matching target adapter: general bounded-executor envelopes emphasize
delegated outcome, permitted sources/tools, source refresh, output form, quality
checks, and return boundary; repository-executor envelopes additionally specify
repository identity/locality/tools, canonical validation, delivery, and stop
before merge.

## Explicit Kickoff Mutation Boundary

Every generated kickoff or orchestration prompt must declare the task-specific
mutation boundary under [core-model.md](core-model.md#kickoff-mutation-boundaries).
Blanket “read-only” or “no mutation on kickoff” language cannot replace actor,
phase, permitted/prohibited surfaces, prerequisites, and authority.

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

For fully read-only kickoff, state why and scope the actor, surfaces, and
duration. Permitted orchestration/evidence writes authorize neither delegated
substance nor human-gated transitions. Prompts and execution evidence create
zero authority.

This projection owns only the controller's declared boundary. Existing surface
routing, storage/admission, delivery/retention, cleanup/replay, and progress
contracts still apply. Prompt-contract machinery cannot drive lifecycle or
orchestration.

### Repository mutation and decision-boundary check

Before requiring implementation or Git mutation in a prompt, identify current
human direction or the narrower workflow that authorizes it. Apply
[repository mutation and decision boundaries](repo-readiness.md#repository-mutation-and-decision-boundaries).

Direct implementation-and-PR requests default to one focused branch/PR.
Materiality, design, or independent review may add a semantic boundary, not a
separate design document, staging branch, or proposal PR. Review the exact
implementation artifact when the owner permits it.

Discussion, design, specification, or review requests select review/audit or
orchestration/prompt-authoring without implementation topology. Separate repo
artifacts need explicit request or narrow workflow requirement; their authority
is distinct from later implementation. Recorded future intent is insufficient.

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

Keep prompt delivery small and deterministic. Resolve these decisions in order:

1. Classify the produced artifact.
2. Resolve the human operator or viewer and execution recipient independently.
3. Resolve the execution/handoff boundary under the existing
   [material-attempt and conversational-steering boundary](prompt-contracts.md#material-attempts-and-conversational-steering).
4. Qualify and select the applicable transport, then its presentation.

A concrete machine recipient alone does not create a durable handoff or require
transport qualification. Use the linked boundary to distinguish ordinary in-run
steering from fresh execution or revised-contract handoffs, independently of
visible thread reuse.

Wording such as `show me`, `give me`, or `prompt me` does not override a clearly
named machine recipient, including when the human manually launches its
downstream thread. An unresolved machine execution surface does not become a
human recipient.

- no prompt: no delivery action;
- conceptual fragment: lightweight conversational presentation;
- ordinary in-run steering to an already-active machine attempt: conversational
  inline delivery, using the canonical two-block presentation when complete;
  no new durable handoff;
- complete prompt for a human recipient: the canonical inline two-block
  presentation;
- qualifying small canonical-text prompt for a ChatGPT, Claude, or Codex
  machine recipient crossing an execution or handoff boundary with a permitted
  Airtable route: the Airtable record handoff below;
  or
- missing, unresolved, or mismatched required recipient, boundary, route,
  destination, or identity for a genuine handoff: a clear blocked result with
  no alternate renderer, after inspecting applicable unknown capability.

Do not use request wording, operator visibility, or an available file provider
to override the resolved recipient and route. A file provider is not a fallback
for a qualifying small canonical-text handoff. A separately authorized workflow
may select file-backed delivery only when its payload actually requires
arbitrary bytes or provider file identity, revision, or checksum behavior.

### Recipient-routing qualification cases

These cases exercise the decision model above. Tests validate their routing
relationships rather than the surrounding prose.

| Case | Produced artifact | Operator/viewer | Execution recipient | Downstream execution surface | Execution/handoff boundary | Route capability | Selected delivery |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `human-personal-use` | `complete` | `human` | `human` | `human` | `not-applicable` | `not-required` | `inline-two-block` |
| `cak-228-prompt-me-codex` | `complete` | `human` | `codex` | `codex` | `fresh-execution` | `permitted` | `airtable-thin-handoff` |
| `claude-executes` | `complete` | `human` | `claude` | `claude` | `fresh-execution` | `permitted` | `airtable-thin-handoff` |
| `chatgpt-executes` | `complete` | `human` | `chatgpt` | `chatgpt` | `fresh-execution` | `permitted` | `airtable-thin-handoff` |
| `cak-242-codex-correction` | `complete` | `human` | `codex` | `codex` | `in-run-steering` | `permitted` | `inline-two-block` |
| `cak-241-codex-correction` | `complete` | `human` | `codex` | `codex` | `in-run-steering` | `permitted` | `inline-two-block` |
| `claude-steering` | `complete` | `human` | `claude` | `claude` | `in-run-steering` | `unavailable` | `inline-two-block` |
| `chatgpt-steering` | `complete` | `human` | `chatgpt` | `chatgpt` | `in-run-steering` | `not-inspected` | `inline-two-block` |
| `reused-thread-revised-contract` | `complete` | `human` | `codex` | `codex` | `revised-contract-review` | `permitted` | `airtable-thin-handoff` |
| `machine-route-unavailable` | `complete` | `human` | `codex` | `codex` | `fresh-execution` | `unavailable` | `blocked` |
| `machine-identity-unresolved` | `complete` | `human` | `codex` | `codex` | `fresh-execution` | `identity-unresolved-after-inspection` | `blocked` |
| `conceptual-fragment` | `fragment` | `human` | `none` | `none` | `not-applicable` | `not-applicable` | `lightweight` |

`cak-228-prompt-me-codex` represents “Prompt me to have Codex do X,” including
manual thread creation: the human is the viewer or launcher, while Codex
receives and executes the complete prompt.

`identity-unresolved-after-inspection` means the required route or identity
remains unverified after the applicable capability inspection; an unknown route
that has not yet been inspected does not qualify for terminal blocking.

### Airtable canonical-text handoff

This section owns the shared handoff contract for the eligible machine
recipients named above. Adapters map its operations to concrete connector
actions without redefining it.

A handoff qualifies as small canonical text when the frozen payload fits
unchanged in one `Payload` long-text field and within the current connector's
single-record request and response limits. The permitted Airtable route owns
that runtime limit check. Payloads that do not qualify remain outside this
normal text route; they do not trigger a fallback from it.

After the decision model selects a genuine handoff, use one new Airtable record
per producer attempt with these required fields:

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

For a qualifying small canonical-text handoff to an eligible machine recipient,
apply the [Airtable contract](#airtable-canonical-text-handoff) and provide the
target-shaped thin envelope without reproducing the complete prompt in chat.
On success, return only the matching adapter's launch or configuration guidance
and required external envelope; do not replay the stored payload or routine
transport mechanics. For a human execution recipient, use the matching
adapter's canonical inline presentation. Inspect unknown connector capability
before selection; if the required Airtable route or identity is unavailable,
fail clearly rather than switching to file-backed delivery or reconstructing
the prompt in chat.

Prompt governance remains a separate selection. A material prompt that passes
its admission test additionally applies the
[`issue-owned durable rendered-prompt handoff profile`](prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile).
Complete that profile before reporting preservation or providing an
exact-identity handoff. Routine handoffs do not acquire material-prompt
governance merely because Airtable carries them.

### Current terminal presentation boundary

Repository routing and presentation rules do not hard-enforce the live ChatGPT
final response. Native ChatGPT remains **soft-only** for the two-block
invariant. Hard enforcement requires an owned display/emission surface or an
equivalent provider/client intercept before display.

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

Use this template for direct implementation. Resolve the executor metadata
through [Complete Prompt Shape](#complete-prompt-shape) and apply the
[complete-prompt rule](repo-readiness.md#interaction-mode-preflight).

```text
Task:
Implement [bounded outcome] in [repository].
Governing issue/source: [current task and authority reference]

State:
- [source locations and exact predecessor/input identities needed for this action]
- [required existing locality and whether acquisition/substitution is permitted,
  when correctness depends on a named checkout or supplied worktree]
- [unresolved dependency, if material]

[resolved thread-name section when applicable]
[minimal startup route if not already supplied by the receiving context]

Scope and constraints:
- [task-specific changes, exclusions, and overrides of repository defaults]

Acceptance:
- [observable behavior or evidence that establishes the result]
- [task-specific validation or delivery requirements, if not inherited]

[resolved task-appropriate kickoff mutation boundary when applicable]

Completion:
- [required result and stop boundary]
```

Resolve any applicable
[kickoff mutation boundary](#explicit-kickoff-mutation-boundary) from current
authority; retain its task-specific permissions and restrictions.

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

Use this template when the current deliverable is a downstream task envelope.
Resolve the executor metadata through
[Complete Prompt Shape](#complete-prompt-shape) and apply the
[complete-prompt rule](repo-readiness.md#interaction-mode-preflight).
Point to recoverable state instead of reproducing it.

```text
Task:
[bounded action and intended work layer] in [repository].
Governing issue/source: [current task and authority reference]

State:
- [authoritative source locations and exact predecessor/input identities]
- [required existing locality and whether acquisition/substitution is permitted,
  when correctness depends on a named checkout or supplied worktree]
- [unavailable context or unresolved dependency, if material]

[resolved thread-name section when applicable]
[minimal startup route if not already supplied by the receiving context]

Constraints:
- [task-specific scope, permissions, and exceptions to inherited rules]

[resolved task-appropriate kickoff mutation boundary]

Completion:
- [task-specific decision/acceptance criterion, required result, and stop boundary]
```

Resolve the
[kickoff mutation boundary](#explicit-kickoff-mutation-boundary) for the
receiving actor and phase. A source pointer does not replace an explicit
task-specific authorization or restriction.

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

Normal implementation delivery is inherited from the repository operating mode.
Use an add-on only for a task-specific delivery requirement or exception, such
as an existing PR to update or an explicitly local-only result; omit it when
current canonical owners already supply the requirement.

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
