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

Core guidance should stay tool-agnostic whenever possible. The core docs should describe the operating model, lifecycle, checkpoints, and review expectations in language that survives tool changes.

Tool-specific behavior belongs in adapter docs under [`docs/tool-adapters/`](docs/tool-adapters/). Adapters may explain how a specific tool maps onto the core model, but they should not redefine the model itself.

## Current Focus

The first core module is delivery. Additional workflow families may be added later, but only if they meet the same discipline standards and stay aligned with the repository intent.

## Initial Map

- [`docs/core-model.md`](docs/core-model.md): high-level operating model
- [`docs/feature-lifecycle.md`](docs/feature-lifecycle.md): delivery lifecycle
- [`docs/alignment-checkpoints.md`](docs/alignment-checkpoints.md): pause points and branch/PR rules
- [`docs/review-packet.md`](docs/review-packet.md): standard human review packet
- [`docs/tool-adapters/codex.md`](docs/tool-adapters/codex.md): Codex-specific adapter notes
- [`docs/playbook-integrity-check.md`](docs/playbook-integrity-check.md): lightweight anti-drift check
- [`docs/new-repo-bootstrap.md`](docs/new-repo-bootstrap.md): reusable bootstrap pattern for brand-new repositories
