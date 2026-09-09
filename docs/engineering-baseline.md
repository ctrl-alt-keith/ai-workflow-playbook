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
  - Tests presented as implementation coverage must exercise repository-owned
    executable behavior or externally meaningful interfaces. A helper, model,
    validator, workflow, or protocol implementation that exists only in the
    test suite is scaffolding, not evidence that repository implementation
    semantics are covered.
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

- Follow [PR Readiness](repo-readiness.md#pr-readiness) for pull-request
  mechanics.
- Keep commits clean and focused.

## Test Value

Keep tests that materially protect consequential behavior, compatibility,
safety or mutation boundaries, provider or identity evidence, security
properties, machine-consumed contracts, or demonstrated regressions. Do not
add or preserve tests merely to exercise every function, maintain a coverage
percentage, freeze implementation topology, preserve presentation output, or
assert the absence of hypothetical future capabilities. Loss of test coverage
is not itself a regression.

Prefer the smallest representative set of tests for each meaningful invariant;
retain multiple fixtures or scenarios only for materially distinct failure
modes. When removing a test, do not replace it unless the underlying behavior
independently warrants permanent regression coverage. Historical regression
tests may be removed when the failure is no longer plausible, the architecture
removed the failure mode, or another test now protects the same invariant.

## Regression Fixture Fidelity

For deterministic extraction, parsing, normalization, or replay, shift to fast
regression-fixture iteration once the failure shape is understood. Trust it
only after fixtures faithfully reproduce a known real failure; retain
fail-before/pass-after evidence whenever practical. Treat unproven "derived" or
"representative" fixtures, unchanged integration replay, or identical
integration failure signatures despite fixture success as fidelity warnings.

If fixtures pass but integration behavior is unchanged, stop speculative
fixtures or heuristics and compare the real execution path with the tested
layer before another logic change. Check stage order, alternate paths,
configuration, preprocessing, caching/state reuse, runtime wiring, and artifact
generation. Fail-before/pass-after evidence is necessary but may be insufficient
in this case. Validate integration periodically and at milestones to confirm
path equivalence, not for every candidate fix.

## Documentation Validation

Validate documentation structure, links, schemas, machine-consumed contracts,
or executable behavior where applicable. Do not add tests that assert
incidental wording, sentences, headings, explanatory prose, or equivalent
text-presence checks. Exact-text assertions are appropriate only when the exact
bytes or tokens are themselves a machine-consumed contract or externally
required interface.

## Agent-Read Documentation

Classify sections by primary use, including in mixed documents: agent-read
directs agent execution; human-facing supports human understanding, review, or
decisions.

Retain agent-read documentation and prompt content only if it can change agent
action, decision, authority interpretation, safety/evidence boundaries,
validation obligations, or stop/failure behavior, or another canonical contract
explicitly requires it. Preserve consequential contract semantics, including
precedence, identity, and source ownership.

Use the smallest unambiguous normative representation; human narrative flow is
secondary. Prefer [canonical-owner references](start-here.md#canonical-ownership)
over copied doctrine while keeping required activation and source access
available to the consuming agent.

Omit rationale, design history, unused implementation mechanics, explanatory
restatement, defensive narration, and redundant scenario permutations; keep
examples/cases only for materially distinct behavior not already clear from the
rule. Put human rationale, history, and change explanations on human-facing
surfaces. Add no taxonomy, scoring, checklist, or ceremony.

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
path, such as a fresh private directory allocated only through its platform's
qualified route or
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

Start deferred consolidation lanes only after upstream PRs merge and the human
explicitly confirms continuation. Apply
[PR Readiness](repo-readiness.md#pr-readiness) before reconciliation.

If two PRs overlap unexpectedly, pause and re-establish the order before merging:

- apply [PR Readiness](repo-readiness.md#pr-readiness) to affected PRs
- inspect the PR surfaces directly
- do not merge based only on local cleanliness

Parallelism must not weaken:

- one repository, one branch, one worktree, one PR scope integrity
- required repo-local `.worktrees/` isolation for implementation changes
- canonical validation
- direct PR inspection
- authoritative source requirements

## Public API Baselines

Before changing code, tests, docs, risks, or user-facing claims dependent on
external behavior, establish current behavior from official sources. This
includes public/SaaS/cloud/GitHub APIs, SDKs, CLIs, package managers, and other
external systems; it excludes trivial changes or internal-only refactors that
do not depend on external API semantics.

Use authoritative docs as primary evidence: controlled by the responsible
provider or standards body and specific enough to support the claim, such as
API references, schemas, SDK docs, or release notes.
Corporate home pages, marketing, blogs, forums, community answers,
issue comments, third-party tutorials, AI output, and search snippets are not
authoritative. Neither these nor memory, stale knowledge, or inference may
substitute for available authoritative docs. In PRs, link directly to official
docs; justify any secondary third-party context beside its link.

Verify relevant lifecycle/status, location availability, pagination, limits,
retries, auth/token errors, deletion/idempotency, consistency/timing, and
SDK/CLI behavior. If official docs are ambiguous or cannot confirm behavior,
state uncertainty, choose conservative behavior, and avoid false guarantees or
limitations.

### External Dependency Boundaries

For external providers, specs, CLIs, SDKs, or hosted platforms, distinguish
officially documented guarantees, observations, and local assumptions in code
comments, docs, tests, risks, and PR notes. Record the checked date when behavior
is operationally important, time-sensitive, or likely to change. Prefer
conservative workflows when docs are incomplete, ambiguous, or silent; never
encode unverified assumptions as architecture, public guarantees, or destructive
defaults.

Keep credentials in the environment or approved secret stores, and
account-specific state, private topology, and local paths out of reusable docs.
Provider-specific semantics belong in the consuming repository with direct
official sources; the Playbook owns verification posture.

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
