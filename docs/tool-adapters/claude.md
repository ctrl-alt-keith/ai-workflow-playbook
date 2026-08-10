# Claude Adapter

Claude Code-specific deltas on top of the core playbook. Use with
[`start-here.md`](../start-here.md), [`core-model.md`](../core-model.md),
[`source-first-retrieval.md`](../source-first-retrieval.md),
[`repo-readiness.md`](../repo-readiness.md), and the target repo's `AGENTS.md`.
Record only what differs for Claude Code here; shared rules stay in their
canonical docs.

## Instruction Discovery And Precedence

Claude Code auto-loads `CLAUDE.md` memory at session start (project `CLAUDE.md`
or `.claude/CLAUDE.md`, user `~/.claude/CLAUDE.md`, and their imports). It does
not guarantee that repo-local `AGENTS.md` is ingested, yet `AGENTS.md` is the
canonical repository execution layer the startup contract requires. Therefore:

- Explicitly read the target repository's `AGENTS.md`; do not assume auto-loaded
  memory covers repo-local policy.
- Do not fork `AGENTS.md` or shared doctrine into a `CLAUDE.md`. If a `CLAUDE.md`
  exists, keep it a thin pointer to `docs/start-here.md` and the repo's
  `AGENTS.md`, not a second policy source. See
  [`repo-readiness.md`](../repo-readiness.md#agentsmd-responsibilities).
- Memory files are a transport for instructions, not an authority layer. The
  [Repository Instruction Hierarchy](../start-here.md#repository-instruction-hierarchy)
  governs; a user-level `~/.claude/CLAUDE.md` is operator context and does not
  override repo-local policy.

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
- Verified evaluation: permission rules are checked `deny` -> `ask` -> `allow`,
  first match wins. This is approval/prompting behavior, not an authorization
  boundary.
- `bypassPermissions` skips approval prompts; Anthropic documents it for use
  only in isolated environments such as containers or VMs. Do not use it for
  repository work with meaningful blast radius, and do not treat repository-level
  `deny` rules as a sufficient safety boundary under it.

Approval is capability, not authority
([`core-model.md`](../core-model.md#authority-and-transitions)). Being allowed to
run a tool does not authorize merge, release, tag, destructive, or externally
visible actions; those remain human-gated (see
[Delivery And Stop Conditions](#delivery-and-stop-conditions)).

## Command Execution

Claude executes Bash commands as separate processes. In the main session,
working-directory changes may carry over within the project or explicitly added
directories, but shell environment changes such as `export`, `source`, aliases,
and virtual-environment activation do not persist between calls; subagent
working-directory changes do not persist. Keep commands self-contained and
follow the
[command-form rule](../repo-readiness.md#command-form-and-intent-visibility):
run ordinary repository operations in direct, single-purpose form (`git status`,
`gh pr view <n>`, `make check`) rather than wrapping them in extra `bash -lc`,
aliases, or compound-shell layers that hide intent. Claude may issue independent
tool calls in parallel; keep parallel calls to independent read-only inspection
and never parallelize mutating Git or overlapping worktree operations.

Isolation comes from the permission model and the working directory or Git
worktree, not from a writable-root sandbox. Keep durable artifacts in the
repo-local paths in
[`repo-readiness.md`](../repo-readiness.md#repo-local-workflow-state); use OS
temp locations only for short-lived process-local files.

## Worktrees And Subagents

Apply the one-repository, one-branch, one-worktree, one-PR rule and
`<repo>/.worktrees/` placement from
[`repo-readiness.md`](../repo-readiness.md#pr-readiness) unchanged; create
repo-changing worktrees with direct `git worktree add` naming the full
`.worktrees/<task-name>` path.

Non-fork Claude subagents (`Task` tool) start with a separate context and do not
receive the parent conversation history or files the parent previously read, so
give each one a complete, self-contained envelope rather than relying on implicit
conversational context: repository and working directory, interaction mode and
deliverable, goal, scope and exclusions, source evidence or retrieval
instructions, validation path, and stop conditions (this is the standalone-worker
requirement in
[`orchestration-and-parallelism.md`](../orchestration-and-parallelism.md)).
Worker authority stops at the envelope; a worker must not merge, enable
auto-merge, update other branches, or continue into downstream reconciliation
unless the human authorizes that step.

## Context Compaction And Recovery

Claude Code auto-compacts before the context window fills and supports `/compact`
and session resume (`--resume`, `--continue`). Compaction replaces earlier turns
with a summary. Treat compacted or resumed conversation as navigation, not
authority: after either, re-retrieve authoritative repository, PR, issue, CI, and
file state before relying on it, per
[`source-first-retrieval.md`](../source-first-retrieval.md) and
[durable continuity](../core-model.md#durable-continuity).

## Connectors

Claude reaches remote services, including GitHub, through MCP servers. Apply the
[runtime-evidence rule](../start-here.md#connector-availability-is-runtime-evidence):
inspect available connector actions or attempt the operation before claiming a
capability is unavailable, and treat a successful call as evidence it remains
available. For GitHub PR and issue work, prefer connector-first inspection per
[`review-packet.md`](../review-packet.md#direct-pr-inspection); direct `git` and
`gh` supplement it and remain appropriate for verified connector gaps or
repo-local workflows.

## Claude Model, Thinking, And Thread Routing

Choose the lowest-cost Claude Code model/configuration expected to preserve the
confidence required by the bounded task. Do not infer a mapping from OpenAI
model names or tiers. Current Claude Code documentation, checked 2026-08-10,
establishes the executor-native `haiku`, `sonnet`, and `opus` aliases: Haiku for
simple fast tasks, Sonnet for daily coding, and Opus for complex reasoning.
Anthropic's current platform model guidance independently positions Haiku 4.5
for fast, high-volume, cost-sensitive work; Sonnet 5 for coding, agents, and
enterprise workflows; and Opus 5 for complex agentic coding and enterprise
work. Exact model IDs, aliases, model availability, context variants, and
administrator allowlists are runtime evidence, not this adapter's assumption.
The broader platform catalog also lists Claude Fable 5; it is outside this
Claude Code routing matrix because the current Claude Code model configuration
documents `haiku`, `sonnet`, and `opus` as its selectable task-routing aliases.

| Claude task class | Default Claude Code model | Thinking/effort guidance | Escalate when | Downgrade/follow up when |
| --- | --- | --- | --- | --- |
| Deterministic external verification; hashes, inventories, evidence citations; simple source inspection; mechanical fallback verification | `haiku` | Use executor default; Claude Code does not document effort control for Haiku | a result is ambiguous, changes a decision, or source access is insufficient | substantive review has converged and a qualified deterministic check remains |
| Implementation review; evidence-package review; reviewer follow-up after substantive convergence; bounded long-context evidence synthesis | `sonnet` | Use `high` for intelligence-sensitive review where the active runtime supports effort; otherwise preserve the executor default | residual findings repeat, evidence conflicts, or semantics remain unresolved | split inventories, hashes, and other externally checkable claims to Haiku or another qualified mechanism |
| Substantive adversarial code review; protocol/design review; architecture review; authority or security-boundary review | `opus` | Use `xhigh` where the active runtime supports it; otherwise use the highest supported setting justified by the bounded review | a new trust boundary, unresolved architecture/security implication, conflicting authority, or a finding that changes qualification disposition appears | after substantive convergence, delegate only the remaining mechanical claim; do not relabel it as substantive review |

The table is a conservative routing hypothesis, not a quality-parity claim. A
large evidence package does not automatically require Opus, and a small
authority-boundary change may. Do not downgrade when error consequences are
high, ambiguity is material, independent verification is weak, work is hard to
reverse, or failure could silently corrupt authority or evidence.

### Thinking And Effort

Claude's thinking and effort controls are distinct from model choice where the
active Claude surface supports them. Anthropic documents adaptive thinking and
an `effort` parameter on current supported models; its Claude Code documentation
lists the actual model/effort combinations and says the effort scale is
calibrated per model. Use the executor's canonical terminology and supported
values rather than treating `light`, `medium`, and `high` as portable numeric
equivalents. For current Claude Code, `low`, `medium`, `high`, `xhigh`, and
`max` availability depends on the selected model; verify the effective choice
at runtime. Do not invent a Haiku effort setting where the executor does not
offer one.

### Thread Routing And Review Boundaries

Apply the shared `FRESH THREAD`, `SAME THREAD`, and `CHILD TASK` vocabulary in
[`prompts.md`](../prompts.md#thread-routing-and-configuration-continuity). For
a FRESH THREAD, choose this matrix's task-appropriate model and supported
thinking/effort setting. For a SAME THREAD, preserve the existing parent model
and thinking/effort configuration by default: a cheaper setting being sufficient
for the current sub-phase does not itself justify changing the running task.
For a CHILD TASK, select the lowest-cost sufficient Claude configuration for the
bounded child and preserve its inputs, configuration, execution identity,
durable result, and authority boundary where the workflow requires it.

If a lower-capability SAME THREAD reaches unresolved ambiguity, an architecture
or authority decision, conflicting authoritative evidence, repeated residual
correctness findings, an unexplained invariant, a new trust boundary, or a
decision-relevant uncertainty, prefer a bounded stronger child or explicit
fresh-thread transition over mutating the parent silently. If a stronger parent
reaches deterministic follow-up, delegate the bounded check to Haiku or another
qualified mechanism where worthwhile instead of downgrading the parent solely
for cost.

Reviewer independence is separate from model, thinking/effort, and thread
routing. A qualified separate Claude invocation can supply the selected external
review only when it meets the reviewer contract; an internally spawned Codex
review remains Codex review. Mechanical external verification and Codex
mechanical fallback must be labeled as their actual mechanism and never
retroactively stand in for substantive external review. CAK-106 is observational
workflow evidence only: substantive authority/process findings justified deeper
review, while later evidence-precision, environment-limited verification, and
mechanical follow-up were candidates for a bounded qualified mechanism. It does
not establish savings, quality parity, or cross-vendor equivalence.

### Prompt Operator Metadata

When an operator prepares a Claude prompt, use one complete metadata block:

```text
Operator metadata (do not include in prompt)
Thread routing: <FRESH THREAD | SAME THREAD | CHILD TASK>
Recommended model: <FRESH THREAD/CHILD TASK: haiku | sonnet | opus; SAME THREAD: Preserve current thread model>
Recommended thinking/effort: <FRESH THREAD/CHILD TASK: supported executor setting; SAME THREAD: Preserve current thread setting>

Reason:
<one concise task-specific selection or continuity justification>
```

This metadata is operator guidance, not task authority. Do not recommend a
model, effort, or child configuration that the current Claude surface cannot
support.

## Reasoning And Model Configuration

When a material prompt uses the product-neutral reasoning class in
[`prompt-contracts.md`](../prompt-contracts.md) (`light`, `medium`, `high`), the
Claude representation is a supported thinking/effort setting plus model
selection chosen for the bounded task. Concrete model names and thinking budgets are adapter
configuration and attempt-receipt metadata, not the meaning of the class.
Preserve whether the class and each capability are mandatory or advisory; if the
available Claude surface cannot meet a mandatory requirement without weakening a
guarantee, fail closed rather than silently downgrade. A model change alone does
not justify a prompt rewrite; preserve existing behavior first, then make
surgical changes tied to an observed failure.

## Local GitHub And Environment Preflight

`scripts/codex-preflight` checks local GitHub SSH auth, `gh` auth, and repository
reachability — executor-neutral environment readiness. When Claude drives
repository automation or worker fan-out, run it first and stop on a non-zero
exit:

```text
cd /Users/keith/src/ctrl-alt-keith/ai-workflow-playbook
./scripts/codex-preflight
```

## Delivery And Stop Conditions

Follow the PR readiness, validation, and delivery rules in
[`repo-readiness.md`](../repo-readiness.md) and repo-local `AGENTS.md`. On
completion, report the PR link when one was opened or updated, files changed,
validation results, and known blockers or residual risks.

Pause and ask for human input when the repository, branch, or worktree context
appears wrong, the scope is ambiguous or has shifted, required source state
cannot be retrieved, more than one valid path depends on human judgment, or the
next step is merge, release, tag, destructive, externally visible, or
permissions-sensitive.

## References

Behavioral claims above are grounded in official Anthropic documentation,
including [memory](https://docs.claude.com/en/docs/claude-code/memory),
[permissions](https://code.claude.com/docs/en/permissions),
[the tools reference](https://code.claude.com/docs/en/tools-reference),
[subagents](https://docs.claude.com/en/docs/claude-code/sub-agents), and
[worktrees](https://code.claude.com/docs/en/worktrees). Model-routing claims
above are additionally derived from Anthropic's official [Claude Code model
configuration](https://code.claude.com/docs/en/model-config), [model-selection
guide](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model),
[models overview](https://platform.claude.com/docs/en/about-claude/models/overview),
and [thinking guide](https://platform.claude.com/docs/en/about-claude/models/extended-thinking-models),
checked 2026-08-10.
