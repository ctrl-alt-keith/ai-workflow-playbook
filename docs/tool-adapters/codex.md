# Codex Adapter

This adapter records Codex-specific deltas on top of the core playbook. Use it
with `docs/start-here.md`, `docs/source-first-retrieval.md`,
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

## Startup Deltas

Before repo-scoped work:

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
- Treat summaries, memory, pasted descriptions, generated notes, and local
  branch state as navigation only until the relevant source has been inspected.
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

Use repo-local scratch paths for workflow artifacts that need review later. Use
temporary OS paths only for short-lived process-local files whose path and
contents do not matter after the command finishes.

## Autonomous Lane

Codex should continue without pausing when the scope is clear, the repo context
matches the task, required sources are available, validation can run, and no
human-gated decision is next.

Do not use autonomy to widen scope, reinterpret intent, or take ownership of
merge, release, tag, destructive, security-sensitive, permissions-sensitive, or
policy-interpretation decisions.

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
