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
- Canonical executable truth
  - Keep executable behavior in one authoritative tool, module, workflow, or
    validation entrypoint.
  - Orchestration may enumerate targets, invoke canonical commands, collect
    outputs, and summarize or report results.
  - Do not create wrapper scripts, aggregation scripts, secondary audit
    engines, parser forks, or validation-semantic copies that partially
    reimplement canonical tooling.
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

## Regression Fixture Fidelity

For deterministic extraction, parsing, normalization, or replay behavior, shift
from slow integration loops to fast regression-fixture iteration once the
failure shape is understood.

Trust that loop only after the fixture faithfully reproduces a known real
failure. Whenever practical, keep fail-before/pass-after evidence: the new
fixture should fail on the broken implementation and pass after the fix.

Treat fixture fidelity as suspect when the local fixture loop passes but
milestone or integration replay remains unchanged, integration validation shows
identical failure signatures, or "DORA-derived", "derived", or
"representative" fixtures were never proven against the actual failing shape.

Faithful fixtures do not guarantee execution-path equivalence. A
fail-before/pass-after fixture is necessary, but not always sufficient, when
the real system still behaves as if nothing changed.

If the fixture passes but integration behavior remains unchanged, stop adding
speculative fixtures or heuristics and treat the problem as possible
execution-path divergence. Compare the real integration path against the tested
layer before making another logic change. Check stage ordering, alternate code
paths, configuration skew, preprocessing differences, caching or state reuse,
runtime wiring, and artifact generation paths.

Run periodic integration validation to confirm the fixture loop is still
anchored to real behavior, not just a convenient local approximation.
Use integration validation to confirm path equivalence at milestones, not as
the repeated inner loop for every candidate fix.

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
and temporary-directory abstractions instead. When an example needs
attempt-local scratch, show the lifecycle pattern rather than a captured local
path, such as a fresh private `mktemp`-style directory or
`[attempt-local-directory]/artifact`.

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

This applies to local operational configuration such as Codex
`automation.toml` files when humans are expected to inspect, tune, or review
their prompts, schedules, or execution settings. Keep long prompt fields as
real multiline strings and prefer one setting per line over compact generated
serialization.

## Parallel Execution And Merge Ordering

For the full solo-operator decision model, worker envelope, reconciliation
sequence, and "when not to parallelize" guidance, use
[`orchestration-and-parallelism.md`](orchestration-and-parallelism.md). This
section records the engineering baseline that applies to any parallel batch.

Prefer parallel task execution when work can be cleanly separated by repository,
file area, or risk surface. Parallelism should improve throughput without
weakening reviewability, validation, or merge safety.

Before launching parallel work, classify each task by lane:

- independent capability
- governance
- isolated code path
- shared API/client behavior
- mutation/safety-critical path
- release/checking
- deferred consolidation

Do not parallelize changes that share mutation paths, release state, schema
contracts, or fragile overlapping files unless the dependency is explicit and a
clear merge order exists before work starts.

Independent capability lanes and governance lanes may run in parallel when they
are separated by file area, behavior surface, or risk surface. Consolidation or
reconciliation lanes that depend on outputs from other lanes should be gated,
not launched against moving branches.

For every parallel batch, define the intended merge order up front. If the work
is truly independent, say that merge order is flexible and why. When ordering
does matter, prefer the order that reduces conflict and review risk:

- governance before dependent docs
- reusable infrastructure before repo adoption
- shared client/API behavior before callers
- safety/mutation changes after dependent semantics are clear
- deferred consolidation after upstream PRs have merged

Start deferred consolidation lanes only after the upstream PRs are merged,
current `main` has been fetched, and the human explicitly confirms
continuation. These lanes should reconcile vocabulary, docs, contracts,
examples, or shared semantics from current `main` rather than chasing moving
branches.

This gating avoids semantic churn, avoidable rebases, and accidental behavior
changes during parallel implementation.

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
