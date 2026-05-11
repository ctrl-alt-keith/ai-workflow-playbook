# Start Here

## Purpose

- This playbook defines the canonical workflow for AI-assisted repository work.
- Use this page to quickly orient before performing tasks.

## Read Order

- `docs/engineering-baseline.md` -> foundational engineering expectations
- `docs/repo-readiness.md` -> repository workflow expectations
- `docs/tool-adapters/codex.md` -> required adapter guidance for Codex
  executions; mandatory startup material for Codex runs, not optional
  deep-reference material
- `docs/tool-adapters/` -> documented adapter guidance for other executors,
  when a matching adapter exists
- `docs/maintenance-automations.md` -> recurring Codex maintenance automation expectations
- `docs/prompts.md` -> reusable prompt templates

## Execution Model

- Use `ai-workflow-playbook` as the canonical source of reusable workflow rules.
- Treat `AGENTS.md` as the repo-local execution layer.
- Repo-local rules take precedence only for repo-specific behavior.
- Treat canonical playbook changes and `AGENTS.md` edits as separate work
  types. Updating the playbook does not implicitly authorize any `AGENTS.md`
  edit, including in `ai-workflow-playbook` itself.
- Edit `AGENTS.md` only with explicit user authorization or when the task's
  primary purpose is `AGENTS.md` update, rollout, or enforcement.
- Before acting on repository or software work, determine the interaction mode
  using `docs/repo-readiness.md`: implementation, review/audit, or
  orchestration/prompt-authoring.

## Startup Contract

Before acting on repository or software work:

1. Read `docs/start-here.md` first.
2. Read the target repository's repo-local `AGENTS.md`.
3. Identify the current executor and apply any matching documented adapter:
   - For Codex, read and apply `docs/tool-adapters/codex.md` before
     implementation, review/audit, or orchestration/prompt-authoring work.
     Codex adapter guidance is part of the startup contract for Codex runs, not
     optional reference material.
   - For other executors, read and apply the matching file under
     `docs/tool-adapters/` when one exists.
   - When no matching adapter exists, continue with the executor-neutral core
     startup guidance and repo-local `AGENTS.md`; do not infer tool-specific
     obligations or capability parity from references to other executor
     ecosystems.
4. Select the interaction mode before acting: implementation, review/audit, or
   orchestration/prompt-authoring.
5. Identify the canonical source for the rule, behavior, or context being used.
6. Confirm the command form and execution settings for planned repository
   commands, especially direct `git` and `gh` usage.
7. Identify the repository's canonical validation path.
8. Act only after those checks are clear, or report the blocker,
   uncertainty, or missing context.

## Adapter Authority

- Only documented adapter files under `docs/tool-adapters/` are authoritative
  for executor-specific workflow behavior.
- Mentions of other AI tools, reviewers, or executor ecosystems elsewhere in
  the playbook provide context unless a matching adapter promotes the behavior
  into tool-specific guidance.
- If a task needs executor-specific behavior that no adapter documents, keep
  the reusable workflow policy executor-neutral and report the missing adapter
  guidance instead of inventing a stub workflow.

## Source Authority Map

- `ai-workflow-playbook` is the canonical source for reusable workflow policy.
- Repo-local `AGENTS.md` files are repo-local execution guidance layered on top
  of the playbook.
- `AGENTS.md` alignment is update, enforcement, or rollout work, not a side
  effect of changing canonical playbook guidance.
- Incubation, staging, and evidence repositories, including
  `ai-workflow-incubator`, are noncanonical unless a durable rule is explicitly
  promoted into the playbook.
- Runtime artifacts, generated snapshots, copied custom instructions, local
  workspace instructions, and temporary operational notes are reference or
  execution surfaces, not canonical reusable policy unless they are explicitly
  promoted.

## Staging vs Playbook

- The private staging/incubation layer is for ideas and experiments.
- It is not canonical and is not a direct path into playbook guidance.
- Durable workflow guidance follows this order: idea -> notes staging ->
  bounded repo issue or PR -> evidence-supported reusable lesson -> playbook
  promotion -> notes cleanup.
- Treat repository code, tests, docs, reviews, and merged PRs as the evidence
  source for reusable lessons before promoting them into the playbook.
- Canonical guidance should generally describe staging and incubation by role;
  use concrete private repository names when operational paths, examples,
  provenance, or ecosystem topology need them.

## Rule of Thumb

- Prefer small, scoped changes.
- Report whether a workflow change is canonical playbook guidance only or an
  explicitly authorized `AGENTS.md` update/enforcement task.
- For global rollout and implementation changes, use one repository, one
  branch, one dedicated worktree, and one pull request per target repository
  unless that repository's documented process says otherwise.
- In ctrl-alt-keith workflows, default ambiguous repository tasks to
  review/audit or orchestration/prompt-authoring unless the human explicitly
  asks for direct implementation.
- Run commands directly from inside the target repository worktree; follow
  `docs/repo-readiness.md` for command form and shell-wrapping rules.
- Run repository validation through the repo's Makefile when it provides the
  canonical entrypoint.
- Open PRs ready for review by default unless explicitly instructed otherwise.
