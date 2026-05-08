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
  - Run ordinary repo commands directly from the target repository, following
    the command-form rules in `docs/repo-readiness.md`.
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

- one repository, one branch, one PR scope integrity
- repo-local `.worktrees/` isolation when worktrees are used
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
      official_domains: docs.example-provider.com
```

The reusable workflow checks out both the caller repository and
`ctrl-alt-keith/ai-workflow-playbook`, then runs the canonical
`scripts/check_authoritative_sources.py` scanner against the caller repository.
The check is advisory and emits warnings without blocking the pull request.
The scanner reports non-authoritative links only when they appear near public
API evidence terms such as API, SDK, CLI, endpoint, pagination, rate limits, or
retry behavior. This keeps normal repository links quiet while still surfacing
third-party sources used to support external API behavior claims.

Use `scan_mode: all` only when the caller intentionally wants to scan every
Markdown file instead of the pull request's changed Markdown files. Use
`official_domains` to add provider-controlled documentation domains that are
authoritative for the caller repository but not built into the scanner. Use
`playbook_ref` only when testing or pinning a non-`main` playbook ref.

### Official Domain Classification

Keep official-source classification narrow and explainable. Add documentation
domains that are controlled by the provider and are used for API references,
developer docs, SDK docs, official schemas, changelogs, release notes, or
product support docs that directly describe the behavior in question.

Do not add broad generic domains just because a vendor owns them. Avoid
allowlisting mixed surfaces such as blogs, communities, marketplaces, marketing
sites, support forums, or generic corporate roots when only a documentation
subdomain or developer portal is authoritative.

The scanner includes narrow Google and Atlassian documentation domains because
they are common adoption targets:

- Google: `cloud.google.com`, `developers.google.com`, and
  `firebase.google.com`.
- Atlassian: `developer.atlassian.com`, `docs.atlassian.com`, and
  `support.atlassian.com`.

These defaults do not imply that `google.com`, `atlassian.com`, `blog.google`,
`community.atlassian.com`, or other mixed/community domains are authoritative.
Caller repositories can still add more narrow `official_domains` when their
public API surface depends on another provider-controlled documentation domain.

Same-organization GitHub repository links are intentionally treated as project
references for this playbook's repositories. They are useful for local project
history, reusable workflow behavior, and issue or PR context owned by the same
organization. They are not a substitute for provider documentation when the
claim is about an external public API.

### Source Justifications

Suppressions must be visible, justified, and intentionally scoped. A
non-authoritative source may remain only when official docs are unavailable,
ambiguous, or insufficient for the specific edge case being discussed.

Use a nearby justification marker with a reason, such as:

```text
Source justification: official docs do not cover this API edge case; this link is investigation context only.
```

The scanner recognizes `Source justification:`, `Source exception:`,
`non-authoritative-source-ok:`, and `third-party-source-ok:` only when the
marker includes text after the colon and appears near the URL. Bare markers or
distant blanket exceptions are not suppressions. Keep the source claim
conservative, prefer replacing the link with official docs when possible, and
leave the exception visible in the reviewed Markdown or PR body.

### Incremental Advisory Adoption

Use the advisory check first in API-facing repositories where public API claims
are common and the repository already has a clear canonical validation path.
Google-facing and Atlassian-facing repositories are good candidates when their
docs, tests, or PR notes regularly cite vendor API behavior.

Adopt the check in this order:

1. Inventory the changed surfaces that make public API claims, such as docs,
   generated-client notes, schemas, examples, and PR descriptions.
2. Identify the narrow official vendor documentation domains needed for that
   repository's APIs. Prefer product API references, developer portals,
   official schemas, SDK docs, release notes, and changelogs controlled by the
   vendor.
3. Add the reusable workflow in `scan_mode: changed` with only those narrow
   `official_domains`. Keep it advisory and visible in PR checks.
4. Triage the first findings in ordinary PR review. Replace community, blog, or
   third-party links with official sources when official sources exist.
5. Use a nearby source justification only when official docs are unavailable,
   ambiguous, or insufficient for the specific edge case. Keep the claim
   conservative.
6. Expand to the next repository only after the current repository has a small,
   understandable finding pattern and no broad domain suppressions.

Keep rollout lightweight. Do not require every historical Markdown file to be
clean before adoption. Use `scan_mode: all` only for an explicit audit PR, not
as the default rollout posture. Do not make advisory warnings required merge
gates unless the caller repository explicitly documents that stricter local
policy.

False-positive mitigation should stay local and narrow:

- Prefer specific official documentation domains over broad corporate domains.
- Do not add broad allowlists for mixed domains that also host community,
  marketing, or blog content.
- Keep third-party investigation links separate from authoritative API claims,
  or add a nearby source justification when no official source exists.
- Avoid mixed source dumps where one community link appears to support many API
  claims.
- Fix wording when the scanner reveals an unsupported guarantee rather than
  suppressing the finding.

Implementation details remain in the reusable workflow and scanner. Caller
repositories should document only their chosen official documentation domains,
any repo-local advisory status, and any intentional exclusions from local
blocking validation.

### Reusable Workflow Pinning

Reusable workflows consumed by other repositories should be treated as
cross-repo dependencies. GitHub documents that reusable workflows can be
referenced by SHA, release tag, or branch, and that commit SHA references are
the safest option for stability and security:

- [Reusable workflow reference](https://docs.github.com/en/actions/reference/workflows-and-actions/reusable-workflows#behavior-of-reusable-workflows-when-re-running-jobs)
- [Secure use guidance](https://docs.github.com/en/actions/reference/security/secure-use#reusing-third-party-workflows)

Default stable callers to a release tag or full-length commit SHA instead of
`@main`. Use a full-length commit SHA for security-sensitive, release-blocking,
or otherwise behavior-sensitive checks. Use a release tag when readable version
intent and routine update ergonomics matter more than strict immutability, and
the workflow owner has a clear tag-publishing practice.

`@main` is acceptable only while the reusable workflow is actively iterating
with known downstream callers, while the workflow is unpublished or explicitly
experimental, or when the caller intentionally wants every default-branch change
immediately. Before treating the workflow as a stable shared contract, replace
`@main` with a tag or SHA and document the expected update path.

When rolling out updates, publish or choose the next workflow ref first, then
update downstream callers in scoped pull requests. Each downstream update should
state the old and new refs, run the caller repository's canonical validation and
CI path, and keep any required compatibility fixes in the same review surface.
For this playbook's advisory scanner, pin `playbook_ref` to the same tag or SHA
as the reusable workflow unless the caller is deliberately testing a split
workflow/scanner ref.

## Relationship to Playbook

- The AI workflow playbook builds on this baseline.
- Repo-local `AGENTS.md` adds repo-specific constraints.
