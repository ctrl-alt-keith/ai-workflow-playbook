# Reusable Workflow Prompt Templates

This file holds reusable prompt shapes. Keep workflow rules in the core
playbook docs, Codex-specific execution guidance in `docs/tool-adapters/codex.md`,
and repo-local execution rules in `AGENTS.md`.

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

The name is an executor action, not an operator configuration. Put an exact
`Thread name` instruction in an applicable executable prompt; do not put a
`Recommended thread name` field in operator metadata. The operator is not
expected to set or copy the name manually, while the active executor can apply
it when its surface exposes that control.

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

Apply the instruction by route:

- `FRESH THREAD`: include the executable `Thread name` instruction and have
  the capable executor apply the exact name before substantive work.
- `CHILD TASK`: include it only when the child has its own separately visible,
  nameable thread or task and its execution surface can apply the name.
- `SAME THREAD`: preserve the established visible name unless an explicit
  rename is part of the task; do not inject a routine rename instruction.

If the execution surface cannot apply the name, continue the substantive task
and report that limitation. Naming failure is non-blocking because the name is
navigation only.

When rendering an applicable prompt, replace the thread-name placeholder with
the exact computed visible name. Do not ask the downstream executor to infer
or recover it from planning or repository context.

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

When rendering a complete Codex prompt inside a Markdown code fence, never
nest another Markdown code fence inside it. If the prompt needs an embedded
YAML, JSON, shell, Markdown, or other example, represent the example with
indentation and prefer plain text over Markdown formatting. Optimize the
finished prompt for reliable copy/paste across ChatGPT clients without changing
its meaning or execution.

## Quick Navigation

- [Codex Implementation Task](#codex-implementation-task)
- [Parallel Batch Add-On](#parallel-batch-add-on)
- [Orchestration Handoff](#orchestration-handoff)
- [Implementation Delivery Add-On](#implementation-delivery-add-on)
- [PR Review](#pr-review)

## Codex Implementation Task

Use this template only when the intended interaction mode is direct
implementation. For review or orchestration, use the matching template instead.
Apply the model-and-reasoning routing guidance in
[`tool-adapters/codex.md`](tool-adapters/codex.md#gpt-56-model-and-reasoning-routing)
to the bounded task. The first block below is operator metadata for the human
or operator. It is not part of the executable prompt and should not be copied
into the downstream agent. Copy or deliver only the second block. The second
block is complete without the metadata. Emit the two blocks consecutively with
no intervening heading or explanation.

```text
Operator metadata (do not include in prompt)
Thread routing: [FRESH THREAD | SAME THREAD | CHILD TASK]
Recommended model: [FRESH THREAD/CHILD TASK: executor adapter selection; SAME THREAD: Preserve requested thread model and observe effective runtime model]
Recommended reasoning/thinking: [FRESH THREAD/CHILD TASK: executor adapter selection; SAME THREAD: Preserve requested thread setting and observe effective runtime setting]

Reason:
[one concise task-specific explanation]
```

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

Thread name:
- Include this section for a FRESH THREAD; before substantive work, set this
  execution thread's visible name to: `[exact visible name]`.
- Include it for a CHILD TASK only when the child is separately visible and
  nameable; set that child's visible name to: `[exact child visible name]`
  before its substantive work.
- Omit this section for a SAME THREAD unless this task explicitly authorizes a
  rename; otherwise preserve the established visible name.
- If this surface cannot apply the name, continue and report the limitation;
  do not ask the operator to set it manually.

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
- Follow `docs/repo-readiness.md`, `docs/tool-adapters/codex.md`, and
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

Apply the model-and-reasoning routing guidance in
[`tool-adapters/codex.md`](tool-adapters/codex.md#gpt-56-model-and-reasoning-routing)
to the bounded task. The first block below is operator metadata for the human
or operator. It is not part of the executable prompt and should not be copied
into the downstream agent. Copy or deliver only the second block. Emit the two
blocks consecutively with no intervening heading or explanation.

```text
Operator metadata (do not include in prompt)
Thread routing: [FRESH THREAD | SAME THREAD | CHILD TASK]
Recommended model: [FRESH THREAD/CHILD TASK: executor adapter selection; SAME THREAD: Preserve requested thread model and observe effective runtime model]
Recommended reasoning/thinking: [FRESH THREAD/CHILD TASK: executor adapter selection; SAME THREAD: Preserve requested thread setting and observe effective runtime setting]

Reason:
[one concise task-specific explanation]
```

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

Thread name:
- Include this section for a FRESH THREAD; before substantive work, set this
  execution thread's visible name to: `[exact visible name]`.
- Include it for a CHILD TASK only when the child is separately visible and
  nameable; set that child's visible name to: `[exact child visible name]`
  before its substantive work.
- Omit this section for a SAME THREAD unless this task explicitly authorizes a
  rename; otherwise preserve the established visible name.
- If this surface cannot apply the name, continue and report the limitation;
  do not ask the operator to set it manually.

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

## Implementation Delivery Add-On

Append this only when the task is implementation mode and normal PR delivery is
expected.

```text
Delivery:
- Follow the branch, worktree, validation, and PR delivery rules in
  `docs/repo-readiness.md`, `docs/tool-adapters/codex.md`, and repo-local
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

Apply the model-and-reasoning routing guidance in
[`tool-adapters/codex.md`](tool-adapters/codex.md#gpt-56-model-and-reasoning-routing)
to the bounded task. The first block below is operator metadata for the human
or operator. It is not part of the executable prompt and should not be copied
into the downstream agent. Copy or deliver only the second block. Emit the two
blocks consecutively with no intervening heading or explanation.

```text
Operator metadata (do not include in prompt)
Thread routing: [FRESH THREAD | SAME THREAD | CHILD TASK]
Recommended model: [FRESH THREAD/CHILD TASK: executor adapter selection; SAME THREAD: Preserve requested thread model and observe effective runtime model]
Recommended reasoning/thinking: [FRESH THREAD/CHILD TASK: executor adapter selection; SAME THREAD: Preserve requested thread setting and observe effective runtime setting]

Reason:
[one concise task-specific explanation]
```

```text
Task:
Review pull request [pull_request] in [repository].

Inputs:
- Repository: [repository]
- Pull request: [pull_request]
- Task or issue context: [task_or_issue_context]
- Summary-only requested: [summary_only]

Thread name:
- Include this section for a FRESH THREAD; before substantive work, set this
  execution thread's visible name to: `[exact visible name]`.
- Include it for a CHILD TASK only when the child is separately visible and
  nameable; set that child's visible name to: `[exact child visible name]`
  before its substantive work.
- Omit this section for a SAME THREAD unless this task explicitly authorizes a
  rename; otherwise preserve the established visible name.
- If this surface cannot apply the name, continue and report the limitation;
  do not ask the operator to set it manually.

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
