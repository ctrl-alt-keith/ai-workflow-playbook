# Engineering Baseline

## Purpose

Define shared engineering expectations across repositories. This baseline forms the foundation for workflow rules in this playbook.

## Core Principles

- Small, scoped changes
  - One PR = one reason.
- Validate before PR
  - Use the repository's canonical validation command, such as `make check`.
  - Do not add or substitute alternate local validation tools outside the
    repo-defined workflow.
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

## Parallel Execution And Merge Ordering

Prefer parallel task execution when work can be cleanly separated by repository,
file area, or risk surface. Parallelism should improve throughput without
weakening reviewability, validation, or merge safety.

Before launching parallel work, classify each task by lane:

- docs/governance
- isolated code path
- shared API/client behavior
- mutation/safety-critical path
- release/checking

Do not parallelize changes that share mutation paths, release state, schema
contracts, or fragile overlapping files unless the dependency is explicit and a
clear merge order exists before work starts.

For every parallel batch, define the intended merge order up front. If the work
is truly independent, say that merge order is flexible and why. When ordering
does matter, prefer the order that reduces conflict and review risk:

- docs/governance before dependent docs
- reusable infrastructure before repo adoption
- shared client/API behavior before callers
- safety/mutation changes after dependent semantics are clear

If two PRs overlap unexpectedly, pause and re-establish the order before merging:

- rebase or update branches in the intended order
- rerun canonical validation after each update
- inspect the PR surfaces directly
- do not merge based only on local cleanliness

Parallelism must not weaken:

- one repository, one branch, one PR scope integrity
- workspace or worktree isolation
- canonical validation
- direct PR inspection
- authoritative source requirements

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

### Reusable Advisory Check

Repositories can call the canonical advisory scanner from this playbook instead
of copying scanner logic. Add a local workflow that calls the reusable workflow:

```yaml
name: Authoritative Source Check

on:
  pull_request:

permissions:
  contents: read

jobs:
  authoritative-source-check:
    uses: ctrl-alt-keith/ai-workflow-playbook/.github/workflows/authoritative-source-check.yml@main
    with:
      scan_mode: changed
```

The reusable workflow checks out both the caller repository and
`ctrl-alt-keith/ai-workflow-playbook`, then runs the canonical
`scripts/check_authoritative_sources.py` scanner against the caller repository.
The check is advisory and emits warnings without blocking the pull request.

Use `scan_mode: all` only when the caller intentionally wants to scan every
Markdown file instead of the pull request's changed Markdown files. Use
`playbook_ref` only when testing or pinning a non-`main` playbook ref.

## Relationship to Playbook

- The AI workflow playbook builds on this baseline.
- Repo-local `AGENTS.md` adds repo-specific constraints.
