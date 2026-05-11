# Engineering Baseline

## Purpose

Define shared engineering expectations across repositories. This baseline forms the foundation for workflow rules in this playbook.

## Core Principles

- Small, scoped changes
  - One PR = one reason.
- Validate before PR
  - Use the repository's canonical validation command, such as `make check`.
  - Run available canonical local validation before opening or updating a PR;
    do not treat CI as a substitute for that local step.
  - Do not add or substitute alternate local validation tools outside the
    repo-defined workflow.
- Command intent stays visible
  - Run ordinary repo commands directly from the target repository worktree,
    following the command-form rules in `docs/repo-readiness.md`.
- Repository isolation
  - One repository per PR.
  - One dedicated worktree per implementation change.
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

- Fetch current `origin/main` at task start and anchor implementation to that
  fetched baseline.
- Before opening or updating a PR, verify current mergeability against `main`.
- Update or rebase only for conflicts, overlapping upstream changes, repo
  policy, or explicit human request.
- Rerun canonical validation after any update or rebase.
- Keep commits clean and focused.
- PRs are ready for review by default.

## Config And CLI Default Changes

When extending config/default precedence or CLI override logic, identify every
parallel structure that describes the field before editing: allowlists,
candidate/default maps, source labels, option-name maps, redaction lists, and
error-message paths. Update them together or replace the parallel structure with
one source of truth when that is locally simple.

For each new config-validation CLI override, add focused tests for both accepted
and rejected command paths:

- a supported command accepts the override and reports the expected source,
- an unsupported command fails cleanly with the option name in the parser or
  validation error,
- raw implementation exceptions, such as missing-map `KeyError`s, do not leak
  through.

When commands have command-specific allowed fields, test at least one supported
and one unsupported command for each new override.

## Licensing Baseline

- Use Apache License 2.0 as the default license for public repositories unless
  the repository has an explicit reason to choose another license.
- Public repositories must include a root `LICENSE` file before normal delivery
  work begins.
- Keep licensing guidance simple and reusable; put repository-specific
  exceptions in the repository's own setup notes.

## Public Artifact Path Hygiene

Public-facing workflow artifacts should avoid machine-local absolute filesystem
paths. This includes public docs, reusable examples, manifests, validation
notes, PR evidence, and reusable workflow guidance.

Prefer relative paths, repo-root placeholders, lint-safe example placeholders,
and temporary-directory abstractions instead. When an example needs a scratch
location, show the pattern rather than a captured local path, such as a
`mktemp`-style temporary directory or `[temporary-directory]/artifact`.

Machine-local paths reduce portability and can leak unnecessary local context
into public artifacts. Keep path examples reusable unless the artifact is
explicitly private, local-only, and not intended for publication.

## Human-Maintained TOML Readability

Valid TOML is the baseline requirement. When TOML files are intended for human
editing or review, prefer multiline strings, arrays, and tables that keep the
operational intent inspectable in diffs and review surfaces.

Avoid long escaped single-line blobs with embedded `\n` sequences in
human-maintained configuration. Compact serialized TOML is usually appropriate
for intentionally machine-generated artifacts or local runtime state where
round-trip serialization is more important than review readability.

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

- one repository, one branch, one worktree, one PR scope integrity
- required repo-local `.worktrees/` isolation for implementation changes
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
- Treat a source as authoritative only when it is controlled by the provider or
  standards body responsible for the behavior and is specific enough to support
  the claim being made. Product API references, developer portals, schema
  definitions, SDK docs, and provider release notes are good evidence.
- Do not treat generic corporate home pages, marketing pages, blogs, forums,
  community answers, issue comments, StackOverflow answers, third-party
  tutorials, AI-generated content, or search-result snippets as authoritative
  evidence for public API behavior.
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

### External Dependency Boundaries

For repositories that depend on external providers, specs, CLIs, SDKs, or
hosted platforms, keep the boundary between documented behavior and local
assumption visible. This boundary is part of the repository's safety posture,
not just a citation habit:

- Treat official provider or specification docs as authoritative for behavior
  claims.
- Distinguish documented guarantees from observed behavior in code comments,
  docs, tests, risks, and PR notes.
- Record the checked date when the behavior is operationally important,
  time-sensitive, or likely to change.
- Prefer conservative workflows when docs are incomplete, ambiguous, or silent.
- Do not turn unverified assumptions into architecture, public guarantees, or
  destructive default behavior.
- Keep credentials in the environment or approved secret stores; do not encode
  account-specific state, private topology, or local paths into reusable docs.

Provider-specific API semantics belong in the repository that uses that
provider, backed by direct official sources. The playbook should define the
verification posture, not repeat external documentation.

## Advisory Source Check Operations

The durable policy is the public API baseline above: use authoritative,
provider-controlled sources for external behavior claims and keep assumptions
visible. Operational details for the reusable advisory scanner, official-domain
classification, source justifications, rollout order, and reusable workflow
pinning live in
[`authoritative-source-check.md`](authoritative-source-check.md).

## Relationship to Playbook

- The AI workflow playbook builds on this baseline.
- Repo-local `AGENTS.md` adds repo-specific constraints.
