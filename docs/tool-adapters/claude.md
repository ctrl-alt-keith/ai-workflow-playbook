# Claude Adapter

This adapter records Claude Code-specific deltas on top of the core playbook.
Use it with [`start-here.md`](../start-here.md),
[`core-model.md`](../core-model.md),
[`source-first-retrieval.md`](../source-first-retrieval.md),
[`repo-readiness.md`](../repo-readiness.md), and the target repo's `AGENTS.md`;
do not treat it as a second copy of those rules.

This adapter intentionally does not mirror the Codex adapter. Where the two
executors share behavior, the shared rule stays in its canonical playbook doc
and this file only records what is genuinely different for Claude Code. Where an
analogous Codex concept has no Claude equivalent, such as Codex's writable-root
sandbox or its argv/`shell=false` execution toggle, this adapter says so instead
of restating the Codex mechanics.

## Claude-Specific Quirks

- Claude Code loads its instruction and permission context from files and
  settings rather than from a single prompt; instruction discovery below is the
  most important delta to get right for repositories that standardize on
  `AGENTS.md`.
- Claude 4.x models fire tool calls, including `Bash`, in parallel and can be
  aggressive about it. Keep parallel calls to independent, non-mutating
  inspection; do not parallelize mutating Git operations or overlapping worktree
  changes.
- Claude can produce fluent summaries that still require source inspection and
  human judgment on scope, tradeoffs, and completion. Apply
  [`source-first-retrieval.md`](../source-first-retrieval.md) before stateful
  conclusions.

## Instruction Discovery And Precedence

Claude Code natively auto-loads `CLAUDE.md` memory at session start: a
project-level `CLAUDE.md` or `.claude/CLAUDE.md` in the working directory, a
user-level `~/.claude/CLAUDE.md`, and any files those import. This repository
family instead treats repo-local `AGENTS.md` as the canonical repository
execution layer, and the startup contract in
[`start-here.md`](../start-here.md#required-repository-startup-contract) requires
reading the target repository's `AGENTS.md`.

Because Claude's automatic memory loading is `CLAUDE.md`-centric and does not
guarantee that `AGENTS.md` is ingested, Claude must explicitly read the target
repository's `AGENTS.md` to satisfy the startup contract. Do not assume
auto-loaded memory already covers repo-local execution policy.

- Do not fork or duplicate `AGENTS.md` (or shared playbook doctrine) into a
  `CLAUDE.md`. Canonical ownership stays with `AGENTS.md` and the shared docs;
  duplicating it creates a competing instruction copy that can drift. See
  [`repo-readiness.md`](../repo-readiness.md#agentsmd-responsibilities).
- If a `CLAUDE.md` is used in a repository, keep it a thin pointer to
  `docs/start-here.md` and the repo's `AGENTS.md`, not a second policy source.
- Claude's memory files and settings are a transport for instructions, not a new
  authority layer. The Repository Instruction Hierarchy in
  [`start-here.md`](../start-here.md#repository-instruction-hierarchy) still
  governs: the human's explicit task, then repo-local `AGENTS.md`, then this
  adapter, then shared playbook defaults. A user-level `~/.claude/CLAUDE.md`
  carries operator context and does not override repo-local policy.

## Interaction Mode And Permission Behavior

Apply the interaction-mode preflight in
[`repo-readiness.md`](../repo-readiness.md#interaction-mode-preflight) first.
Claude Code's permission modes map onto those modes but do not replace them:

- Plan mode analyzes and plans without mutating the repository, which fits
  review/audit and orchestration/prompt-authoring. For ctrl-alt-keith
  workflows, ambiguous repository tasks default to review/audit or
  orchestration/prompt-authoring, so prefer plan mode until the human explicitly
  asks Claude to implement, commit, push, or open the PR.
- Default mode implements with per-action approval and suits implementation
  mode with a human in the loop.
- `acceptEdits` suits bounded implementation once scope and approach are agreed.
- `bypassPermissions` should be avoided for repository mutation with real blast
  radius.

A permission approval is capability, not authority
([`core-model.md`](../core-model.md#authority-and-transitions)). Being allowed
to run a tool does not authorize merge, release, tag, destructive, or
externally visible actions; those remain human-gated (see
[Delivery And Stop Conditions](#delivery-and-stop-conditions)). Deny rules in
settings are evaluated first
and hold even under `bypassPermissions`, so prefer explicit deny rules for
push, merge, and destructive operations over relying on interactive prompts.

## Sandbox And Command Execution

Claude Code does not use Codex's `workspace-write` writable-root sandbox. The
Codex adapter's `effective-sandbox-check`, `writable_roots`, and temp-root
exclusion mechanics do not apply to Claude and are not reproduced here.
Isolation for Claude comes from the permission model and the working directory
or Git worktree, not from writable-root configuration. Keep durable workflow
artifacts in the repo-local paths named by
[`repo-readiness.md`](../repo-readiness.md#repo-local-workflow-state); use OS
temp locations only for short-lived process-local files.

Claude runs shell commands through the `Bash` tool as a persistent shell
session, so it cannot toggle the native argv / `shell=false` execution that the
Codex adapter describes; that specific Codex instruction does not transfer. The
shared intent from
[`repo-readiness.md`](../repo-readiness.md#command-form-and-intent-visibility)
still holds: run ordinary repository operations in direct, single-purpose form
such as `git status`, `gh pr view <n>`, and `make check`, and do not bury them
in extra `bash -lc`, alias, or compound-shell layers that hide operational
intent. Use shell composition only when it is genuinely required, and keep the
wrapped command narrow enough to stay reviewable.

## Worktrees And Worker Isolation

The one-repository, one-branch, one-worktree, one-PR rule and the
`<repo>/.worktrees/` placement are owned by
[`repo-readiness.md`](../repo-readiness.md#pr-readiness) and repo-local
`AGENTS.md`; apply them unchanged. Claude's native worktree pattern, a separate
checkout per branch created from an existing commit, fits this directly. Create
repo-changing worktrees with direct `git worktree add` naming the full
`.worktrees/<task-name>` path, and reuse a worktree only when it clearly belongs
to the same active task.

Claude subagents (the `Task` tool) run in a separate context window with a
self-contained prompt and report a summary back to the orchestrator; they do not
inherit the parent conversation. This matches the standalone-worker-prompt
requirement in
[`orchestration-and-parallelism.md`](../orchestration-and-parallelism.md)
natively, so Claude does not need the Codex caveat about avoiding
"fork this conversation." Give each subagent a complete envelope: repository and
working directory, interaction mode and deliverable, goal, scope and exclusions,
source evidence or retrieval instructions, validation path, and stop conditions.
Worker authority stops at the assigned envelope; a worker must not merge, enable
auto-merge, update other branches, or continue into downstream reconciliation
unless the human explicitly authorizes that step.

## Context Compaction And Conversation Recovery

Claude Code auto-compacts the conversation before the context window fills and
also supports manual `/compact` and session resume (`--resume`, `--continue`,
and the resume picker). Compaction replaces earlier turns with a summary, and a
resumed session keeps the model it was using when the transcript was saved.

Treat compacted or resumed conversation as navigation, not authority. This is
the same durable-continuity rule the playbook already states in
[`core-model.md`](../core-model.md#durable-continuity) and
[`source-first-retrieval.md`](../source-first-retrieval.md); compaction and
resume simply make it operationally important for Claude. After a compaction or
resume, re-retrieve authoritative repository, PR, issue, CI, and file state
before relying on it rather than trusting the summarized context.

## Connectors

Claude reaches remote services, including GitHub, through MCP servers. Apply the
runtime-evidence rule in
[`start-here.md`](../start-here.md#connector-availability-is-runtime-evidence):
inspect the available connector actions or attempt the operation before claiming
a capability is unavailable, and treat a successful call as positive evidence
that the capability remains available. For GitHub PR and issue work, prefer
connector-first inspection per
[`review-packet.md`](../review-packet.md#direct-pr-inspection) and
[`source-first-retrieval.md`](../source-first-retrieval.md); direct `git` and
`gh` supplement that inspection and remain appropriate for verified connector
gaps or repo-local workflows.

## Reasoning And Model Configuration

When a material prompt uses the product-neutral reasoning class in
[`prompt-contracts.md`](../prompt-contracts.md) (`light`, `medium`, or `high`),
the Claude representation is an extended-thinking budget together with model
selection, chosen from the bounded task shape. Concrete model names and thinking
budgets are adapter configuration and attempt-receipt metadata; they are not the
semantic meaning of the reasoning class.

- Preserve whether the reasoning class and each required capability are
  mandatory or advisory. If the available Claude surface cannot satisfy a
  mandatory class or capability without weakening a guarantee, the attempt fails
  closed rather than silently downgrading.
- A model change alone does not justify a prompt rewrite; preserve existing
  behavior and settings first, then make surgical changes tied to an observed
  failure.

The full Codex operator-metadata rendering (the `Light | Medium | High` block)
is the Codex representation of that reasoning class and is not reproduced here.
A product-neutral Claude rendering of reasoning-selection guidance is deferred
until it is needed; see the shared owner in
[`prompt-contracts.md`](../prompt-contracts.md).

## Local GitHub And Environment Preflight

`scripts/codex-preflight` verifies local GitHub SSH authentication, `gh`
authentication, and playbook repository reachability. Those checks are
executor-neutral GitHub and environment readiness, not Codex mechanics, so a
Claude automation run benefits from the same preflight. When Claude drives
repository automation or worker fan-out, run it first and stop on a non-zero
exit:

```text
Before starting repository work, run:

cd /Users/keith/src/ctrl-alt-keith/ai-workflow-playbook
./scripts/codex-preflight

If it exits non-zero, stop and report the failing check and remediation.
```

Claude does not need a separate preflight script; a duplicate would fork
canonical executable behavior, which the engineering baseline prohibits. The
future rename of this shared check is tracked as deferred work in the pull
request that introduced this adapter.

## Delivery And Stop Conditions

Follow the PR readiness, validation, and delivery rules in
[`repo-readiness.md`](../repo-readiness.md) and repo-local `AGENTS.md`. When
reporting completion for implementation work, include the PR link when one was
opened or updated, files changed, validation results, and any known blockers or
residual risks.

Pause and ask for human input when the repository, branch, or worktree context
appears wrong, the scope is ambiguous or has shifted, required source state
cannot be retrieved, more than one valid path depends on human judgment, or the
next step is merge, release, tag, destructive, externally visible, or
permissions-sensitive.

## References

Claude Code behavior described in this adapter is drawn from the official
Anthropic documentation, including
[Claude Code memory](https://docs.claude.com/en/docs/claude-code/memory),
[permissions](https://docs.claude.com/en/docs/claude-code/sdk/sdk-permissions),
[subagents](https://docs.claude.com/en/docs/claude-code/sub-agents), and
[common workflows](https://docs.claude.com/en/docs/claude-code/common-workflows).
