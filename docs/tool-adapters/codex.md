# Codex Adapter

This adapter records Codex-specific deltas on top of the core playbook. A Codex
task combines an interactive thread for steering and disposition with an
execution workspace for bounded repository work, validation, and evidence.
Apply the core
[`surface roles`](../core-model.md#interactive-and-execution-surfaces) to the
concrete capability in use. Use this adapter with `docs/start-here.md`,
`docs/core-model.md`, `docs/source-first-retrieval.md`, `docs/repo-readiness.md`,
and repo-local `AGENTS.md`; do not treat it as a second copy of those rules.

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

### Issue-Owned Durable Prompt Retrieval

Apply the shared
[`Airtable canonical-text handoff`](../prompts.md#airtable-canonical-text-handoff)
and the
[`issue-owned durable rendered-prompt handoff profile`](../prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile)
when Codex receives an exact issue-owned prompt. Use the external envelope's
exact Airtable base, table, and record IDs and retrieve that record through a
currently permitted connector route. Require exactly one result and verify the
expected key and field set before re-encoding the payload and independently
checking its byte length and SHA-256.

This receiver projection does not add Codex to the normal ChatGPT/Claude route
selected by the shared decision model. It applies only when a narrower
authorized contract supplies Codex an envelope that uses the same Airtable
record format and verification rules.

Fail closed on a missing, multiple, stale, transformed, truncated, or mismatched
record. Do not substitute a local download, another delivery route, or
reconstructed chat text. Record the delivery operation and Codex attempt
separately from the record and envelope; neither supplies authority. Concrete
provider, account, destination, retention, and visibility policy stay in their
owning contract, not this adapter.

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

### Qualified Direct Claude Code Path

Direct Claude Code execution from Codex under `workspace-write` has a narrower
qualified runtime contract in addition to the general child-process guidance:

For local development and lifecycle controls, use the repository's
[`claude-review`](../../scripts/claude-review) source rather than a hand-built
environment assignment. It derives the effective operating-system account,
normalizes `USER`, `LOGNAME`, and `HOME` for the Claude child, reads the review
prompt from standard input rather than argv, and emits bounded diagnostics plus
append-only attempt receipts. For substantive review, pass `--review-config`
with the versioned governed-launch JSON and pass only model and supported effort
selection after `--`. The launcher owns the Claude tools, permission mode, MCP,
settings, hook, output, and session-persistence flags; do not append competing
review flags. Production auth and review use the byte-exact machine-local
installation made by
[`install-claude-review`](../../scripts/install-claude-review), not the writable
repository path. Put `--review-config` immediately after that exact installed
absolute path. Authentication preflight follows the same convention.
The launcher rejects either mode when combined with permission-hook or lifecycle
control modes, so an allowed review prefix cannot authorize those controls.

Before an expensive independent review, run the same launcher with
`--auth-preflight`. It reuses the effective-user environment and executable
resolution, sends only the fixed `CLAUDE_AUTH_OK` prompt on standard input,
disables all Claude tools, passes `--no-session-persistence`, and runs from a
fresh private attempt-local directory through the qualified macOS or Linux
route. It also disables Claude instruction and auto-memory loading so a global
or project bootstrap cannot intercept the fixed authentication canary. It may
retain the selected model and effort, but it is not substantive
review and does not read repository, candidate, or held-out content.
For example:

```text
/ABSOLUTE/INSTALLED/PATH/claude-review --auth-preflight -- --model opus --effort high
```

The project rule at
[`../../.codex/rules/claude-review.rules`](../../.codex/rules/claude-review.rules)
keeps every writable repository-relative launcher form approval-gated. The
portable machine-rule template is
[`../../.codex/rule-templates/claude-review.rules`](../../.codex/rule-templates/claude-review.rules).
Never copy that template unchanged into the user layer: its placeholder is not
an executable identity, and a relative allow prefix can match writable bytes in
more than one repository.

The installer verifies a clean exact source commit and derives one immutable,
content-addressed entry contract from the launcher bytes, installation and
qualification schemas, Codex rule-template bytes, configured Claude selector,
active-rule path, forbidden roots, and the exact installation directory. An
unrelated source commit remains activation provenance and does not change the
entry contract when those execution-contract inputs are identical. The
installer publishes the stable command `~/.local/bin/claude-review` with one
combined schema-v3 installation and current-qualification record at
`~/.local/bin/.claude-review.json`. The content digest remains in that record
and the entry contract, not in the command name. Qualification serializes on
the stable executable and atomically replaces the combined record. It creates
no other sidecar, `libexec`, state, cache, log, or historical receipt tree.
The production installer derives that directory from the effective user's
account home and exposes no relocation flag.
The installer renders the user rule with the exact installed absolute path,
refuses a different existing object, and requires the caller to name the
expected digest before replacing an existing active rule. An identical-contract
rerun securely validates and preserves the current receipt.
Selector drift on a rerun is qualification-required and occurs before rule or
activation-receipt mutation. Older installation schemas remain historical
state; do not reinterpret or migrate them automatically. Supply every
candidate, evidence, workspace, and attempt-scratch root as a forbidden root.
The activation receipt is explicit operation evidence and does not become
durable launcher state. Production auth preflight reports its bounded record on
standard error and does not accept a diagnostics-file destination. Governed
review diagnostics remain inside the config's exact evidence directory. A
diagnostics-path or config failure is reported on standard error without
falling back to an unqualified file path.
For example, using operator-selected absolute paths:

```sh
./scripts/install-claude-review \
  --claude-bin /ABSOLUTE/PATH/TO/QUALIFIED/CLAUDE \
  --forbidden-root /ABSOLUTE/PATH/TO/WORKSPACE \
  --forbidden-root /ABSOLUTE/PATH/TO/EVIDENCE \
  --activation-receipt /ABSOLUTE/PRIVATE/PATH/activation-receipt.json \
  --expected-existing-rule-sha256 EXPECTED_SHA256
```

The generated user rule allows only direct auth-preflight and governed-review
prefixes for that installed path. The exact
`--qualify-claude-identity` prefix is `prompt`, as are lifecycle and
permission-hook controls; repository-relative, alternate-path, arbitrary
Claude-selection, and shell-wrapped forms are not allowed. The installed
command and rule are a one-time setup while their contract remains unchanged;
a routine Claude update uses only the bounded qualification command emitted by
the drift diagnostic, not another install, rule rewrite, or Codex restart. The
installed launcher verifies its own bytes, immutable entry contract,
active-rule hash, singular flat qualification receipt, and the
selector's exact non-executing file identity before either allowed operation.
Only matching already-qualified bytes may be queried for their recorded version,
followed by a repeated file observation. It never resolves `claude` through
inherited `PATH`.

When the configured selector resolves to a legitimate new identity, ordinary
auth and review fail before provider launch with
`reviewer_identity_qualification_required`. The bounded diagnostic names the
current receipt digest, observed canonical path and file digest, the exact
non-executing observation and its digest, and the exact qualification command;
it does not claim a version for unqualified bytes. That command accepts only the
expected current receipt digest and expected observed file-identity digest; it
derives the selector from the immutable entry manifest, recomputes the target,
serializes the transition under the entry's exact lock, rejects no-op requests,
then performs the first permitted version query. After another exact file
observation it atomically compare-and-swap replaces the one current receipt
through a flushed sidecar temporary file. The replacement records the prior
receipt digest without retaining an accumulating local receipt history.
It cannot select another executable or change the selector. After the operator
approves and the transition succeeds, rerun the unchanged auth or review
command through the unchanged rule. An upgrade, consecutive upgrade, or
rollback each requires a new transition from the current receipt.

Codex loads rules at startup. After a genuine entry-contract install or rule
update, validate the rendered rule without launching Claude, then restart Codex
before relying on it. A qualification-only transition does not edit the rule or
launcher and does not require a restart:

```sh
codex execpolicy check --pretty \
  --rules /ABSOLUTE/PATH/TO/ACTIVE/claude-review.rules \
  -- /ABSOLUTE/INSTALLED/PATH/claude-review --auth-preflight

codex execpolicy check --pretty \
  --rules /ABSOLUTE/PATH/TO/ACTIVE/claude-review.rules \
  -- /ABSOLUTE/INSTALLED/PATH/claude-review --terminate /tmp/live-state.json \
  --termination-authority operator-approved

codex execpolicy check --pretty \
  --rules /ABSOLUTE/PATH/TO/ACTIVE/claude-review.rules \
  -- /ABSOLUTE/INSTALLED/PATH/claude-review --qualify-claude-identity \
  --expected-current-receipt-sha256 EXPECTED_RECEIPT_SHA256 \
  --expected-observed-file-identity-sha256 EXPECTED_FILE_IDENTITY_SHA256
```

The first check must report `allow`; the lifecycle and qualification checks
must report `prompt`. Do not use
shell wrappers, redirections, or pipelines for this path: they change policy
evaluation and bypass the launcher's owned prompt/output flow. Supply the review
prompt directly on standard input through an execution channel that remains open
until the controller writes the exact frozen prompt bytes and then explicitly
closes standard input. A runner that starts the launcher with standard input
already closed delivers an empty prompt and is not a valid governed-review
invocation; the launcher must fail it before starting a reviewer. For a
controller API, start the direct process with writable standard input, write the
frozen bytes exactly once, close the stream to deliver EOF, and then await that
same process and process group through the terminal boundary.

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

Do not use autonomy to widen scope, reinterpret intent, or take ownership of
merge, release, tag, uncertain deletion, security-sensitive,
permissions-sensitive, or policy-interpretation decisions.

## Delivery Notes

Use the PR readiness, validation, and delivery rules in
[`repo-readiness.md`](../repo-readiness.md) and repo-local `AGENTS.md`.

When reporting successful completion for Codex implementation work, apply the
core model's
[`Successful completion projection`](../core-model.md#successful-completion-projection).
Normally include the opened or updated PR and its status, the canonical
validation and review summary, the exact implementation head when useful, and
the stop boundary. Add changed-file, blocker, risk, or forensic-evidence detail
only when it materially affects operator review or action.
