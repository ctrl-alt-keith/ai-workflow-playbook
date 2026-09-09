# Codex Adapter

This adapter records Codex-specific deltas on top of the core playbook. A Codex
task combines an interactive thread for steering and disposition with an
execution workspace for bounded repository work, validation, and evidence.
Apply the core
[`surface roles`](../core-model.md#interactive-and-execution-surfaces) to the
concrete capability in use. Use this adapter with `docs/start-here.md`,
`docs/core-model.md`, `docs/source-first-retrieval.md`, `docs/repo-readiness.md`,
and repo-local `AGENTS.md`; do not treat it as a second copy of those rules.

## OpenAI Model And Reasoning Routing

Choose the lowest-cost available model and reasoning effort that preserves the
confidence required by the bounded task. Model selection and reasoning effort
are separate configuration decisions: select both deliberately, and do not
default substantial work to Sol or Astra merely because it is long-running.

The official model references, checked 2026-09-05, position
[GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)
(`gpt-6-astra`) for the hardest end-to-end reasoning, coding, computer-use,
research, and document tasks;
[GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
for complex professional work;
[Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
for an intelligence/cost balance; and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
for cost-sensitive, high-volume workloads. Astra's documented API reasoning
efforts are `low`, `medium`, `high`, `xhigh`, and `max`; GPT-5.6 also supports
`none`. A Codex surface may expose a different set: verify the selected
model/effort combination in that runtime rather than copying the API list.
This adapter uses Light, Medium, and High as portable recommendation classes,
mapped to the available runtime setting by the operator.

OpenAI's [Codex release guidance](https://learn.chatgpt.com/docs/whats-new)
documents Astra as an option once available to the account. Rollout and
administrator enablement remain separate from model capability; verify access
on the actual interactive or scheduled execution surface.

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

The Luna/Terra/Sol defaults remain in place pending representative Astra
qualification. Defaults are routing hypotheses, not a guarantee that the
lower-cost choice is sufficient. Do not downgrade when consequences are high, ambiguity is
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

### Provisional Astra Placement

Consider Astra for a bounded quality-first escalation or a demanding workflow
spanning code, browsers, research, and professional artifacts when its
documented strengths match an observed need. This is a provisional routing
recommendation, not a demonstrated improvement over Sol for Playbook work.
Before changing defaults, compare representative outcomes, boundary adherence,
latency, cost per accepted result, and intervention behavior under controlled
conditions. Launch benchmarks and a single successful run do not qualify a
task class. Use current provider pricing rather than assuming fewer output
tokens makes Astra cheaper for the workload.

The published Astra context/output limits do not exceed those of Luna, Terra,
or Sol; a model switch alone does not justify a larger source set. OpenAI's
[misalignment monitoring](https://developers.openai.com/api/docs/guides/safety-checks/misalignment-monitoring)
can stop covered conversations and can flag legitimate activity or miss issues.
It does not undo prior actions or replace the existing authority, evidence,
review, and human-decision boundaries.

Astra's existence does not require a change to the
[autonomous maintenance layer](../maintenance-automations.md). Deterministic
hosted stewardship gains no model dependency; residual model-backed jobs are
candidates for later qualification on their actual execution surfaces.

### Codex Selector Routing And Acceptance

For FRESH THREAD and CHILD TASK, record the requested model, exact selector,
runtime-reported effective model (or `unobservable`), and any permitted
fallback or substitution separately. Use only these exact mappings; reject
aliases, near-matches, and guessed IDs.

| Requested model | Exact Codex selector |
| --- | --- |
| `GPT-6 Astra` | `gpt-6-astra` |
| `GPT-5.6 Luna` | `gpt-5.6-luna` |
| `GPT-5.6 Terra` | `gpt-5.6-terra` |
| `GPT-5.6 Sol` | `gpt-5.6-sol` |

Pass the exact selector to the real task launch. Reject it before task start if
the runtime does not accept it. Record any permitted fallback or substitution
at that boundary; exact-model requirements do not fall back.

`scripts/codex-preflight` checks independent local prerequisites only; it does
not launch Codex or qualify selectors. For SAME THREAD, preserve the parent
configuration and use runtime-visible effective-model evidence when available.

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
[`prompts.md`](../prompts.md#thread-routing-and-configuration-continuity).
Select model and effort using the matrix and selector contract above. For a
CHILD TASK, independently choose the lowest-cost sufficient configuration and
retain the evidence required by the governing workflow.

When a SAME THREAD crosses a capability boundary, use a bounded child or an
explicit fresh-thread transition rather than silently changing the parent.
Preserve reviewer independence separately from model capability.

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

Use compact outcome-oriented task envelopes from [`prompts.md`](../prompts.md)
and resolve only the Codex-specific model, effort, naming, and execution fields
here. Do not copy shared doctrine or add generic reasoning instructions.

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
For an Astra comparison from `none` or `minimal`, OpenAI recommends `low`;
record that required configuration change as a comparison limitation.
Treat reasoning effort as execution configuration rather than prompt prose,
then tune it against representative tasks. Do not recommend a global increase
or compensate for a configuration mismatch by bloating the prompt.

Keep Pro mode, persisted reasoning, programmatic tool calling, explicit prompt
caching, multi-agent execution, async tool calling, and mid-turn steering
outside the baseline migration. Evaluate each optional feature separately only
when the workload shape and measured
results justify it. Preserve behavior and settings before optimizing.

The API's [async tool calling](https://developers.openai.com/api/docs/guides/async-tool-calling)
allows useful work while application-managed tools are pending;
[mid-turn steering](https://developers.openai.com/api/docs/guides/steering)
accepts user updates through Responses WebSockets without undoing prior actions
or canceling started tools. These API capabilities do not establish their
availability or behavior in every Codex runtime.

### Operator Metadata And Reasoning Recommendations

When the playbook produces or recommends a complete Codex prompt, precede the
executable prompt with this plain-text operator metadata:

```text
Thread routing: <FRESH THREAD | SAME THREAD | CHILD TASK>
Recommended model: <FRESH THREAD/CHILD TASK: GPT-5.6 Luna | GPT-5.6 Terra | GPT-5.6 Sol | GPT-6 Astra (provisional; exact Codex selector must be accepted at launch); SAME THREAD: Preserve requested thread model and observe effective runtime model>
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
[model guidance](https://developers.openai.com/api/docs/guides/latest-model)
and [OpenAI models reference](https://developers.openai.com/api/docs/models),
checked 2026-09-05. Provider positioning supports candidate selection; the
Playbook's task-class defaults still require workload evidence.

## Prompt-Contract Mapping

Codex is an executor representation, not the owner of shared prompt meaning.
For a material prompt:

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

### Airtable Prompt Retrieval

Apply the shared
[`Airtable canonical-text handoff`](../prompts.md#airtable-canonical-text-handoff)
when Codex receives a qualifying small canonical-text prompt. Retrieve the
envelope's exact record through a currently permitted connector route and apply
the shared verification and fail-closed rules without choosing another route or
renderer.

When the prompt is an exact issue-owned material prompt, also apply the
[`issue-owned durable rendered-prompt handoff profile`](../prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile).
Routine machine-recipient handoffs use the shared transport without acquiring
that material-prompt governance.

Record the delivery operation and Codex attempt separately from the record and
envelope; neither supplies authority. Concrete provider, account, destination,
retention, and visibility policy stay in their owning contract.

## Startup Deltas

[OpenAI's current `AGENTS.md` guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
documents that Codex loads user-global guidance from `~/.codex/AGENTS.md` once
per run and combines it with project guidance. Use the copy-ready
[`global bootstrap router`](../../distributions/global-bootstrap/bootstrap-router.md)
there. It applies the shared
[`global bootstrap persistence`](../start-here.md#global-bootstrap-persistence)
timing invariant across repositories; it is not a per-turn retrieval rule.

Before repo-scoped work:

Apply the repository floor and task-activated owners selected by
[`start-here.md`](../start-here.md). Confirm the Codex project, execution
container, current directory, and Git state match the named repository and
worktree before editing. Use
[`source-first-retrieval.md`](../source-first-retrieval.md) for current source
state and [`repo-readiness.md`](../repo-readiness.md) for interaction mode,
policy alignment, command form, validation, and delivery. Stop on a repository,
worktree, authority, or required-source mismatch rather than inferring through
it.

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

Some Codex surfaces cannot reliably inherit a full conversation with explicit
worker roles. Give each child a standalone bounded envelope from
[`prompts.md`](../prompts.md), including the selected repository, sources,
scope, authority, validation, delivery, and stop boundary. The controller owns
startup activation and context sufficiency; a child reports newly activated or
missing sources instead of widening its own source set. Worker authority ends
at the envelope, and reconciliation remains controller-owned under
[`orchestration-and-parallelism.md`](../orchestration-and-parallelism.md).

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

### User-Layer Approval Policy

Use the portable
[`custom.rules`](../../.codex/rule-templates/custom.rules) template for the
operator's general Codex user-layer policy. Writable-root sandboxing is the
primary filesystem boundary; the template adds restrictions only for a small
set of destructive or external authority boundaries, and unmatched commands
fall through to sandbox policy. It contains no `allow` rules and grants no
authority outside the sandbox.

Raw `gh api` access is forbidden in favor of a supported high-level `gh`
command or an approved connector. Report a capability gap when neither route
can establish a materially necessary fact. A documented lower-level exception
requires an explicit operator change to this deny rule; agents do not bypass
it. The template does not install itself into `~/.codex/rules/custom.rules`;
workstation reconciliation remains a separate post-merge action.

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

Apply the core model's
[`Operator Observability`](../core-model.md#operator-observability) guidance.
Report Codex-visible phase, source, validation, artifact, blocker, and stop
state that changes what the operator should trust or do; aggregate routine
success and do not narrate hidden reasoning.

## Governed Artifact Capture Projection

Apply the shared contract in
[`evidence-lifecycle.md#governed-artifact-capture`](../evidence-lifecycle.md#governed-artifact-capture)
and the owning workflow's storage constraints. Codex supplies the permitted
write, exact verification, receipt, and compact report; it does not select a
new owner or turn capture evidence into authority.

## External API Claims

Apply the official-source requirement in
[`engineering-baseline.md`](../engineering-baseline.md#public-api-baselines)
when a Codex task depends on external API behavior.

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

### Local Claude Code Review

Invoke the active Playbook checkout's `scripts/claude-review` directly. No
supported workflow installs, copies, or reconciles a machine-local launcher.

Pass the absolute Claude executable with `--claude-bin`; the wrapper resolves
it, verifies that it is executable, and records its `--version` result. It does
not use inherited `PATH` to select Claude. It normalizes `HOME`, `USER`, and
`LOGNAME` from the effective account before starting Claude. Before an expensive
review, use the cheap authentication canary in that context:

```text
/ABSOLUTE/PATH/TO/ai-workflow-playbook/scripts/claude-review \
  --claude-bin /ABSOLUTE/PATH/TO/CLAUDE \
  --auth-preflight -- --model opus --effort high
```

For a review, run the command from the intended checkout, pass its exact commit
with `--candidate-commit`, and supply the review question on standard input.
Immediately before invoking Claude, the wrapper verifies that the checkout
resolves to that commit and adds the verified repository path and commit to the
review context. A mismatch fails before review rather than selecting a new
candidate.

The wrapper accepts only model and effort choices after `--`; it supplies the
read-only Claude tools, no-session-persistence, no-connector, and
non-interactive permission settings itself. It captures provider output, treats
an empty or failed response as wrapper failure, and emits bounded redacted
diagnostics. `--diagnostics-file` can retain those diagnostics at a new absolute
path when needed. Together with the caller's review question and subsequent
finding disposition, this is the Claude projection of the exact-candidate
review contract in [`external-ai-reviewer.md`](../external-ai-reviewer.md).
It grants no implementation, merge, release, or promotion authority.

The repository project rule keeps this local reviewer execution approval-gated.
Run the preflight before review and stop for operator attention if it fails;
do not treat a Claude failure as an ACCEPT or REJECT result.

## Autonomous Lane

Codex should continue without pausing when the scope is clear, the repo context
matches the task, required sources are available, validation can run, and no
human-gated decision is next.

Do not use autonomy to widen scope, reinterpret intent, or take ownership of
merge, release, tag, uncertain deletion, security-sensitive,
permissions-sensitive, or policy-interpretation decisions.

## Delivery Notes

Use the PR readiness, validation, and delivery rules in
[`repo-readiness.md`](../repo-readiness.md) and repo-local `AGENTS.md`.

When reporting successful completion for Codex implementation work, apply the
core model's
[`Successful completion projection`](../core-model.md#successful-completion-projection).
