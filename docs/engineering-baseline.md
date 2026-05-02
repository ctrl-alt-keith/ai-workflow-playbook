# Engineering Baseline

## Purpose

Define shared engineering expectations across repositories. This baseline forms the foundation for workflow rules in this playbook.

## Core Principles

- Small, scoped changes
  - One PR = one reason.
- Validate before PR
  - Use repo-defined validation, such as `make check`.
- Repository isolation
  - One repository per PR.
  - No cross-repo commits.
- Deterministic behavior
  - Prefer explicit, predictable outputs.
- Fail fast and clearly
  - Avoid silent no-ops.
- Minimal surface area
  - Avoid unnecessary features or complexity.
- Documentation for user-facing behavior
  - If behavior changes, document it.

## Git and PR Expectations

- Branch from current `main`.
- Update the branch against current `main` before PR.
- Keep commits clean and focused.
- PRs are ready for review by default.

## Public API Baselines

When a task changes code, tests, docs, risks, or user-facing claims that depend
on external public API behavior, establish the current behavior from official
sources before making the change.

- Applies to public APIs, SDKs, SaaS APIs, cloud providers, GitHub APIs, CLIs,
  package managers, and other external systems.
- Prefer authoritative, provider-controlled sources:
  - official provider documentation, such as TechDocs or API references
  - official OpenAPI or schema definitions
  - official SDK documentation
  - official release notes or changelogs
- Check official sources for behavior such as resource lifecycle or status
  semantics, region or location availability, pagination, rate limits and
  retryability, auth or token error behavior, deletion and idempotency
  semantics, eventual consistency or timing behavior, and SDK or CLI command
  behavior.
- If authoritative docs exist, use them as the primary source.
- Do not rely on blogs, forum posts, StackOverflow, third-party summaries,
  AI-generated content, model memory, stale historical knowledge, or inference
  where authoritative docs are available.
- If authoritative docs are ambiguous or cannot confirm the behavior, state the
  uncertainty, choose conservative behavior, and avoid asserting or encoding a
  false guarantee or limitation.
- When citing sources in PRs, link directly to official docs and avoid indirect
  or derivative sources.
- If a third-party source is still useful for context, keep it secondary and add
  an explicit source justification near the link.

This requirement does not apply to trivial changes or internal-only refactors
that do not depend on external API semantics.

## Relationship to Playbook

- The AI workflow playbook builds on this baseline.
- Repo-local `AGENTS.md` adds repo-specific constraints.
