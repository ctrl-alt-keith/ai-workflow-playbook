# AI Workflow Playbook

`ai-workflow-playbook` is a reusable playbook for disciplined AI-assisted work.

Its purpose is to capture workflow patterns that have been proven in practice or are necessary to explain the core operating model behind reliable AI-assisted delivery. It is intentionally narrow: this is not a notebook, idea dump, or project-specific implementation repo.

## Scope

This repository should contain:

- Repeatable workflow patterns
- Proven heuristics
- Decision frameworks
- Reusable prompt structures
- Core operating-model guidance needed to apply the playbook well

## Non-Scope

This repository should not contain:

- Raw brainstorms
- One-off notes
- Vendor news or trend commentary
- Project-specific implementation docs
- Automation code or orchestration systems that belong in a separate implementation repo

If an area grows into implementation, tooling, or automation, it should eventually move to its own repository.

## Guardrails

Use this repo only when content is:

- Reusable across more than one project
- Specific enough to guide execution
- Grounded in real usage, not speculation
- Small enough to strengthen the playbook instead of diluting it

Do not add content that behaves like a working notebook. If material is exploratory, unstable, or tied to one codebase, it does not belong here yet.

## Core And Adapters

Core guidance should stay tool-agnostic. The core docs should describe the operating model, lifecycle, checkpoints, and review expectations in language that survives tool changes.

Tool-specific behavior belongs in documented adapter docs under [`docs/tool-adapters/`](docs/tool-adapters/). Adapters explain how a specific executor maps onto the core model, but they do not redefine the model itself. When no matching adapter exists, use the executor-neutral startup guidance and repo-local `AGENTS.md`; do not infer tool-specific requirements from another executor's adapter.

## Repo-Local AGENTS.md

The playbook is the canonical home for reusable workflow policy. A repo-local `AGENTS.md` is the execution layer for that repository, layered on top of the playbook and authoritative only for repo-specific validation, commands, and PR expectations. Playbook changes and `AGENTS.md` edits are separate work types; update `AGENTS.md` only with explicit authorization or when that update is the task's purpose.

Reusable pattern:

> This repository uses the shared playbook in `ai-workflow-playbook` as the canonical source for reusable workflow rules. `AGENTS.md` provides the repo-specific instructions (validation, commands, PR expectations). Repo-local rules take precedence only for repo-specific behavior.

## Workspace Bootstrap Bundle

Run `make workspace-bootstrap` to generate `dist/workspace-bootstrap.md`, a non-canonical hydration bundle for fresh-thread and project-source context loading. Canonical guidance remains in the source docs and repo-local `AGENTS.md`; the generated bundle is only a convenience snapshot and should be regenerated instead of edited directly.

Run `make context-refresh` to generate `dist/context-refresh.md`, a non-canonical repository orientation brief for fresh-thread handoff and repo orientation refresh. Dynamic PR and issue state is intentionally omitted; inspect GitHub directly before acting.

Run `make github-context` to generate `dist/github-context.md`, a paste-ready `@GitHub` repo list for connector rehydration in fresh threads. The artifact is non-canonical and generated from `config/workspace-repos.txt`.

These generated artifacts are complementary:

- `workspace-bootstrap` hydrates stable operating guidance.
- `context-refresh` captures durable repo orientation state.
- `github-context` rehydrates GitHub connector repo scope.

Repository code, issues, pull requests, docs, and repo-local `AGENTS.md` files remain the source of truth.

## Current Focus

The first core module is delivery. Additional workflow families may be added later, but only if they meet the same discipline standards and stay aligned with the repository intent.

## Initial Map

- [`docs/start-here.md`](docs/start-here.md): mandatory startup, source authority map, and adapter-routing contract
- [`docs/engineering-baseline.md`](docs/engineering-baseline.md): foundational engineering expectations, including validation, review, merge authority, and ready-for-review defaults
- [`docs/repo-readiness.md`](docs/repo-readiness.md): interaction-mode selection, repository workflow expectations, validation taxonomy, and `AGENTS.md` responsibilities
- [`docs/core-model.md`](docs/core-model.md): high-level operating model
- [`docs/feature-lifecycle.md`](docs/feature-lifecycle.md): delivery lifecycle, branch behavior, and PR completion expectations
- [`docs/alignment-checkpoints.md`](docs/alignment-checkpoints.md): pause points and branch/PR rules
- [`docs/review-packet.md`](docs/review-packet.md): standard human review packet
- [`docs/tool-adapters/`](docs/tool-adapters/): documented executor-specific adapter guidance; Codex runs must apply [`docs/tool-adapters/codex.md`](docs/tool-adapters/codex.md)
- [`docs/playbook-integrity-check.md`](docs/playbook-integrity-check.md): lightweight anti-drift check
- [`docs/new-repo-bootstrap.md`](docs/new-repo-bootstrap.md): reusable bootstrap pattern for brand-new repositories
- [`docs/context-refresh.md`](docs/context-refresh.md): verified context refresh primitive for durable repository orientation briefs
- [`docs/maintenance-automations.md`](docs/maintenance-automations.md): reusable operating rules plus reference inventory notes for recurring Codex maintenance automation
- [`docs/prompts.md`](docs/prompts.md): reusable prompt templates, including the standard Codex task prompt format

> AI-generated. Human-verified. Occasionally argued about.
