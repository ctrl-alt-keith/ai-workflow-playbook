# Start Here

## Purpose

- This playbook defines the canonical workflow for AI-assisted repository work.
- Use this page to quickly orient before performing tasks.

## Read Order

- `docs/engineering-baseline.md` -> foundational engineering expectations
- `docs/source-first-retrieval.md` -> execution ordering for deterministic
  repository triggers, source-of-truth gates, and continuity constraints
- `docs/authoritative-source-check.md` -> advisory source scanner adoption and
  reusable workflow operations
- `docs/repo-readiness.md` -> repository workflow expectations
- `docs/repo-awareness-onboarding-refresh.md` -> repository inventory and
  governance refresh procedure
- `docs/tool-adapters/codex.md` -> required adapter guidance for Codex
  executions; mandatory startup material for Codex runs, not optional
  deep-reference material
- `docs/tool-adapters/` -> documented adapter guidance for other executors,
  when a matching adapter exists
- `docs/maintenance-automations.md` -> recurring Codex maintenance automation expectations
- `docs/prompts.md` -> reusable prompt templates

## Execution Model

- Use `ai-workflow-playbook` as the canonical source of reusable workflow rules.
- Treat `AGENTS.md` as the repo-local execution layer; repo-local rules take
  precedence only for repo-specific behavior.
- Treat playbook changes and `AGENTS.md` edits as separate work types. Edit
  `AGENTS.md` only with explicit authorization or when the task's primary
  purpose is `AGENTS.md` update, rollout, or enforcement.
- Before acting on repository or software work, determine the interaction mode
  using `docs/repo-readiness.md`: implementation, review/audit, or
  orchestration/prompt-authoring. This applies before implementation, review,
  audit, architecture analysis, workflow analysis, PR/issue/branch
  recommendations, "what changed?", and "what should we do next?" responses.
- Deterministic workflow triggers, operational invariants, and source-of-truth
  retrieval requirements execute before conversational interpretation,
  continuity, or summary-based reasoning.
- When the human asks for a concrete operational action and the needed tools
  and context are available, perform that action before discussing workflow
  philosophy, intent analysis, or speculative improvements. Examples include
  inspecting a repo or PR, generating the requested implementation prompt,
  reviewing the actual PR, updating an open PR, or running validation.
- Conversational coherence is subordinate to operational trigger handling:
  references to authoritative operational state, including pull requests,
  issues, repositories, runtime state, CI state, files, logs, and uploaded
  artifacts, require retrieval or revalidation before conversational
  continuation.
- Repo-aware advisory and evaluation requests are retrieval tasks first and
  advisory tasks second when a repository is explicitly named and the answer
  depends on that repository's actual state.
- In fresh threads, assume no repository, pull request, branch, issue, or local
  path state is verified until the referenced source is directly inspected.
- Treat advisory summaries, generated snapshots, organization briefs, staged
  notes, memory, and conversational context as aids for finding what to inspect,
  not proof of current repository state.
- Conversational fluency, prior thread context, summaries, inferred intent, and
  pasted descriptions must not suppress required retrieval, inspection, or
  validation steps.
- If authoritative state is accessible through available tools or connectors,
  retrieve it before asking the human to restate, summarize, or paste it. Merely
  acknowledging missing state without performing available retrieval is not
  sufficient recovery.
- If referenced repository state was not directly verified, state
  `unknown → referenced repo state was not verified` before answering from that
  state.
- When a deterministic trigger applies, perform the required retrieval or
  inspection first, then continue the conversation from the inspected state. If
  the required source is unavailable, report that blocker instead of inferring
  the state from conversation.
- Anti-pattern: a human references a PR, and the assistant continues
  philosophical or meta discussion instead of retrieving the PR state.
- Anti-pattern: the assistant recognizes an operational request but explains
  the workflow problem instead of performing the available action.
- Anti-pattern: the assistant asks the human to paste retrievable PR, CI, file,
  log, or artifact state instead of inspecting the available source.
- Use `docs/source-first-retrieval.md` for the reusable trigger
  classification, ordering model, verification gate, and failure handling.

## Startup Contract

Before acting on repository or software work, including read-only analysis,
review, audit, advisory, architecture/workflow analysis, PR/issue/branch
recommendations, and "what changed?" or "what should we do next?" requests:

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

- The execution model above owns the playbook-vs-`AGENTS.md` boundary.
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
- Durable workflow guidance moves from staging to bounded repo work, then to an
  evidence-supported playbook promotion and notes cleanup when it proves
  reusable.
- Treat repository code, tests, docs, reviews, and merged PRs as the evidence
  source for reusable lessons before promoting them into the playbook.
- Canonical guidance should generally describe staging and incubation by role;
  use concrete private repository names when operational paths, examples,
  provenance, or ecosystem topology need them.

## Rule of Thumb

- Prefer small, scoped changes.
- Report whether a workflow change is canonical playbook guidance only or an
  explicitly authorized `AGENTS.md` update/enforcement task.
- Follow `docs/repo-readiness.md` for implementation isolation, command form,
  interaction mode, and validation rules.
- Open PRs ready for review by default unless explicitly instructed otherwise.
