# Authoritative Source Check

## Purpose

Define the operational adoption guidance for the playbook's reusable advisory
source scanner. The durable source-authority policy remains in
[`engineering-baseline.md`](engineering-baseline.md#public-api-baselines).

## Reusable Advisory Check

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
Markdown file. The default scans changed Markdown files and the PR body. Use
`playbook_ref` when testing or pinning a non-`main` playbook ref.

## Official Domain Classification

Use the [canonical source policy](../scripts/authoritative_sources.json) for
built-in classifications. Add verified provider-controlled documentation at the
narrowest scope. An exact-host rule covers only the named host. An HTTPS
subtree rule covers its root and descendants on that host, at path-segment
boundaries. Use a subtree only for a verified first-party documentation area.
Subtree citations use the default HTTPS port and an unambiguous path without
embedded credentials.
Use exact URLs for individual pages on mixed hosts. Repository rules match the
configured host, owner, and repository. Configured project owners identify
project references. For each external API claim, verify that the cited
provider page supports it.

Caller `official_domains`, CLI `--official-domain`, and
`AUTHORITATIVE_SOURCE_OFFICIAL_DOMAINS` accept bare DNS domains separated by
commas or spaces. Each entry covers its host and its subdomains. The scanner
rejects URLs and paths in domain overrides.

## Source Justifications

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
distant blanket exceptions are not suppressions. A marker with multiple nearby
links is ambiguous and suppresses none of them; put each exception next to its
link with enough separation to identify its scope. Keep the source claim
conservative, prefer replacing the link with official docs when possible, and
leave the exception visible in the reviewed Markdown or PR body.

## Incremental Advisory Adoption

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

## Reusable Workflow Pinning

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
