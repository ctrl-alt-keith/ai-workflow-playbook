# Repo Awareness And Onboarding Refresh

## Purpose

Use this procedure when repositories are added, removed, renamed, archived, or
meaningfully reclassified in the `ctrl-alt-keith` workspace. The goal is to
keep repository awareness current without turning every future prompt into a
bespoke inventory and governance exercise.

Future prompts can say:

```text
Run the repo-awareness and onboarding refresh for [repo names].
```

That prompt means two related but separate checks:

- repo discovery and inventory refresh
- repo onboarding and governance compliance

Keep the distinction visible in reports, issues, pull requests, and follow-up
lists.

## Source Boundaries

Repository awareness is layered. Do not collapse these sources into one
document or one generated artifact.

- GitHub organization state owns whether a repository exists, its visibility,
  archived state, default branch, topics, description, settings, branch
  protection, security features, installed apps, and other hosted metadata.
- Maintained workspace manifests, such as `config/workspace-repos.txt`, own
  the explicit repository set used by generated playbook context artifacts.
- Repo-local files own repository execution truth: `AGENTS.md`, `README.md`,
  Makefile targets, CI workflow files, CODEOWNERS, dependency config, tests,
  and docs.
- Automation configuration owns active schedules, runtime prompts, execution
  paths, allowlists, and skip conditions for recurring jobs.
- Org-admin settings own controls that cannot be changed safely or completely
  from repository files, such as branch protection rules, required status check
  registration, repository visibility, secret scanning, push protection,
  Dependabot enablement, and app permissions.
- The playbook owns reusable procedure and source-of-truth layering. It should
  not duplicate volatile repository inventories except where a maintained
  manifest or reference inventory is already intentionally part of the repo.
- `ai-workflow-incubator` may stage operational checklists, examples, prompt
  drafts, and evidence. Incubator material is noncanonical until a separate
  promotion task moves a durable rule into the playbook.

## Discovery And Inventory Refresh

Repo discovery asks: "Which repositories should this workflow know about?"

Use it for:

- new repositories
- renamed repositories
- archived or deleted repositories
- visibility changes that affect generated public or private artifacts
- repository role changes that affect workspace context, automation coverage,
  or enforcement scope

Discovery should reconcile, not guess:

1. Enumerate the relevant GitHub organization repositories or inspect the named
   repositories directly.
2. Compare live org state with explicit workspace manifests that intentionally
   feed generated context, such as `config/workspace-repos.txt`.
3. Compare local checkout state only after the explicit sources are known. Do
   not treat the filesystem as authoritative workspace scope.
4. Classify each repository as included, intentionally excluded, inaccessible,
   archived, local-only, or needing human decision.
5. Update only the maintained inventory sources that are supposed to know about
   the repository.

Avoid hard-coded repo lists in canonical prose. When an inventory must be
maintained, keep it in the owning manifest, runtime config, or reference
inventory and identify that owner explicitly.

## Onboarding And Governance Compliance

Onboarding asks: "Is each repository ready to participate safely in the
workspace?"

Run onboarding and governance checks for newly visible repositories and for
repositories whose role, visibility, risk level, automation coverage, or default
branch protection expectations changed.

Check at least these surfaces:

- repo-local startup and readiness: `AGENTS.md`, README orientation,
  repo-local `docs/start-here.md` when used, `make check`, `make help` when the
  Makefile has multiple useful targets, validation documentation, and local
  workflow artifact hygiene
- branch and review controls: default branch, pull-request flow, branch
  protection expectations, required review posture, direct-push restrictions,
  auto-merge policy, and whether ready-for-review PR defaults still make sense
- required CI and status checks: hosted checks that should be required, checks
  that are intentionally advisory, and checks that remain local-only
- ownership and review routing: CODEOWNERS expectations, responsible maintainers
  or teams, and repo-local escalation notes where applicable
- Actions and automation policy: default token permissions, workflow write
  permissions, third-party action review or pinning expectations, automation
  schedules, automation allowlists, and skip conditions
- security posture: visibility, secret scanning, push protection, dependency
  alerts, Dependabot or equivalent dependency-update automation, private
  vulnerability reporting, security advisories, and repository secret scope
- metadata: repository description, topics, homepage/profile links, archived
  state, default branch, and public/private/internal visibility
- enforcement integration: advisory scanner coverage, drift config, reusable
  workflow adoption, org scan inclusion, and intentionally excluded surfaces

When a setting cannot be represented in repo files or changed from the current
execution context, record it as a manual or org-admin follow-up. Do not pretend a
docs PR enforced a hosted setting.

## Propagation Targets

A repo-awareness refresh should inspect these target families and update only
the owning source when a change is needed:

- Playbook references: canonical docs, reusable prompts, generated-context
  source manifests, and reference inventories that intentionally summarize
  current automation scope.
- Incubator and bootstrap assumptions: staging checklists, bootstrap templates,
  examples, and evidence notes that need to mention the new workflow shape
  without becoming canonical policy.
- Automation allowlists and configuration: local Codex automations, enforcement
  configs, branch-cleanup coverage, drift-scan scope, scheduled validation
  targets, and org scanners.
- Org-level metadata and settings: repository visibility, description, topics,
  default branch, branch protection, required status checks, Actions policy,
  auto-merge policy, security features, Dependabot, installed apps, and access.
- Enforcement surfaces: advisory checks, reusable workflows, CODEOWNERS
  expectations, scanner configuration, CI workflows, and report-only audit
  scope.
- Repo-local readiness: `AGENTS.md`, README, Makefile, validation commands,
  docs, CI files, dependency metadata, and local security posture notes.

## Public And Private Handling

Public-safe artifacts must not expose private repository details unless the
owning artifact is explicitly private and intended to carry that detail. Prefer
role-based language in canonical docs. Use concrete private repository names
only when operational paths, examples, provenance, or ecosystem topology need
them and the artifact's visibility supports that disclosure.

For public repositories, verify that docs, generated artifacts, descriptions,
topics, examples, and validation notes do not leak local paths, private topology,
credentials, account identifiers, private hostnames, or sensitive operational
context.

For private repositories, still keep durable guidance portable and reviewable.
Private visibility is not permission to mix source-of-truth layers or commit
secrets.

## Completion Report

Report completion by lane:

- discovery and inventory changes made
- onboarding and governance checks completed
- repo-local changes and pull requests opened
- automation or enforcement changes and pull requests opened
- manual or org-admin follow-ups that remain outside repo-local enforcement
- validation performed, usually `make check` in each changed repository
- inaccessible repositories, blocked settings, or intentionally excluded scope

If no change is needed for a target, say why. If a repository is intentionally
excluded from a manifest, automation, or enforcement surface, record that as an
explicit decision rather than leaving it indistinguishable from an omission.
