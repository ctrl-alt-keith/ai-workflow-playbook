# AI Workflow Playbook

`ai-workflow-playbook` is a reusable playbook for disciplined AI-assisted work.

Its purpose is to capture workflow patterns that have been proven in practice or are necessary to explain the core operating model behind reliable AI-assisted delivery. It is intentionally narrow: this is not a notebook, idea dump, or project-specific implementation repo.

## Scope

This repository should contain:

- Repeatable workflow patterns
- Proven heuristics
- Decision frameworks
- Reusable prompt structures
- Domain-independent operating principles and core operating-model guidance
  needed to apply the playbook well

## Non-Scope

This repository should not contain:

- Raw brainstorms
- One-off notes
- Vendor news or trend commentary
- Project-specific implementation docs
- Project-specific automation code, orchestration systems, or control planes
  that belong in a separate implementation repo

Small reusable checks that directly validate or demonstrate playbook guidance
may live here when they remain narrow, documented, and subordinate to the docs.

If an area grows into implementation, tooling, or automation, it should eventually move to its own repository.

## Guardrails

Use this repo only when content is:

- Reusable across more than one project
- Specific enough to guide execution
- Grounded in real usage, not speculation
- Small enough to strengthen the playbook instead of diluting it

Do not add content that behaves like a working notebook. If material is exploratory, unstable, or tied to one codebase, it does not belong here yet.

## Core And Adapters

Core guidance should stay tool-agnostic. The core docs should describe the
operating principles, operating model, lifecycle, checkpoints, and review
expectations in language that survives tool changes.

Tool-specific behavior belongs in documented adapter docs under [`docs/tool-adapters/`](docs/tool-adapters/). Adapters explain how a specific executor maps onto the core model, but they do not redefine the model itself. When no matching adapter exists, use the executor-neutral startup guidance and repo-local `AGENTS.md`; do not infer tool-specific requirements from another executor's adapter.

## Repo-Local AGENTS.md

The playbook is the canonical home for reusable workflow policy. Repo-local
`AGENTS.md` files provide thin repository execution guidance; see
[`docs/start-here.md`](docs/start-here.md#startup-contract) and
[`docs/repo-readiness.md`](docs/repo-readiness.md#agentsmd-responsibilities).

Reusable pattern:

> This repository uses the shared playbook in `ai-workflow-playbook` as the canonical source for reusable workflow rules. `AGENTS.md` provides the repo-specific instructions (validation, commands, PR expectations). Repo-local rules take precedence only for repo-specific behavior.

## Current Focus

The first core module is delivery. Additional workflow families may be added later, but only if they meet the same discipline standards and stay aligned with the repository intent.

## Local Projections

For the narrow set of workstation projections whose implementation is owned by
this Playbook, use the discoverable operator loop:

```text
make check-local
make plan-local
make apply-local
```

It composes component-owned contracts rather than treating provider homes as a
general configuration store. See the [global-bootstrap distribution](distributions/global-bootstrap/README.md#unified-local-projection-workflow)
for included components, the read-only boundary, and the explicit apply path.

## Initial Map

- [`docs/start-here.md`](docs/start-here.md): task-neutral startup routing and
  conditional repository workflow entry point
- [`docs/architecture-foundation-candidate.md`](docs/architecture-foundation-candidate.md):
  non-authoritative candidate under adversarial review; not current Playbook
  doctrine
- [`docs/constitutional-vocabulary-guide.md`](docs/constitutional-vocabulary-guide.md):
  implementation guidance for distinguishing Product authority, human
  governance authority, repository implementation, and runtime execution
- [`docs/constitutional-terminology-ratification-decision.md`](docs/constitutional-terminology-ratification-decision.md):
  accepted human governance decision recording ratified and deferred
  constitutional terminology
- [`docs/product-status.md`](docs/product-status.md): canonical current accepted
  Product status for the identities it lists
- [`docs/product-promotion-decisions/`](docs/product-promotion-decisions/):
  immutable provenance records for the human Product governance decisions that
  established current or prior status
- [`docs/repo-to-repo-interface-contracts.md`](docs/repo-to-repo-interface-contracts.md): lightweight pattern for documenting producer/consumer boundaries
- [`docs/cross-repo-glossary.md`](docs/cross-repo-glossary.md): qualified cross-repository architecture vocabulary
- [`docs/ai-workflow-ecosystem.md`](docs/ai-workflow-ecosystem.md): conceptual overview of the repository ecosystem, retained-knowledge boundaries, and architectural direction
- [`docs/engineering-baseline.md`](docs/engineering-baseline.md): foundational engineering expectations, including validation, source authority, review, merge authority, and ready-for-review defaults
- [`docs/authoritative-source-check.md`](docs/authoritative-source-check.md): advisory authoritative-source scanner adoption, domain classification, source justifications, and reusable workflow pinning
- [`docs/repo-readiness.md`](docs/repo-readiness.md): interaction-mode selection, governance operating model, workflow-state ownership and lifecycle classification, repository workflow expectations, validation taxonomy, and `AGENTS.md` responsibilities
- [`docs/repo-awareness-onboarding-refresh.md`](docs/repo-awareness-onboarding-refresh.md): repository discovery, inventory propagation, onboarding, and governance refresh procedure
- [`docs/core-model.md`](docs/core-model.md): canonical domain-independent AI
  operating principles, roles, authority, phases, and durable continuity
- [`docs/evidence-lifecycle.md`](docs/evidence-lifecycle.md): accepted evidence, integration, synthesis, semantic accounting, and reporting boundaries
- [`docs/feature-lifecycle.md`](docs/feature-lifecycle.md): delivery lifecycle, branch behavior, and PR completion expectations
- [`docs/alignment-checkpoints.md`](docs/alignment-checkpoints.md): pause points and branch/PR rules
- [`docs/review-packet.md`](docs/review-packet.md): standard human review packet
- [`docs/external-ai-reviewer.md`](docs/external-ai-reviewer.md): selecting,
  governing, and completing independent external-AI review
- [`docs/knowledge-ingestion-patterns.md`](docs/knowledge-ingestion-patterns.md): reusable patterns for provenance-aware ingestion and retained-knowledge governance boundaries
- [`docs/tool-adapters/`](docs/tool-adapters/): documented executor-specific adapter guidance; Codex runs must apply [`docs/tool-adapters/codex.md`](docs/tool-adapters/codex.md), Claude runs must apply [`docs/tool-adapters/claude.md`](docs/tool-adapters/claude.md), and repository-scoped ChatGPT runs must apply [`docs/tool-adapters/chatgpt.md`](docs/tool-adapters/chatgpt.md)
- [`docs/playbook-integrity-check.md`](docs/playbook-integrity-check.md): lightweight anti-drift check
- [`docs/new-repo-bootstrap.md`](docs/new-repo-bootstrap.md): reusable bootstrap pattern for brand-new repositories
- [`docs/maintenance-automations.md`](docs/maintenance-automations.md):
  autonomous maintenance layer responsibilities, capability classes, authority
  and evidence boundaries, and local-configuration separation
- [`docs/codex-preflight.md`](docs/codex-preflight.md): read-only local prerequisite check for Codex automation startup
- [`docs/workstation-maintenance.md`](docs/workstation-maintenance.md): manual-only local workstation maintenance procedures, including Codex log cleanup
- [`docs/prompts.md`](docs/prompts.md): reusable prompt templates, including the standard Codex task prompt format

> AI-generated. Human-verified. Occasionally argued about.
