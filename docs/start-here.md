# Start Here

## Purpose

This page is the routing entry point for AI-assisted repository work. Use it
to identify the governing docs, startup checks, and compact invariants before
acting.

## Read Order

- `docs/engineering-baseline.md` -> foundational engineering expectations
- `docs/source-first-retrieval.md` -> retrieve and revalidate authoritative
  state before stateful repository reasoning
- `docs/repo-readiness.md` -> interaction mode, command form, worktree, branch,
  validation, and PR expectations
- `docs/tool-adapters/codex.md` -> required Codex-specific deltas for Codex
  executions
- `docs/tool-adapters/` -> adapter guidance for other executors when a
  matching adapter exists
- `docs/authoritative-source-check.md` -> advisory source scanner workflow
- `docs/repo-awareness-onboarding-refresh.md` -> repository inventory refresh
- `docs/maintenance-automations.md` -> recurring Codex maintenance automation
  expectations
- `docs/prompts.md` -> reusable prompt templates

## Startup Contract

Before repository or software work, including read-only review, audit,
advisory, architecture/workflow analysis, PR/issue/branch recommendations, and
"what changed?" or "what should we do next?" requests:

1. Read this page.
2. Read the target repository's repo-local `AGENTS.md`.
3. Apply the matching executor adapter. Codex runs must apply
   `docs/tool-adapters/codex.md`.
4. Select the interaction mode from `docs/repo-readiness.md`: implementation,
   review/audit, or orchestration/prompt-authoring.
5. Identify the canonical source for the rule, behavior, or state being used.
6. Confirm command form and execution settings for planned repository commands.
7. Identify the repository's canonical validation path.
8. Act only after those checks are clear, or report the blocker, uncertainty,
   or missing context.

## Core Invariants

- `ai-workflow-playbook` is the canonical source for reusable workflow rules.
- `AGENTS.md` is the repo-local execution layer; repo-local rules take
  precedence only for repo-specific behavior.
- Playbook changes and `AGENTS.md` edits are separate work types. Edit
  `AGENTS.md` only with explicit authorization or when the task's primary
  purpose is an `AGENTS.md` update, rollout, or enforcement.
- Deterministic repository triggers run before conversational interpretation:
  retrieve or revalidate authoritative source state before claims about current
  PRs, issues, branches, commits, CI, validation, files, runtime state, or
  external provider/API behavior.
- Advisory summaries, generated snapshots, staged notes, memory, pasted
  descriptions, and conversational context can help find what to inspect. They
  are not proof of current repository state.
- If referenced repository state was not directly verified, state
  `unknown → referenced repo state was not verified` before answering from
  that state.
- When retrieval was missed and remains available, recovery starts by doing
  the missed retrieval or revalidation, then correcting or marking prior
  assumptions as unverified.
- If the human asks for a concrete operational action and the needed tools and
  context are available, do the action before discussing workflow intent,
  philosophy, or speculative improvements.
- Only documented adapter files under `docs/tool-adapters/` are authoritative
  for executor-specific workflow behavior.
- Incubation, staging, runtime artifacts, generated snapshots, copied custom
  instructions, local workspace instructions, and temporary operational notes
  are noncanonical unless a durable rule is explicitly promoted into the
  playbook.

## Rule of Thumb

- Prefer small, scoped changes.
- Keep changes in the target repository, branch, and worktree.
- Follow `docs/repo-readiness.md` for implementation isolation, command form,
  interaction mode, validation, and PR readiness.
- Open PRs ready for review by default unless explicitly instructed otherwise.
