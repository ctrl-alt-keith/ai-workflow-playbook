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

When Chat is the current interactive surface, use it as the normal control
plane for human-led clarification, scoping, authority decisions, decomposition,
steering, review, and disposition. Keep hard reasoning in Chat while that
semantic role remains interactive. Move work only after a bounded outcome and
execution contract have emerged:

- choose Work for a bounded general-purpose multi-step outcome or
  non-repository deliverable;
- choose Codex when completion materially depends on repository locality,
  terminal commands, tests, Git, worktrees, commits, pull requests, or code
  review; and
- keep work in Chat when the next useful result is discussion, judgment,
  clarification, steering, or review rather than delegated execution.

Select by semantic role, execution locality, required tools, and deliverable.
Difficulty, model tier, and reasoning setting do not select a surface. Chat is
the normal interactive controller, not a mandatory mediator for every
automated or independently initiated workflow, a universal authority, a
canonical record, or a project system of record. Ordinary chat, brainstorming,
and conceptual discussion remain lightweight and do not inherit repository
ceremony.

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

Moving between Chat and Work does not create a new durable executor identity or
authority contract merely because the interface changed. Moving to Codex is a
distinct repository-execution handoff and must make repository, locality,
tools, validation, delivery, and stop boundaries explicit. Shared application
chrome, project membership, conversation history, product branding, or a
folder name does not prove that context or authority transferred.

### Surface-transition check

At a surface transition, re-evaluate context sufficiency and any materially
changed source, authority, locality, acting identity, tool, validation, output,
or completion boundary. Retrieve newly activated owners and refresh mutable
repository, GitHub, planning-system, and provider facts from the systems that
own them before relying on those facts. Reuse still-current verified context;
a surface change does not require blanket rehydration or replay of unchanged
doctrine.

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

Shape the thin envelope for the selected target rather than sending a generic
prompt.

For Work, emphasize the delegated outcome, permitted connected sources and
tools, source refresh, output form, quality checks, and return boundary:

```text
Target: Work — bounded general-purpose outcome
Outcome: [source-backed non-repository deliverable]
Governed payload: [exact manifest or sealed-package identity]
Human direction and authority: [bounded declaration, owning reference, prohibitions]
Refresh: [mutable sources to retrieve from their owners]
Tools and locality: [permitted connected sources and execution location]
Validation and output: [quality checks and deliverable form]
Return boundary: [return to Chat for review or stop condition]
```

For Codex, emphasize repository execution, exact locality, terminal and Git
tools, canonical validation, delivery, and the stop-before-merge boundary:

```text
Target: Codex — repository execution
Outcome: [bounded repository change or review]
Repository and locality: [repository, worktree, branch, relevant surface]
Governed payload: [exact manifest or sealed-package identity]
Human direction and authority: [bounded declaration, owning reference, prohibitions]
Refresh: [repository, GitHub, planning, and provider facts to re-read]
Tools: [terminal, tests, Git, worktrees, commits, PR, or code review as applicable]
Validation and delivery: [canonical command, outputs, commit/push/PR expectation]
Stop boundary: [including no merge or other prohibited transition]
```

### Examples

1. **Difficult architecture discussion remains in Chat.** The human and Chat
   are still comparing authority boundaries and tradeoffs. No bounded
   deliverable or execution contract exists, so difficulty does not trigger a
   move to Work or Codex.
2. **Source-backed report moves from Chat to Work.** Chat establishes the
   question and authority boundary, then sends a Work-shaped envelope for a
   cited report with `Governed payload: [immutable manifest path plus exact
   digest or file identity]`, current source-refresh instructions, output
   checks, and return-to-Chat boundary. It does not paste the recoverable
   package into the conversation.
3. **Repository implementation moves from Chat to Codex.** Chat establishes a
   bounded repository outcome, then sends a Codex-shaped envelope naming the
   repository and worktree expectations, terminal and Git tools, canonical
   validation, PR delivery, stop-before-merge boundary, and `Governed payload:
   [exact sealed-package identity]`.
4. **Discussion becomes delegated execution.** A task begins in Chat as an
   open-ended product discussion. It stays there until the human selects a
   bounded comparison report with accepted sources and review criteria; only
   then does it move to Work.
5. **Worker result returns to Chat.** Work returns the report identity,
   validation evidence, limitations, and output—not new authority. Chat is
   again the interactive surface for human review, interpretation,
   disposition, or next-step selection.
6. **Package reference fails closed.** A target receives only a mutable folder,
   or the named manifest is inaccessible, stale, digest-mismatched, or
   ambiguous. It stops the affected work or reports a non-authorizing partial
   result without rebuilding the missing payload from conversation memory.

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

- [`prompt-contract-semantic-anchors-v1.json`](prompt-contract-semantic-anchors-v1.json)
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

## Quick Navigation

- [Task-Shape Surface Selection And Thin Handoffs](#task-shape-surface-selection-and-thin-handoffs)
- [Repository Implementation Task](#repository-implementation-task)
- [Parallel Batch Add-On](#parallel-batch-add-on)
- [Orchestration Handoff](#orchestration-handoff)
- [Governed Artifact Capture Add-On](#governed-artifact-capture-add-on)
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
```

Required inputs:

- `repository`
- `working_directory`
- `canonical_source`
- `source_evidence`
- `interaction_mode`
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
- Completion ends at: [artifact, review packet, PR, report, or other]

Stop rules:
- Stop before merge, release, tag, destructive, externally visible, or
  permissions-sensitive actions unless explicitly authorized.
- Ask for human input when required evidence is unavailable or the next step
  depends on a human judgment call.
```

## Governed Artifact Capture Add-On

Append this only when the producing task's owning workflow activates
[`evidence-lifecycle.md#governed-artifact-capture`](evidence-lifecycle.md#governed-artifact-capture).
Name that workflow and any narrower storage constraints. After storage
admission, capture the complete artifact directly, verify its exact identity,
leave the proportionate permitted producing receipt, and return only a compact
conversation summary. The add-on grants no acceptance or downstream authority.

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
- Do not mutate the PR unless explicitly asked.
- If required PR evidence is unavailable, state that blocker and caveat any
  feedback from already-present information.

Output format:
1. Review findings: severity-ordered findings with file or PR references where
   possible.
2. Scope and evidence notes: inspected PR surface, checks, mergeability, and
   task fit.
3. Recommendation: `ready to merge`, `needs decision`, or `blocked`, only when
   direct PR evidence supports it.
```
