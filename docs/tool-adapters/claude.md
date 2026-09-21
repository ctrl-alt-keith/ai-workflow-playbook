# Claude Adapter

This adapter maps Claude Chat, Claude Cowork, and Claude Code onto the shared
Playbook. Use it with
[`start-here.md`](../start-here.md), [`core-model.md`](../core-model.md),
[`source-first-retrieval.md`](../source-first-retrieval.md),
[`repo-readiness.md`](../repo-readiness.md), and the target repo's `AGENTS.md`.
Record only Claude-specific deltas here; shared rules stay in their canonical
docs.

## Surface And Invocation Routing

Map each concrete capability through the core
[`surface roles`](../core-model.md#interactive-and-execution-surfaces) and
[`locality classes`](../core-model.md#surface-classes):

- **Claude Chat** is an interactive, conversational surface with no repository
  filesystem.
  [**Instructions for Claude**](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)
  apply account-wide to conversations, while project instructions apply only
  inside that project. Repository files arrive through
  [explicitly selected GitHub content](https://support.claude.com/en/articles/10167454-use-the-github-integration),
  project knowledge, or another currently observed retrieval route, so current
  source retrieval is best-effort per thread rather than guaranteed by the
  instruction surface.
- **Claude Cowork** combines interactive steering with bounded execution.
  [Sessions run in the cloud on every surface](https://support.claude.com/en/articles/15520349-use-claude-cowork-on-web-desktop-and-mobile),
  so it is agentic-remote by default, or agentic-local for an active
  desktop-connected repository folder while that connection remains available.
- **Claude Code** combines interactive and execution roles when human-driven;
  a controller-launched run is an execution surface. It is agentic-local with
  the repository filesystem and otherwise agentic-remote until current source
  and repo-local instructions are available.

Initiation remains separate:
[scheduled Cowork](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork) is
unattended; [Dispatch](https://support.claude.com/en/articles/13947068-assign-tasks-from-anywhere-in-claude-cowork) is a
human assignment whose execution does not require the human to remain present,
and Anthropic documents it as unavailable to new accounts, so its presence is
runtime evidence; Claude Code may be interactive or controller-launched. Controller-launched
independent review additionally applies the conditional
[`Local Read-Only Reviewer Launch`](#local-read-only-reviewer-launch) route and
the controller-side adapter for the invoking executor; each adapter governs its
own run boundary.

### Claude Chat-to-Cowork projection

Apply the shared
[`interactive-to-execution consent boundary`](../core-model.md#interactive-to-execution-transition-consent):
in this adapter, it governs Claude Chat-to-Cowork transitions. Independently
initiated Cowork remains governed by its own invocation and authority contract.

## Hydration Transport By Surface

Persistent instructions trigger hydration but do not prove success or source
freshness. Apply the shared
[`global bootstrap router`](../../distributions/global-bootstrap/bootstrap-router.md)
and its
[`persistence boundary`](../start-here.md#global-bootstrap-persistence) at each
independently starting Claude surface, then use the surface-specific route
below.

### Account-Level Hosted Transports

- Anthropic documents [**Instructions for Claude**](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)
  as an account-wide setting for conversations; it is not a Chat-only
  transport and project instructions do not replace it.
- When a current run exposes one or more `user_preferences` blocks, treat them
  as independently observed transports until ownership and precedence are
  established. An account-setting edit does not prove that a separately
  presented block changed.
- Anthropic documents [Cowork Global instructions](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)
  as standing instructions for every Cowork session at
  **Settings > Cowork > Global instructions**, and states that in the new
  Claude experience they are part of Instructions for Claude at
  **Settings > General**. Which field the current UI exposes is runtime
  evidence; use the field Anthropic documents for that experience, not another
  account field.

### Claude Chat

Put the router in the verified account transport and keep project instructions
to project-specific context. Prefer explicitly selected current GitHub content
or another observed current route; a prior project sync is not current-source
evidence. Chat hydration is best-effort per thread. If a required source cannot
be retrieved after applying the
[`runtime-evidence rule`](../start-here.md#connector-availability-is-runtime-evidence),
stop the repository-dependent task rather than proceeding from conversation or
project memory.

### Claude Cowork

Use verified Cowork Global instructions for the router and keep project or
folder instructions as thin project-specific pointers. When no global
transport is exposed, an interactive task may proceed only from a verified
task, project, or folder trigger that obtains the required current sources;
record the coverage gap. A connected local folder supplies the local startup
route while the connection remains available. Unattended tasks must name a
qualified current-source route and stop when it is unavailable.

[Desktop Cowork skips outside-working-directory imports](https://code.claude.com/docs/en/memory)
and linked user files; cloud, web, and mobile Cowork run in the cloud and
cannot infer coverage from a workstation `~/.claude/CLAUDE.md`.

Anthropic does not publish precedence among account instructions, runtime
`user_preferences`, and Cowork Global instructions. Verify them independently;
if one runtime presents the exact router more than once, apply its trigger once.

### Claude Code

Claude Code uses the file-backed `CLAUDE.md` discovery below. A repo-local
`CLAUDE.md` may point to current `docs/start-here.md` and `AGENTS.md` but does
not replace them. In remote Code, retrieve those sources through the current
workspace or another observed route and stop if they are unavailable.

The remaining execution, permission, worktree, context, model, and delivery
sections are Claude Code-specific unless a section explicitly says
otherwise.

## Instruction Discovery And Precedence

[Claude Code's current memory guidance](https://code.claude.com/docs/en/memory)
documents four instruction scopes in broad-to-specific load order: managed
policy, user instructions at `~/.claude/CLAUDE.md`, project instructions at
`./CLAUDE.md` or `./.claude/CLAUDE.md`, and personal project-local
instructions. Project instructions appear in context after user instructions,
and discovered files are concatenated rather than one scope overriding another;
load order is context ordering, not authority transfer, and user-level
`~/.claude/CLAUDE.md` remains operator context that cannot override repo-local
policy. Claude Code reads `CLAUDE.md`, not repo-local `AGENTS.md`, unless the
latter is imported or explicitly read. Explicitly read `AGENTS.md`, keep any
`CLAUDE.md` as a thin pointer rather than a policy copy, and apply the
[`repository instruction hierarchy`](../start-here.md#repository-instruction-hierarchy).

Install the router in `~/.claude/CLAUDE.md` as an inline marked block per the
[distribution README](../../distributions/global-bootstrap/README.md), not as
an outside-working-directory import, symlink, or hard link (desktop Cowork
skips those). Keep the HTML markers: Claude Code strips them from context, the
drift validator needs them.

## Interaction Mode And Permission Mode

These are two separate axes. The playbook interaction mode (implementation,
review/audit, orchestration/prompt-authoring) expresses intent and authority;
select it first via the
[interaction-mode preflight](../repo-readiness.md#interaction-mode-preflight).
Claude Code's permission mode (`default`, `plan`, `acceptEdits`,
`bypassPermissions`) controls execution capability. Choose the permission mode
from the task's actual tool requirements and blast radius, not by inferring it
from the interaction mode.

- Review/audit work usually needs read-only shell such as `git status`,
  `git diff`, `gh pr view`, and `make check`. Choose a mode that permits those
  reads while withholding write/mutation approval; do not assume `plan` mode is
  the right default merely because the interaction mode is review/audit.
- For implementation, prefer per-action approval (`default`); reserve broader
  auto-approval (`acceptEdits`) for bounded, already-agreed scope.
- [Permission rules](https://code.claude.com/docs/en/permissions) are checked
  `deny` -> `ask` -> `allow`, first match wins. This is approval/prompting
  behavior, not an authorization boundary.
- `bypassPermissions` skips approval prompts; Anthropic documents it for use
  only in isolated environments such as containers or VMs. Do not use it for
  repository work with meaningful blast radius, and do not treat repository-level
  `deny` rules as a sufficient safety boundary under it.

Permission mode changes capability, not authority; apply
[`core-model.md`](../core-model.md#authority-and-transitions).

## Command Execution

Claude executes Bash commands as separate processes. In the main session,
working-directory changes may carry over within the project or explicitly
added directories, but shell environment changes do not persist between calls;
subagent working-directory changes do not persist. Keep commands self-contained
and follow the
[command-form rule](../repo-readiness.md#command-form-and-intent-visibility):
run ordinary repository operations in direct, single-purpose form (`git status`,
`gh pr view <n>`, `make check`) rather than wrapping them in extra `bash -lc`,
aliases, or compound-shell layers that hide intent. Parallelize only independent
read-only inspection.

Claude has no writable-root sandbox. Apply the shared durable-state and
scratch rules in
[`repo-readiness.md`](../repo-readiness.md#repo-local-workflow-state).

### Local Read-Only Reviewer Launch

Apply this section only when launching or interpreting a local
`claude-review` or `codex-review` attempt. First apply the shared
[`external-ai-reviewer.md`](../external-ai-reviewer.md) contract and the
launcher-owned [`review-launchers.md`](../../scripts/review-launchers.md).
That reference owns launcher records, diagnostics, redaction, provider-runtime
qualification, and incident interpretation; it is not ordinary Claude startup
context.

Use only the active Playbook checkout's repository-owned launcher, with the
explicit absolute provider binary it requires. Invoke it from the checkout
being reviewed and bind its exact `--candidate-commit`; a mismatch stops before
review. The configured launcher supplies read-only review controls. Keep local
reviewer execution behind explicit per-action approval; do not launch it in an
auto-approving permission mode.

Run the selected launcher's required preflight before an expensive review. A
qualified Claude authentication failure during preflight or review requires
operator reauthentication; every other Claude failure is generic wrapper
failure. Codex has no qualified authentication classification, so a failed
Codex preflight or review is generic failure. Neither is review evidence, a
verdict, or grounds for silent reviewer substitution.

Recover a qualified Claude authentication failure by having the operator log in
again through the Claude CLI in their own interactive session, then rerun the
unchanged preflight and review. Do not drive that login, mutate auth or session
files, or retry automatically. Restored authentication is capability only: it
is not review evidence and does not revive the failed attempt.

Treat retained diagnostics as review evidence only when the launcher's terminal
record says `diagnostics_file: written`; otherwise preserve the failed attempt
and stop at the selected-review boundary. For the record states, failure
ordering, provenance, retention, redaction, and incident interpretation, use
[`review-launchers.md`](../../scripts/review-launchers.md).

For a Codex review, require an explicit exact selector, successful pre-prompt
selector acceptance, and post-review effective model/effort evidence matching
the request. Missing or mismatched effective-selection evidence fails closed;
exact-model qualification does not fall back. The selector and runtime details
are in [`review-launchers.md`](../../scripts/review-launchers.md).

Launcher controls do not establish total reviewer isolation: operator-layer
instructions and configuration remain outside launcher control. Keep that
limitation visible whenever reviewer qualification relies on isolation.

## Worktrees And Subagents

Claude Code spawns subagents through the `Agent` tool
([subagents](https://code.claude.com/docs/en/sub-agents): renamed from `Task`
in v2.1.63; `Task(...)` references remain aliases). A call selects the subagent
with `subagent_type` and may set `isolation: worktree` to run it in a temporary
git worktree branched from the repository's default branch. Claude resumes a
completed subagent with `SendMessage` addressed to its agent ID or name; the
built-in Explore and Plan agents are one-shot and cannot be resumed.

A non-fork subagent starts with a fresh, isolated context: it receives the
delegation message and the `CLAUDE.md` hierarchy (including
`~/.claude/CLAUDE.md` and any `AGENTS.md` loaded as project instructions), not
the parent conversation, invoked skills, or previously read files. The `fork`
subagent type inherits the parent conversation instead. Give each non-fork
subagent the complete standalone envelope owned by
[`orchestration-and-parallelism.md`](../orchestration-and-parallelism.md), and
apply worktree and PR topology from
[`repo-readiness.md`](../repo-readiness.md#pr-readiness). Claude Code creates
its own worktrees under `.claude/worktrees/`
([worktrees](https://code.claude.com/docs/en/worktrees)); such a worktree does
not by itself satisfy a repo-local `.worktrees/` implementation-isolation
policy. With agent teams enabled, an `Agent` call that carries a `name` can
launch a teammate in the main working directory regardless of the subagent's
frontmatter `isolation`.

A harness default that discourages unprompted delegation is executor
behavior, not Playbook doctrine: report it as a runtime observation and apply
the Playbook's fan-out guidance to decide whether and how to delegate.

## Context Compaction And Recovery

Claude Code auto-compacts before the context window fills and supports
`/compact`, `--resume`, and `--continue`. Treat the resulting summary as
navigation and refresh required mutable state under
[`source-first-retrieval.md`](../source-first-retrieval.md) and
[durable continuity](../core-model.md#durable-continuity).

## Connectors

Claude reaches remote services through MCP connectors. Apply the shared
[`runtime-evidence rule`](../start-here.md#connector-availability-is-runtime-evidence)
and the GitHub route in
[`review-packet.md`](../review-packet.md#direct-pr-inspection).

### Issue-Owned Durable Prompt Retrieval

Apply the shared
[`Airtable canonical-text handoff`](../prompts.md#airtable-canonical-text-handoff)
and the
[`issue-owned durable rendered-prompt handoff profile`](../prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile)
when Claude receives an exact issue-owned prompt through a currently permitted
Airtable route. Use the external envelope's exact base, table, and record IDs;
retrieve with the connector's exact `recordIds` constraint and require exactly
one result. Do not use fuzzy search or key lookup as the retrieval route.

Apply the shared canonical-text, field, byte-length, and SHA-256 verification
before acceptance. If the record is missing, duplicated, stale, transformed,
truncated, or mismatched, fail closed. Do not substitute a local file
or reconstructed chat text.

After acceptance, choose tools, permission mode, and session persistence from
the owning task or narrower reviewer contract; prompt retrieval alone does not
make execution read-only or grant substantive authority.

When Claude produces the handoff, create one new five-field Airtable record,
capture the returned record ID and creation time, then retrieve that exact ID
using `recordIds` and complete the shared verification before constructing or
emitting the envelope from that attempt's verified returned-record identity.
Never update a frozen record; corrections create a new record and
carry predecessor lineage externally. Concrete provider, account, destination,
retention, and visibility values remain outside this adapter.

## Claude Model, Thinking, And Thread Routing

Apply the shared [model and reasoning routing](../model-routing.md) doctrine.
Do not infer a mapping from OpenAI model names or tiers. Claude Code's
[model configuration](https://code.claude.com/docs/en/model-config) defines the
executor-native aliases `haiku` (simple fast tasks), `sonnet` (daily coding),
`opus` (complex reasoning), and `fable` (hardest, longest-running tasks);
`best` resolves to Fable where available and otherwise to `opus`. Exact model
IDs, availability, context variants, and administrator allowlists are runtime
evidence. Fable requires a current Claude Code version, and its availability
under [zero data retention](https://code.claude.com/docs/en/zero-data-retention)
follows Anthropic's Covered Models policy, not Claude Code. Fable and Opus 5
safety classifiers can trigger documented fallback, so request Fable explicitly
only when its effective runtime identity can be observed and meets the task's
qualification requirements.

| Claude task class | Default Claude Code model | Thinking/effort guidance | Escalate when | Downgrade/follow up when |
| --- | --- | --- | --- | --- |
| Deterministic external verification; hashes, inventories, evidence citations; simple source inspection; mechanical fallback verification | `haiku` | Use executor default; Claude Code does not document effort control for Haiku | a result is ambiguous, changes a decision, or source access is insufficient | substantive review has converged and a qualified deterministic check remains |
| Implementation review; evidence-package review; reviewer follow-up after substantive convergence; bounded long-context evidence synthesis | `sonnet` | Use the documented default (`high` absent an organization default); use `medium` or `low` only as an explicit cost/latency trade-off where bounded evidence supports it | residual findings repeat, evidence conflicts, or semantics remain unresolved | split inventories, hashes, and other externally checkable claims to Haiku or another qualified mechanism |
| Substantive adversarial code review; protocol/design review; architecture review; authority or security-boundary review | `opus` | Use the model's documented default; do not assume `xhigh` applies to every Opus runtime | a new trust boundary, unresolved architecture/security implication, conflicting authority, or a finding that changes qualification disposition appears | after substantive convergence, delegate only the remaining mechanical claim; do not relabel it as substantive review |
| Especially hard long-running investigation, outage/root-cause work, or architecture decision that exceeds a normal Opus review | `fable`, where available | Adaptive reasoning is always on; use the documented default (`high` absent an organization default), and reserve `xhigh`/`max` for a bounded demonstrated need | a safety fallback, unavailable Fable runtime, or remaining decision risk defeats the qualification requirement; stop, seek an explicit human decision, or use another independently qualified mechanism | keep Fable out of routine review and delegate only bounded deterministic follow-up |

The table is a conservative routing hypothesis, not a quality-parity claim.

### Thinking And Effort

Effort is distinct from model choice. Use Claude Code's own values (`low`,
`medium`, `high`, `xhigh`, `max`), not the Playbook's `light`/`medium`/`high`
classes as numeric equivalents; which values a model accepts is runtime
evidence. The documented default is `high` for every effort-capable model
except Opus 4.7 (`xhigh`) and except where an organization default effort
applies to its organization default model. Lowering effort is the primary
cost/latency lever for a bounded task. Do not invent a Haiku effort setting
where the executor does not offer one.

### Thread Routing And Review Boundaries

Apply the shared `FRESH THREAD`, `SAME THREAD`, and `CHILD TASK` vocabulary in
[`prompts.md`](../prompts.md#thread-routing-and-configuration-continuity). For
a FRESH THREAD, choose this matrix's task-appropriate model and supported
thinking/effort setting. For a SAME THREAD, preserve the existing parent model
and thinking/effort configuration by default.

### Visible Thread Names

This adapter does not currently establish an executor-applied visible-thread
naming capability. Therefore Claude-targeted `FRESH THREAD`, `SAME THREAD`,
and `CHILD TASK` prompts resolve the shared
`[resolved thread-name section when applicable]` placeholder to nothing. Do
not ask Claude to rename itself or report a naming limitation.

Requested configuration and effective runtime configuration are distinct.
Claude Code can intentionally switch `opusplan` from Opus in plan mode to Sonnet
in execution, and can use configured fallback chains for unavailable or
overloaded models; Fable/Opus safety-classifier fallback is also documented.
For governed work, record the requested model/effort and the effective values
when the runtime exposes them, plus any substitution event. `/status` exposes
the current Claude Code model, and Claude Code shows a transcript notice when a
documented switch occurs. If effective identity is unavailable, record that
limitation rather than treating the request as proof. Requalify, escalate, or
stop only when the effective result violates a required capability or exact-model
reviewer qualification; a runtime event is not automatically fatal.

### Prompt Operator Metadata

When an operator prepares a Claude prompt, use one complete metadata block:

```text
Operator metadata (do not include in prompt)
Thread routing: <FRESH THREAD | SAME THREAD | CHILD TASK>
Recommended model: <FRESH THREAD/CHILD TASK: haiku | sonnet | opus | fable; SAME THREAD: Preserve requested thread model and observe effective runtime model; UNVERIFIED FROM AUTHORING SURFACE: resolve with the operator at launch>
Recommended thinking/effort: <FRESH THREAD/CHILD TASK: supported executor setting; SAME THREAD: Preserve requested thread setting and observe effective runtime setting; UNVERIFIED FROM AUTHORING SURFACE: resolve with the operator at launch>

Reason:
<one concise task-specific selection or continuity justification>
```

This metadata is operator guidance, not task authority. Do not recommend a
model, effort, or child configuration that current evidence shows the Claude
surface cannot support. Interpret FRESH/SAME routing before prompt delivery: do not tell the
downstream Claude task to change or preserve parent configuration when that
surface does not expose the control. The executable task body must be complete
without metadata and may authorize child dispatch only where that Claude
surface supports it. Keep task-required requested/effective runtime evidence in
the executable body when it is a validation or qualification requirement.
When the authoring surface has not verified a required control or capability,
record `UNVERIFIED FROM AUTHORING SURFACE` in the affected metadata field and
resolve it with the operator at launch; do not present that unknown as
unavailable.

## Reasoning And Model Configuration

When a material prompt uses the product-neutral reasoning class in
[`prompt-contracts.md`](../prompt-contracts.md) (`light`, `medium`, `high`), the
Claude representation is the supported model and thinking/effort setting
selected above. Preserve mandatory versus advisory capability and fail closed
when the available surface cannot meet a mandatory requirement.

## Local GitHub And Environment Preflight

`scripts/codex-preflight` checks local GitHub SSH auth, `gh` auth, and repository
reachability — executor-neutral environment readiness. When Claude drives
repository automation or worker fan-out, run it first and stop on a non-zero
exit:

```text
cd /ABSOLUTE/PATH/TO/ai-workflow-playbook
./scripts/codex-preflight
```

## Delivery

Follow the PR readiness, validation, and delivery rules in
[`repo-readiness.md`](../repo-readiness.md) and repo-local `AGENTS.md`.
When reporting successful completion, apply the core model's
[`Successful completion projection`](../core-model.md#successful-completion-projection).
Normally include the opened or updated PR and its status, the canonical
validation and review summary, the exact implementation head when useful, and
the stop boundary. Add changed-file, blocker, risk, or forensic-evidence detail
only when it materially affects operator review or action.

## References

Runtime claims above link their official Anthropic source at the claim.
Claude Code and platform pages were checked on 2026-09-19; Claude Chat and
Cowork support pages on 2026-09-21.
