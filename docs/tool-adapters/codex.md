# Codex Adapter

This adapter records Codex-specific deltas on top of the core playbook. Apply
it to Codex runs wherever Codex is the selected executor. The adapter boundary
follows the selected Codex run or executor and does not depend on how a
particular client packages that surface. It records the specialized repository
mechanics for that distinct run/executor boundary. Use it with `docs/start-here.md`,
`docs/core-model.md`, `docs/source-first-retrieval.md`,
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

## GPT-5.6 Model And Reasoning Routing

Choose the lowest-cost GPT-5.6 model and reasoning effort that preserves the
confidence required by the bounded task. Model selection and reasoning effort
are separate configuration decisions: select both deliberately, and do not
default substantial work to Sol merely because it is long-running.

The current official positioning, checked 2026-08-10, is: Sol for frontier
capability, Terra for an intelligence/cost balance, and Luna for efficient,
high-volume, cost-sensitive workloads. GPT-5.6 supports `none`, `low`,
`medium`, `high`, `xhigh`, and `max` reasoning effort; availability of a
specific combination remains executor/runtime evidence. This adapter uses
Light, Medium, and High as portable recommendation classes, mapped to the
available runtime setting by the operator.

Use task characteristics, not duration, to route: ambiguity, consequence of
error, repository-context breadth, novelty, architectural judgment,
reversibility, reviewer role, repetition/volume, and strength of independent
validation. A short task can still require Sol; a long deterministic task can
remain on Luna.

| Task class | Default model | Default reasoning | Escalate when | Downgrade/delegate when |
| --- | --- | --- | --- | --- |
| Status hydration; Git/Linear checks; inventories/hashes; test or lint invocation; formatting; bounded mechanical verification; evidence-only packaging | Luna | Light | the result is ambiguous, fails unexpectedly, or changes a decision | split data collection and repeatable checks from interpretation |
| Deterministic file edits or docs cleanup with explicit acceptance criteria; routine PR publication | Luna | Medium | semantics, scope, or validation expectations are unclear | Terra/Sol parent delegates the bounded edit or delivery plumbing |
| Localized bug fix; routine implementation; normal PR work; CI debugging with a legible failure; frozen-controller test changes; evidence interpretation | Terra | Medium | repeated attempts fail, an invariant cannot be explained, or cross-system scope appears | delegate lint, hashes, fixture runs, and evidence packaging to Luna |
| Substantial but bounded analysis; moderate synthesis; difficult localized debugging | Terra | High | architecture or authority decisions, conflicting evidence, or unresolved ambiguity remain after bounded investigation | move deterministic execution and verification to Luna |
| Protocol/design work; architecture synthesis; ambiguous root-cause debugging; high-consequence authority or controller semantics; difficult adversarial review | Sol | High; consider `xhigh` or `max` only with a measured need | use a bounded supported Pro-mode execution, independent review, or explicit human decision when the unresolved risk remains material | delegate established-contract implementation to Terra and mechanical verification to Luna |

Defaults are routing hypotheses, not a guarantee that the lower-cost choice is
sufficient. Do not downgrade when consequences are high, ambiguity is
material, validation is weak, work is hard to reverse, or a failure could
silently corrupt authority or evidence. `xhigh` and `max` are exceptional:
use them only for a bounded demanding task with an observed quality need; do
not promote them to a routine default.

OpenAI documents Pro mode as a distinct Responses API execution mode: it keeps
the selected GPT-5.6 model, chooses effort independently, and applies more
model work for difficult quality-first tasks. Use it only where the runtime
exposes it and a bounded quality/reliability need justifies the added cost and
latency; it is not a routine Sol default. The `gpt-5.6` alias resolves to Sol,
so use an explicit Terra or Luna identifier whenever that lower-cost routing is
intended.

### Escalation And Delegation

Escalate a lower-cost task only on evidence: unresolved ambiguity after a
bounded investigation, an architecture decision, conflicting authorities,
a high-consequence security/authority decision, repeated failed attempts, an
unexplained invariant, or a reviewer finding that changes the methodology
rather than the implementation. Prefer a bounded Sol subtask for that question
over restarting the entire workflow on Sol when the execution topology allows
it.

A stronger parent should delegate deterministic, independently checkable work
downward when supported: Sol architecture to Terra implementation; Sol or Terra
to Luna for lint, hashes, inventories, fixture execution, and evidence
packaging. Preserve each child's selected model, reasoning effort, bounded
inputs, execution identity, durable result, and authority boundary in the
attempt evidence when the workflow requires it. A child spawned by the reviewed
party is not an independent external reviewer; this does not invalidate child
work for other purposes.

### Thread Routing And Configuration Continuity

Apply the shared `FRESH THREAD`, `SAME THREAD`, and `CHILD TASK` vocabulary in
[`prompts.md`](../prompts.md#thread-routing-and-configuration-continuity). For
a FRESH THREAD, select the matrix's task-appropriate GPT-5.6 model and effort.
For a SAME THREAD, preserve the requested parent model and effort by default:
task-class sufficiency alone does not justify intentionally mutating an
already-running configuration. Record the effective model and effort separately
when the runtime exposes them, along with any fallback or substitution event.
For a CHILD TASK, independently select the lowest-cost sufficient model and
effort for that bounded child and retain the child evidence required by the
governing workflow.

If a lower-capability SAME THREAD encounters an escalation trigger, delegate
the unresolved question to a bounded stronger child or make an explicit
fresh-thread transition where supported; do not silently mutate the parent. If
a stronger SAME THREAD reaches mechanical follow-up, it may delegate lint,
hashes, inventories, fixture execution, or evidence packaging to a cheaper
child without changing the parent. This default preserves context and decision
continuity, reproducibility, execution provenance, and qualification
boundaries; it does not claim that an in-thread configuration change necessarily
harms quality.

For reviews, preserve reviewer independence separately from model capability.
Keep the selected substantive external reviewer (for example, qualified Claude)
when the review contract requires it. Internal or mechanical review follows
this matrix; Sol is not automatic for a narrow, deterministic fallback.

### Visible Thread Names

Apply the shared visible-thread-name meaning and naming syntax in
[`prompts.md`](../prompts.md#executor-applied-visible-thread-names). Codex is
currently the Playbook adapter that establishes executor-applied visible-thread
naming capability. For a Codex-targeted `FRESH THREAD`, or an eligible
separately visible Codex `CHILD TASK`, resolve the shared
`[resolved thread-name section when applicable]` placeholder to this exact
section with the computed name. Resolve it to nothing for an ordinary `SAME
THREAD` unless an explicit rename is part of the task.

```text
Thread name:
- Before substantive work, set this thread's visible name to: `[exact visible name]`.
- If this surface cannot apply the name, continue and report the limitation;
  do not ask the operator to set it manually.
```

When this section is present and the active Codex surface exposes a visible-name
control, Codex applies that exact name itself before substantive work. If the
control is unavailable, Codex continues the substantive task and reports the
limitation; naming remains non-blocking and navigation only.

The CAK-106 experience supports this split as observed workflow evidence, not
a benchmark: protocol ambiguity, authority architecture, controller semantics,
and architecture synthesis justified stronger reasoning, while repeated focused
validation, hashes/inventories, Git checks, fixture execution, evidence
packaging, and review-follow-up plumbing were plausible Terra or Luna work. Do
not infer quantitative savings without measured usage evidence.

For a Codex task using any selected model, prefer a compact, outcome-oriented
task envelope that:

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

## Goal Mode

Goal mode is Codex persistence and execution control for one bounded,
verifiable outcome. Construct it from the existing outcome-oriented task
envelope and route its task, authority, source-refresh, and (when activated)
material-prompt requirements to [`core-model.md`](../core-model.md),
[`start-here.md`](../start-here.md),
[`source-first-retrieval.md`](../source-first-retrieval.md),
[`prompts.md`](../prompts.md), and
[`prompt-contracts.md`](../prompt-contracts.md); it does not create a second
contract.

Goal state, completion, or successful validation is execution evidence, not
human acceptance, approval, merge, release, publish, adoption, or downstream
continuation authority. When scope, workflow, authoritative-source
requirements, execution locality, completion boundary, or authority changes
materially, re-evaluate the current activation, source-refresh, and authority
requirements. Edit, replace, pause, or clear stale Goal state as appropriate;
do not let it silently drive continuation under an obsolete task contract.

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

### Operator Metadata And Reasoning Recommendations

When the playbook produces or recommends a complete Codex prompt, precede the
executable prompt with this plain-text operator metadata:

```text
Thread routing: <FRESH THREAD | SAME THREAD | CHILD TASK>
Recommended model: <FRESH THREAD/CHILD TASK: GPT-5.6 Luna | GPT-5.6 Terra | GPT-5.6 Sol; SAME THREAD: Preserve requested thread model and observe effective runtime model>
Recommended reasoning level: <FRESH THREAD/CHILD TASK: Light | Medium | High; SAME THREAD: Preserve requested thread setting and observe effective runtime setting>

Reason:
<one concise task-specific explanation>
```

Keep the metadata outside the executable prompt body, and begin that body
immediately afterward. When rendering Markdown, separate the metadata and
prompt body into consecutive code blocks with no intervening prose so the
operator can copy only the executable prompt.

This metadata is operator guidance, not task authority. The recommendation is
advisory, not a guarantee. Interpret FRESH/SAME routing before prompt delivery:
do not tell downstream Codex to change or preserve its parent model or
reasoning level when it lacks that control. The executable task body remains
complete without metadata and includes child-dispatch instructions only when
the active Codex surface can perform that bounded delegation. Runtime-model
facts may remain in the task body when the task must record or validate them.
Choose the model and effort from the bounded task being handed off, using the
routing matrix above. Light, Medium, and High are practical recommendation
categories when the execution surface does not provide more specific
established terminology:

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
and [OpenAI models reference](https://developers.openai.com/api/docs/models),
checked 2026-08-10.

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

The current Playbook artifacts
[`prompt-contract-semantic-anchors-v2.json`](../prompt-contract-semantic-anchors-v2.json)
and
[`prompt-contract-canonicalization-vectors-v1.json`](../prompt-contract-canonicalization-vectors-v1.json)
define shared anchors and conformance inputs. They do not implement a Codex
renderer, validator, receipt, or transport.

### Issue-Owned Durable Prompt Retrieval

Apply the shared
[`issue-owned durable rendered-prompt handoff profile`](../prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile)
when Codex receives an exact issue-owned prompt. Prefer direct retrieval only
when the current connector or provider route exposes raw bytes and the required
provider identity metadata and that exact route has been qualified for the
attempt. A connected account, extracted text, local synchronization, or a
successful prior call does not prove exact-byte retrieval.

When direct retrieval is unavailable or unqualified, the controller or operator
may download the raw provider object once into a private OS-managed
attempt-local directory, verify the provider identity and raw bytes, and pass
Codex the exact local path plus expected size and SHA-256. Codex verifies the
consumed local bytes and declared text format before acceptance. Do not use a
locally synchronized provider mount as provider identity, treat the local
retrieval as durable, or create an exchange root.

Record the delivery operation and Codex attempt separately from the durable
prompt. Distinguish `DELIVERED`, `ACCEPTED`, `STARTED`, and the terminal
attempt outcome rather than inferring one from another. Preserve required
evidence, then remove and verify removal of only the attempt-local retrieval
after the attempt no longer depends on it. The concrete provider, account,
namespace, issue locator, retention, and visibility policy stay in their project
or storage owner, not this adapter. Revalidate containment and identity, and
fail closed on the shared cleanup conditions in
[`repo-readiness.md`](../repo-readiness.md#repo-local-workflow-state).

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
- For GitHub hydration and ordinary source-first retrieval, treat `gh api` as
  a direct-service-API fallback rather than the default retrieval primitive.
  Do not select it only because the REST endpoint is flexible or familiar. Use
  an available GitHub connector when it provides the required source, or the
  narrowest high-level `gh` command when that is the appropriate direct
  repository CLI. If neither provides the required capability, keep `gh api`
  read-only and scoped to the required state unless the current task separately
  authorizes mutation. This avoids unnecessary approval friction; it does not
  create a human approval gate or prohibit `gh api` when it is the narrowest
  available way to retrieve authoritative state.
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

Before child dispatch, the controller resolves current startup activation for
the bounded child task, establishes the repository floor, resolves every
child-activated canonical owner or source, and identifies exact source or
evidence identities when required. The controller places the selected
references or bounded retrieval instructions in the child envelope and retains
ownership of the judgment that the context and source set is sufficient.

Prefer standalone worker prompts that include:

- repository and working directory
- interaction mode and expected deliverable
- goal, scope, and explicit exclusions
- relevant source evidence or retrieval instructions
- repo-family policy alignment expectations for policy-sensitive changes
- constraints, validation path, and stop conditions
- branch, worktree, file-surface, or non-overlap expectations
- reporting expectations for summary, validation, blockers, and residual risks

The child may retrieve exact controller-selected sources, inspect its bounded
assigned repository, issue, PR, or file surface, and report unavailable,
stale, conflicting, or insufficient named sources or a newly encountered
workflow or source activation trigger. It may not turn "read whatever you
need" into self-authorized broad hydration; certify sufficiency from
confidence, task success, inherited full, partial, or no conversation history,
visible files, filesystem access, tool access, or successful retrieval; or
silently widen the source set, workflow, scope, or authority.

When a child encounters a newly activated owner or source, it reports the
trigger under its stop/report contract. The controller re-runs activation
routing and sends a bounded follow-up, reissues the task, handles the work
directly, or stops the lane; the child does not independently widen itself and
declare the new set sufficient.

Worker authority stops at the assigned task envelope. A worker may implement,
validate, commit, and open or prepare the requested PR surface. It should not
merge, enable auto-merge, update other workers' branches, absorb unassigned
issues, or continue into downstream reconciliation unless the human explicitly
authorizes that specific step. Context transfer, sandbox or permission
inheritance, filesystem visibility, and execution capability do not widen this
authority. Reconciliation remains controller-owned under
[`orchestration-and-parallelism.md`](../orchestration-and-parallelism.md).

This is a Codex execution quirk, not a universal playbook rule. Other adapters
may describe different context-passing mechanisms when their execution surfaces
support them, but Codex orchestration should remain self-contained by default.

## Command Execution

Follow the command-form guidance in
[`repo-readiness.md#command-form-and-intent-visibility`](../repo-readiness.md#command-form-and-intent-visibility).

Codex-specific application:

- Use the narrowest Codex execution primitive that directly represents the
  intended operation. Prefer a native filesystem or tool operation when one is
  available; otherwise prefer direct argv-style executable invocation where
  the execution surface supports it.
- Prefer direct `git`, `gh`, `make`, `python`, repo-local script, and tool
  invocations for ordinary repository work. Apply the same directness to simple
  filesystem operations such as directory creation or file inspection.
- Do not introduce `zsh`, `bash`, `sh`, login-shell wrappers, `-c` wrappers, or
  equivalent general-purpose shell execution merely for convenience when the
  operation can be represented directly. This keeps approvals and audit
  records scoped to the specific operation instead of widening them to a
  general-purpose shell.
- If the execution surface defaults to a shell or login shell, disable that
  wrapper where supported for direct executable commands.
- Use shell wrapping only when the operation genuinely needs shell semantics,
  such as pipelines, redirection, command substitution, conditionals, or
  necessary shell expansion that cannot reasonably be represented directly.
  Keep the wrapped operation narrow enough for review and approval surfaces to
  see the intended action.

### Shell-Only Execution Surfaces

Some Codex execution surfaces expose a shell command string even when Codex
selected a simple direct operation. A fixed non-login runner such as `zsh -c`
may therefore appear in executor logs. This transport detail does not authorize
agent-authored shell wrappers, weaken command-form preflight, or grant an
approval exemption.

Continue to select the narrowest direct operation and disable login-shell
semantics where the surface exposes that setting. If a static, contained
filesystem operation still prompts because the surface exposes no native or
argv-style primitive, treat that as a runtime approval limitation. Do not
compensate by adding a broad `mkdir` or `mkdir -p` prefix allow rule: prefix
matching cannot establish containment for every operand or resolved path.
Preserve approval or fail closed, and report the runtime limitation.

### Child-Process Login Identity

When Codex launches a child CLI whose authentication or runtime behavior
depends on login identity, give the child an environment consistent with the
effective operating-system user. Inspect the effective identity and the
inherited environment separately; a matching `HOME` does not make an unset or
conflicting `USER` and `LOGNAME` safe to propagate.

Normalize identity-sensitive variables to the effective user for the bounded
child invocation or through the applicable Codex environment policy. Do not
hard-code a workstation username into reusable commands or configuration, and
do not force this normalization on child CLIs without evidence that their
behavior depends on login identity.

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

This is the Codex rendering of the core model's
[`Operator Observability`](../core-model.md#operator-observability) guidance; it
does not redefine that guidance. For material proposal-first or multi-stage
work, report observable workflow state instead of narrating model activity.
Keep updates concise and include only what helps the human understand or verify
the current boundary:

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

## Governed Artifact Capture

Apply the shared contract in
[`evidence-lifecycle.md#governed-artifact-capture`](../evidence-lifecycle.md#governed-artifact-capture);
this adapter only projects it onto Codex execution. Before retaining bytes,
use source-first retrieval to verify the candidate and the owning workflow's
storage admission, destination, and narrower constraints.

After admission, use one writer and exclusive no-overwrite creation. Read the
result back immediately and verify exact bytes, size, SHA-256, declared text
format, final-newline state, and containment where applicable. Report exact
capability gaps. Describe distinct evidence as `evidenced separately` without
implying an independent actor.

Select the smallest permitted durable append-only producing-receipt surface
that remains sufficient for recovery. Return a compact conversation summary;
chat is not the producing receipt. Do not substitute chat, scratch, unverified
transport, or a Git commit for required durable retention.

This adapter owns no artifact taxonomy, storage destination, planning state,
provider state, or human decision. Capture and receipt evidence transfer zero
authority.

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
flags are enabled. Some tools need a writable temporary directory; when
implicit temp roots are excluded, configure them only under a separate,
explicit repository or tool ownership contract, or expect failures from
compilers, archives, caches, and other temp-file users. A helper API or
environment variable selects allocation mechanics; it does not establish that
ownership or authority.

Use the natural durable or repository-owned path for workflow artifacts that
need review later. Use attempt-local scratch only for short-lived private
process mechanics whose loss cannot impair recovery; the shared lifecycle
contract is in [`repo-readiness.md`](../repo-readiness.md#repo-local-workflow-state).

### Qualified Direct Claude Code Path

Direct Claude Code execution from Codex under `workspace-write` has a narrower
qualified runtime contract in addition to the general child-process guidance:

For an automated, non-interactive Claude review, use the repository's
[`claude-review`](../../scripts/claude-review) launcher rather than a hand-built
environment assignment. It derives the effective operating-system account,
normalizes `USER`, `LOGNAME`, and `HOME` for the Claude child, reads the review
prompt from standard input rather than argv, and emits bounded diagnostics plus
append-only attempt receipts. For substantive review, pass `--review-config`
with the versioned governed-launch JSON and pass only model and supported effort
selection after `--`. The launcher owns the Claude tools, permission mode, MCP,
settings, hook, output, and session-persistence flags; do not append competing
review flags.

Before an expensive independent review, run the same launcher with
`--auth-preflight`. It reuses the effective-user environment and executable
resolution, sends only the fixed `CLAUDE_AUTH_OK` prompt on standard input,
disables all Claude tools, passes `--no-session-persistence`, and runs from a
fresh private attempt-local directory through the qualified macOS or Linux
route. It may retain the selected model and effort, but it is not substantive
review and does not read repository, candidate, or held-out content.
For example:

```text
scripts/claude-review --auth-preflight -- --model opus --effort high
```

`AUTH_PREFLIGHT_OK` means authentication worked for that process context only;
it does not guarantee that a later review cannot expire. Do not start the
review after a preflight failure.

After successful auth preflight, invoke the governed review from the owning
controller and keep awaiting that exact launcher until its live-state record is
terminal. The review config must cover every source root, bind the candidate and
exact `HEAD`, and bind the
disjoint admitted evidence destination, enumerate exact observational command
argv and immutable per-attempt artifact paths, and declare retry and cancellation
policy. Do not use a Codex tool timeout
or missing output as evidence that Claude exited, and do not launch a replacement
while the recorded process group may still be live. If the interactive contract
requires a disposition, use the launcher's request, decline, or authority-bound
termination control against the exact live-state path; force escalation requires
separate authorization.

The configured launch root is the logical source-graph anchor, not Claude's
process directory. The launcher passes it and every additional source root
through exact `--add-dir` arguments, then runs Claude from fresh qualified
attempt-local scratch on macOS or Linux so provider bootstrap writes cannot
enter the candidate. Effective initialization must report that exact scratch
directory before output can qualify.

Controller-side command preflight is followed by an in-provider exact-command
canary. The launcher rejects a missing or failed canary and any
`dangerouslyDisableSandbox` request; do not bypass a nested-sandbox failure.
After Claude's direct process exits, keep awaiting the recorded process group
and complete both stream collectors before freezing output or considering an
eligible exact-input repeat.

The launcher performs representative access and command-effect preflight,
validates Claude's effective initialization metadata, snapshots all guarded
source bytes and the Git index, and requires a positive no-delta postflight.
Its retry cap applies only to fresh executions that repeat exact input after a
fully terminal, explicitly transient provider outcome. Provider-internal retry
events remain part of one attempt. Preserve each attempt receipt even when no
candidate verdict is produced, and apply finding disposition only to successful
substantive review output.

The launcher preserves distinct documented failure classes when provider output
supports them: `AUTH_OAUTH_TOKEN_EXPIRED_401`,
`AUTH_SAVED_LOGIN_REFRESH_REJECTED`, `AUTH_OAUTH_TOKEN_REVOKED`, and
`AUTH_INVALID_CREDENTIALS`. An auth-shaped but unsupported variant is
`AUTH_UNKNOWN_FAIL_CLOSED`; do not invent a provider cause. All auth failures
preserve candidate bytes and review state, retain only non-secret diagnostics,
stop automated retries, do not mutate auth/session files, and never emit
`REJECT`. `AUTH_OAUTH_TOKEN_EXPIRED_401` and
`AUTH_SAVED_LOGIN_REFRESH_REJECTED` require interactive operator
reauthentication before rerunning the unchanged preflight and review. The
remaining documented classes require the matching supported operator diagnosis
in the same environment; do not substitute another reviewer.

Anthropic's [authentication documentation](https://code.claude.com/docs/en/authentication)
describes `claude setup-token` as a separate long-lived automation credential
option. This reviewer path neither provisions nor adopts it. Any
future use requires separate credential-management authority, a supported
secret store, rotation/revocation ownership, and redacted receipts.

- Keep `USER` and `LOGNAME` consistent with the effective user for the Claude
  child. On the qualification host, normalizing those variables restored
  Claude authentication; the precise authentication mechanism was not
  isolated and remains unverified.
- Ensure the effective writable-root set includes `~/.claude/session-env` for
  the session-environment path exercised by the qualification. Resolve `~`
  from the effective user's home when Codex configuration requires an absolute
  path.
- When Claude will use its Bash tool, ensure the effective writable-root set
  includes `/tmp` for Claude's temporary runtime state. On macOS, verify the
  effective policy and path mapping rather than assuming the displayed
  `/tmp` and `/private/tmp` forms represent different requirements.

Codex supports additional roots for `workspace-write` through
[`sandbox_workspace_write.writable_roots`](https://learn.chatgpt.com/docs/config-file/config-reference#sandbox_workspace_writewritable_roots).
Prefer only the roots required by the qualified child path. Do not prescribe
`danger-full-access`, global unsandboxing, or a blanket sandbox bypass when
these scoped roots are sufficient. A workspace-local `TMPDIR` is not a
qualified substitute for either Claude path above.

The concrete qualification was workstation-specific evidence, not portable
configuration doctrine. On the qualification host, Codex ran as a non-root
user with that user's `HOME`, while `USER` was absent and `LOGNAME` named a
different user. Normalizing both login-identity variables restored a minimal
Claude prompt. Direct write probes isolated the session-environment write
failure to the Codex writable-root boundary; after the tested writable paths
were available and Codex was restarted, a Claude Bash probe completed with
`hello`, and a later focused read-only review did not reproduce the observed
authentication, session-environment, or Bash temporary-state failures. These
results qualify only the tested Claude Code version, host, and invocation
contexts under that Codex `workspace-write` environment. They do not establish
a version-independent Claude Code runtime contract, that the tested writable
roots are sufficient for every Claude workflow, or the same paths as
requirements for other child CLIs.

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
