# Codex Adapter

This adapter records Codex-specific deltas on top of the core playbook. Use it
with `docs/start-here.md`, `docs/core-model.md`, `docs/source-first-retrieval.md`,
`docs/repo-readiness.md`, and the target repo's `AGENTS.md`; do not treat it as
a second copy of those rules.

## Codex-Specific Quirks

- Codex can move quickly from brief to implementation, so phase boundaries need
  to be explicit.
- Codex works best with narrow tasks, named constraints, and a clear validation
  path.
- Codex can produce fluent summaries that still require source inspection and
  human judgment on scope, tradeoffs, and completion.
- Small tasks stay small when they extend an existing documented seam and avoid
  new abstractions unless clearly required.

## GPT-5.6 Sol Posture

GPT-5.6 Sol is the flagship GPT-5.6 role for complex reasoning and coding, not
a universal replacement for lower-cost or latency-sensitive model roles. For
Codex work using Sol, prefer a compact, outcome-oriented task envelope that:

- names the current work layer for a long task: research, design,
  implementation, review, or coordination
- states observable success criteria, constraints, dependencies, permissions,
  stop conditions, and the boundary of completion
- points to the governing playbook and repo-local sources instead of copying
  their doctrine into the prompt
- requires validation output or other direct evidence before completion is
  claimed

Do not add generic instructions such as "think step by step," "be thorough,"
or "minimize tool calls." Describe the outcome and evidence that matter. A
changed model string or a successful tool call is progress evidence, not proof
that the task is complete.

### Model And Prompt Updates

A model upgrade does not by itself justify a prompt rewrite. Preserve the
existing prompt and behavior first, establish a representative baseline, and
make only surgical prompt changes tied to an observed failure. When the
variables can be evaluated separately, do not change the model, prompt,
reasoning effort, tool behavior, and workflow at the same time.

Preserve the prior effective reasoning effort as the first migration baseline.
Treat reasoning effort as execution configuration rather than prompt prose,
then tune it against representative tasks. Do not recommend a global increase
or compensate for a configuration mismatch by bloating the prompt.

Keep Pro mode, persisted reasoning, programmatic tool calling, explicit prompt
caching, and multi-agent execution outside the baseline migration. Evaluate
each optional feature separately only when the workload shape and measured
results justify it. Preserve behavior and settings before optimizing.

### Reasoning-Level Recommendations

When the playbook produces or recommends a complete Codex prompt, precede the
executable prompt with this plain-text operator metadata:

```text
Recommended reasoning level: <Light | Medium | High>

Reason:
<one concise task-specific explanation>
```

Keep the metadata outside the executable prompt body, and begin that body
immediately afterward. When rendering Markdown, separate the metadata and
prompt body into consecutive code blocks with no intervening prose so the
operator can copy only the executable prompt.

Treat Light, Medium, and High as practical recommendation categories when the
execution surface does not provide more specific established terminology. The
recommendation is advisory, not a guarantee. Choose it from the bounded task
being handed off:

- High usually fits workflow or system architecture, ambiguous repository-wide
  design, synthesis across conflicting evidence, major refactoring with broad
  consequences, contract or recovery-point design, parallel-agent
  coordination, and work where mistakes would propagate into many later runs.
- Medium usually fits bounded evidence collection, integration against an
  established contract, structured analysis, normal implementation with
  meaningful judgment, and code review or repository changes of moderate
  complexity.
- Light usually fits mechanical or tightly bounded edits, formatting and
  cleanup, applying an approved change, straightforward validation or
  documentation updates, and work with explicit interfaces and acceptance
  criteria.

Use the task shape rather than the apparent size of the broader project. A
tightly scoped task may justify a lower level inside a complex project, while a
small-looking task may justify High when it establishes durable policy or
architecture. Execution runs can often use less reasoning than the design run
that established their contracts, while later synthesis may justify High even
when collection runs used Medium. Reconsider the recommendation whenever the
task changes materially.

Make the reason specific, concise, operational, and honest about the expected
benefit. Do not use promotional language or unverified claims about quality,
speed, cost, or correctness. A reasoning-level recommendation does not replace
a clear prompt, bounded scope, explicit contracts, validation, or safe stopping
conditions.

When a material prompt uses the semantic contract in
[`prompt-contracts.md`](../prompt-contracts.md), this operator metadata is the
Codex representation of the product-neutral `light`, `medium`, or `high`
reasoning class. The adapter must preserve whether that class and each required
capability are mandatory or advisory, the allowed degradation, and every
guarantee that may not be weakened.

Concrete Codex model names, service tiers, execution settings, and reasoning
knobs are adapter configuration and attempt-receipt metadata. They are not the
semantic meaning of the reasoning class. If the available Codex surface cannot
satisfy a mandatory capability or reasoning requirement without weakening a
guarantee, the attempt fails closed rather than silently choosing a weaker
setting.

This posture is derived from OpenAI's current
[GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model)
and [GPT-5.6 Sol model reference](https://developers.openai.com/api/docs/models/gpt-5.6-sol).

## Prompt-Contract Mapping

Codex is an executor representation, not the owner of shared prompt meaning.
For a versioned material prompt:

- preserve the immutable semantic contract and exact attempt-selected inputs;
- map product-neutral capabilities and reasoning class into supported Codex
  instructions and operator metadata;
- keep model, tier, tool, sandbox, and reasoning-knob selections in adapter
  configuration and the attempt receipt;
- preserve exact renderer-emitted prompt bytes across any allowed transport;
- do not treat a successful Codex run, validation result, receipt, checkpoint,
  or delivered prompt as authorization; and
- require the execution or adoption layer to re-read live durable authority
  and verify the acting identity immediately before action.

The Playbook artifacts
[`prompt-contract-semantic-anchors-v1.json`](../prompt-contract-semantic-anchors-v1.json)
and
[`prompt-contract-canonicalization-vectors-v1.json`](../prompt-contract-canonicalization-vectors-v1.json)
define shared anchors and conformance inputs. They do not implement a Codex
renderer, validator, receipt, or transport.

## Startup Deltas

Before repo-scoped work:

- Apply the domain-independent operating principles in
  [`core-model.md`](../core-model.md#operating-principles). The items below are
  Codex execution deltas, not a separate statement of those principles.
- Apply the interaction mode preflight in
  [`repo-readiness.md`](../repo-readiness.md#interaction-mode-preflight).
- Confirm the Codex project, execution container, current directory, and git
  state match the repository and branch or worktree named in the task.
- If the task targets a different repository, an unclear worktree, or a
  cross-repo comparison while the current context is repo-scoped, pause and
  confirm before editing.
- Apply the source-first retrieval model in
  [`source-first-retrieval.md`](../source-first-retrieval.md): retrieve or
  revalidate authoritative repository, PR, issue, file, CI, log, artifact, and
  external-state sources before relying on them.
- Apply the runtime verification rule in
  [`start-here.md`](../start-here.md#connector-availability-is-runtime-evidence);
  do not infer that a connector capability is absent because its tool has not
  been loaded or inspected. Before falling back to a direct service API or
  authenticated CLI for remote service state, determine whether the connector
  provides the required capability. Direct APIs and CLIs remain appropriate
  for verified connector gaps, repository-local workflows, or explicit
  repository policy.
- For policy-sensitive changes, apply the repo-family alignment check in
  [`repo-readiness.md`](../repo-readiness.md#repo-family-policy-alignment)
  before implementation.
- For governance, CI, release, or review-process changes, apply the governance
  operating model in
  [`repo-readiness.md`](../repo-readiness.md#governance-operating-model):
  distinguish safety and integrity protections from coordination overhead
  before proposing new gates or widening existing ones.
- Treat summaries, completion reports, memory, pasted descriptions, generated
  notes, and local branch state as navigation only until the relevant source
  has been inspected.
- If required source state is unavailable, report it as unknown or blocked
  instead of inferring from conversation.

Codex should not treat vague repair language as permission to mutate a repo
when the surrounding context indicates advisory review, audit, orchestration, or
prompt authoring. In ctrl-alt-keith workflows, ambiguous repo tasks default to
read-only review/audit or orchestration/prompt-authoring unless the human
explicitly asks Codex to implement, commit, push, or open the PR.

## Worktrees

The core isolation rule lives in
[`repo-readiness.md#pr-readiness`](../repo-readiness.md#pr-readiness): one
repository, one branch, one dedicated repo-local worktree, and one PR per
change.

Codex-specific application:

- Place repo-changing Codex worktrees under `<repo>/.worktrees/`.
- Before creating or reusing a repo-changing worktree, inspect `git worktree
  list` and choose a path that clearly belongs to the task.
- Create worktrees with direct `git worktree add` commands that name the full
  repo-local `.worktrees/<task-name>` path.
- Do not create `.worktrees/` with a separate `mkdir`; let `git worktree add`
  create the path or stop and report the failure.
- Reuse an existing worktree only when it clearly belongs to the same active
  task and its state is clean and intelligible.
- For same-repo parallel batches, keep lanes separated by file area, behavior
  surface, or risk surface; if overlap appears, pause and coordinate instead of
  forcing reconciliation.
- When cleanup is in scope, remove only the task worktrees and account for any
  blocked or deferred cleanup.

## Subagent And Worker Prompts

Use
[`orchestration-and-parallelism.md`](../orchestration-and-parallelism.md) for
the canonical decision model: default to one Codex thread for one coherent
review surface, fan out only when worker lanes are bounded before launch, and
keep integration or merge decisions with the orchestrator or human.

The ecosystem-level scaling direction prefers one top-level orchestration
prompt that delegates safe parallel work through explicit task envelopes. For
Codex, treat this as a compatibility constraint as well as a workflow
preference: some Codex execution surfaces reject or cannot reliably honor
requests for full-history conversation forking with explicit worker roles.

Codex prompts should therefore avoid asking workers to inherit the complete chat
history, parent-agent role, implicit project state, or hidden constraints. Do
not rely on phrases such as "fork this conversation" or "use the same role and
context as above" as the source of authority for worker behavior.

Prefer standalone worker prompts that include:

- repository and working directory
- interaction mode and expected deliverable
- goal, scope, and explicit exclusions
- relevant source evidence or retrieval instructions
- repo-family policy alignment expectations for policy-sensitive changes
- constraints, validation path, and stop conditions
- branch, worktree, file-surface, or non-overlap expectations
- reporting expectations for summary, validation, blockers, and residual risks

Worker authority stops at the assigned task envelope. A worker may implement,
validate, commit, and open or prepare the requested PR surface. It should not
merge, enable auto-merge, update other workers' branches, absorb unassigned
issues, or continue into downstream reconciliation unless the human explicitly
authorizes that specific step.

This is a Codex execution quirk, not a universal playbook rule. Other adapters
may describe different context-passing mechanisms when their execution surfaces
support them, but Codex orchestration should remain self-contained by default.

## Command Execution

Follow the command-form guidance in
[`repo-readiness.md#command-form-and-intent-visibility`](../repo-readiness.md#command-form-and-intent-visibility).

Codex-specific application:

- Prefer direct `git`, `gh`, `make`, `python`, repo-local script, and tool
  invocations for ordinary repository work.
- Where the execution surface supports native argv-style execution, use it for
  `git` and `gh`.
- If the execution surface defaults to a shell or login shell, disable that
  wrapper where supported for ordinary `git` and `gh` commands.
- Use shell wrapping only when the command genuinely needs shell semantics, and
  keep the wrapped operation narrow enough for review and approval surfaces to
  see the intended action.

### Enforcement-Backed Recursive Cleanup

Direct `rm` and `rm -rf` remain approval-gated. When recursive cleanup is
appropriate and every target is already known to be a disposable directory
beneath the current repository worktree, prefer the reviewed enforcement
control:

```sh
/Users/keith/.local/bin/codex-safe-rm -rf -- TARGET [TARGET ...]
```

The control validates the fixed invocation grammar and every operand, enforces
containment beneath the invocation working directory, rejects `.git`, prevents
symlink escape, rejects top-level files and symlinks, and safely ignores missing
directories. The implementation, threat model, installation and verification
workflow, rule fixture, and tests belong to
[`ai-workflow-enforcement`](https://github.com/ctrl-alt-keith/ai-workflow-enforcement/blob/main/docs/codex-safe-rm.md);
do not reproduce those mechanics in the playbook.

The control establishes invocation and containment safety. It does not decide
whether a directory is disposable. Do not use it to bypass approval when a
target is uncertain, valuable, or part of a broader destructive operation.
Human judgment still owns what may be deleted.

Installation, verification, and activation through Codex rules are separate
operator steps. The presence of this guidance does not make the helper a
prerequisite for every Codex workflow. If the reviewed control is unavailable
or not activated, keep recursive removal approval-gated rather than substituting
an unreviewed wrapper.

## GitHub And PR Evidence

- Before repo- or PR-dependent work, verify GitHub access instead of relying on
  cached context, summaries, or local branch state.
- When a task asks Codex to review, check, assess, approve, or comment on a PR,
  follow the connector-first rule in
  [`review-packet.md#direct-pr-inspection`](../review-packet.md#direct-pr-inspection).
- Local checkout state, `git diff`, and `gh` output may supplement PR review
  after connector inspection, but they do not replace it.
- If required connector or `gh` access is unavailable, stop and report the
  access blocker instead of inferring remote state.
- Do not claim mergeability, required checks, or branch-protection state without
  current PR or repository evidence.

## Independent Reviewer Invocation

Apply the provider-neutral review modes in
[`external-ai-reviewer.md`](../external-ai-reviewer.md). When governed
independent review is selected, Codex should prefer direct invocation against
the exact repository artifact with narrowly scoped read-only source access over
human copy-and-paste transport when the execution surface supports it. Claude
is one possible reviewer implementation; it is not the shared semantic
requirement.

Before invocation, bind the brief to the exact path, commit, or byte identity
and name the decision boundary, review dimensions, authoritative sources,
prohibited mutations, and stop conditions. Require the reviewer to report its
identity, tools and access, sources actually inspected, material capability
gaps, source attribution, anchored findings with severity, and explicit
verdict. Preserve the output at a reviewable identity.

After review, Codex must not turn a verdict into approval. Use the finding
disposition and re-review applicability contract in
[`review-packet.md`](../review-packet.md#independent-review-findings-and-re-review).
If the reviewer declares a material source-access gap, Codex may close it only
through an authorized connector or tool. Record the actor that verified each
source and keep the original capability gap visible; do not rewrite the record
as though the reviewer performed that verification.

## Workflow-State Progress Rendering

This is the Codex rendering of the general principle to make material phases
and next permitted actions legible; it does not redefine that principle. For
material proposal-first or multi-stage work, report observable workflow state
instead of narrating model activity. Keep updates concise and include only what
helps the human understand or verify the current boundary:

- current phase and exact artifact identities;
- satisfied prerequisites and the evidence that satisfied them;
- substantive findings, disposition counts, and unresolved findings;
- material capability gaps and actor-to-source verification attribution;
- invariants and scope exclusions that remain preserved;
- unmet transition criteria; and
- the exact next permitted action or stop condition.

Successful tool calls, model output, validation, and progress text are evidence
of activity, not proof of completion or authority. Re-read current sources at
source-first and post-merge boundaries rather than rendering stale planned
state. Do not expose or request private chain-of-thought; workflow progress is
grounded in artifacts, source state, decisions, validation, and receipts.

## External API Claims

When code, tests, docs, risks, or user-facing claims depend on external public
API behavior, apply the engineering baseline's official-source expectation.
For Codex, that means checking official docs, references, changelogs, or release
notes when tool access is available instead of relying on model memory.

## Local Permissions

Codex runs inside a local permissions model. Some actions require approval,
especially network access, privileged writes, destructive commands, and
worktree cleanup that updates Git metadata outside the visible worktree path.

If a task depends on elevated access, surface that early and keep the requested
action narrowly scoped. If sandbox boundaries matter, inspect the effective
policy with:

```sh
codex debug prompt-input effective-sandbox-check
```

In `workspace-write` mode, effective writable roots may include more than the
explicit `[sandbox_workspace_write].writable_roots` list. Codex can also expose
the current trusted project root, `/tmp` as `/private/tmp` on macOS, and the
Darwin `$TMPDIR` under `/private/var/folders/.../T`. Removing paths from
`writable_roots` does not remove those implicit temp roots.

When stricter isolation should exclude implicit temp roots, use the dedicated
sandbox flags and keep `writable_roots` for durable paths that must remain
writable:

```toml
[sandbox_workspace_write]
exclude_slash_tmp = true
exclude_tmpdir_env_var = true
writable_roots = [
  "/ABSOLUTE/PATH/TO/TRUSTED/WORKSPACE/.codex/automations",
  "/ABSOLUTE/PATH/TO/TRUSTED/WORKSPACE/.codex/sessions",
]
```

Verify the effective policy with both the normal config and an empty explicit
override:

```sh
codex debug prompt-input effective-sandbox-check
codex debug prompt-input -c 'sandbox_workspace_write.writable_roots=[]' effective-sandbox-check
```

Confirm the project root and intended durable roots remain writable, while
`/private/tmp` and `/private/var/folders/.../T` are absent when the exclusion
flags are enabled. Some tools need a writable temp directory; when implicit
temp roots are excluded, configure those tools to use a repo-local temp path
inside the effective sandbox or expect failures from compilers, archives,
caches, and other temp-file users.

Use repo-local scratch paths for workflow artifacts that need review later. Use
temporary OS paths only for short-lived process-local files whose path and
contents do not matter after the command finishes.

## Autonomous Lane

Codex should continue without pausing when the scope is clear, the repo context
matches the task, required sources are available, validation can run, and no
human-gated decision is next.

Routine cleanup of known disposable repo-local directories through the reviewed
`codex-safe-rm` control is an enforcement-backed operation within this lane; it
is not an arbitrary destructive command. This does not delegate the decision
that a target is disposable. Do not use autonomy to widen scope, reinterpret
intent, or take ownership of merge, release, tag, uncertain deletion,
security-sensitive, permissions-sensitive, or policy-interpretation decisions.

## Stop Conditions

Pause and ask for human input when:

- the repo, project, branch, or worktree context appears wrong
- the requested scope is ambiguous or has shifted
- required source state cannot be retrieved or verified
- more than one valid path exists and the choice depends on human judgment
- validation fails in a way that suggests broader work than requested
- the next step is merge, release, tag, destructive, externally visible, or
  permissions-sensitive
- the work touches sensitive auth, secrets, permissions, or policy
  interpretation

## Delivery Notes

Use the PR readiness, validation, and delivery rules in
[`repo-readiness.md`](../repo-readiness.md) and repo-local `AGENTS.md`.

When reporting completion for Codex implementation work, include the PR link
when one was opened or updated, files changed, validation results, and any
known blockers or residual risks.
