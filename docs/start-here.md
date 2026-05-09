# Start Here

## Purpose

- This playbook defines the canonical workflow for AI-assisted repository work.
- Use this page to quickly orient before performing tasks.

## Read Order

- `docs/engineering-baseline.md` -> foundational engineering expectations
- `docs/repo-readiness.md` -> repository workflow expectations
- `docs/maintenance-automations.md` -> recurring Codex maintenance automation expectations
- `docs/prompts.md` -> reusable prompt templates

## Execution Model

- Use `ai-workflow-playbook` as the canonical source of reusable workflow rules.
- Treat `AGENTS.md` as the repo-local execution layer.
- Repo-local rules take precedence only for repo-specific behavior.
- Before acting on repository or software work, determine the interaction mode
  using `docs/repo-readiness.md`: implementation, review/audit, or
  orchestration/prompt-authoring.

## Startup Contract

Before acting on repository or software work:

1. Read `docs/start-here.md` first.
2. Read the target repository's repo-local `AGENTS.md`.
3. Select the interaction mode before acting: implementation, review/audit, or
   orchestration/prompt-authoring.
4. Identify the canonical source for the rule, behavior, or context being used.
5. Confirm the command form for planned repository commands.
6. Identify the repository's canonical validation path.
7. Act only after those checks are clear, or report the blocker,
   uncertainty, or missing context.

## Source Authority Map

- `ai-workflow-playbook` is the canonical source for reusable workflow policy.
- Repo-local `AGENTS.md` files are repo-local execution guidance layered on top
  of the playbook.
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
- In ctrl-alt-keith workflows, default ambiguous repository tasks to
  review/audit or orchestration/prompt-authoring unless the human explicitly
  asks for direct implementation.
- Run commands directly from the target repository; follow
  `docs/repo-readiness.md` for command form and shell-wrapping rules.
- Run repository validation through the repo's Makefile when it provides the
  canonical entrypoint.
- Open PRs ready for review by default unless explicitly instructed otherwise.
