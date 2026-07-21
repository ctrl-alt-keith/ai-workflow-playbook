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

## Reasoning And Model Configuration

When a material prompt uses the product-neutral reasoning class in
[`prompt-contracts.md`](../prompt-contracts.md) (`light`, `medium`, `high`), the
Claude representation is an extended-thinking budget plus model selection chosen
for the bounded task. Concrete model names and thinking budgets are adapter
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
[worktrees](https://code.claude.com/docs/en/worktrees).
