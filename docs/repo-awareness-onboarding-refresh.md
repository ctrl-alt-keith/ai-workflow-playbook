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
document or artifact.

- GitHub organization state owns current organization membership and hosted
  repository state, including visibility, archived state, default branch,
  topics, description, settings, branch protection, security features,
  installed apps, and other hosted metadata.
- Workflow-owned inventories, such as enforcement scanner configs, automation
  allowlists, or caller-supplied manifests, own explicit scoped overrides,
  narrowed scan inputs, or reconciliation lists for workspace-scope checks.
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
  not duplicate volatile repository inventories; consuming workflows should own
  the inventories they need for execution.
- `ai-workflow-incubator` may stage operational checklists, examples, prompt
  drafts, and evidence. Incubator material is noncanonical until a separate
  promotion task moves a durable rule into the playbook.

### Organization membership and enumeration

For current membership in `ctrl-alt-keith`, GitHub organization state is the
authoritative provider source; the Playbook owns the reusable contract for
interpreting and consuming that state. A repository is a current member when
its current GitHub owner is the `ctrl-alt-keith` organization.

- A **member** includes every current organization repository, whether public,
  private, or archived. An **active member** is a member with `archived =
  false`.
- **Visibility** is hosted metadata, not a membership condition. Changing it
  does not add or remove a member.
- Use GitHub's stable numeric repository ID when correlation across a rename
  or transfer matters. `owner/name` is the current locator and can change.
- An organization enumeration is **complete** only when the caller can see all
  organization repositories and follows every result page. A result without
  that access or pagination evidence is partial or unknown: its absence cannot
  establish that a repository is not a member.

Policy overlays, workflow allowlists, role-oriented documentation, generated
dashboards, local checkout sets, and historical snapshots retain their own
narrow purposes. They may select, describe, or preserve information about
repositories, but do not define current organization membership or replace the
provider state that does.

## Discovery And Inventory Refresh

Repo discovery asks: "Which repositories should this workflow know about?"

Use it for:

- new repositories
- renamed repositories
- archived or deleted repositories
- visibility changes that affect public or private documentation, inventory,
  or automation scope
- repository role changes that affect workspace context, automation coverage,
  or enforcement scope

Discovery should reconcile, not guess:

1. Enumerate the relevant GitHub organization repositories or inspect the named
   repositories directly.
2. Treat live org state as the preferred authoritative inventory, then compare
   it with explicit workflow-owned inventories, such as enforcement scanner
   configs, automation allowlists, or caller-supplied manifests, when a scoped
   override or narrowed scan is intended.
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
- local automation coverage: active local automation configs, companion
  allowlists, scheduled validation targets, skip conditions, and whether each
  relevant surface should include the repository, intentionally exclude it, or
  require a human decision
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

## Manual Hosted Settings Change Gate

An authorized manual or org-admin change to a setting-sensitive hosted control
is incomplete until the operator retrieves the resulting hosted state and runs
a scoped governance audit against the affected repository. This is a mandatory
post-change gate, not automatic remediation and not authorization to make the
change. A successful audit verifies the resulting state; it does not supply the
approval that the mutation required.

Apply this gate when changing repository visibility, the default branch, branch
protection or rulesets, required pull requests or status checks, strict
up-to-date requirements, review counts or administrator bypass, force-push or
deletion controls, merge methods, auto-merge, delete-branch-on-merge, Actions
enablement where governed, or Dependabot settings where governed. Unrelated
repository changes do not trigger this procedure.

Use this order:

1. Before mutation, declare the target repository, intended setting change,
   operator or authorizing context when available, authoritative central-policy
   ref, target repository governance ref, and planned evidence names. Confirm
   that the operator is authorized to make the hosted change.
2. Perform only the authorized mutation, then retrieve the affected settings
   from the hosting provider again. Preserve that raw resulting-state response;
   do not treat the mutation request or its success response as proof of the
   resulting state.
3. Check out the `ai-workflow-enforcement` ref containing the authoritative
   central repository-settings policy and scanner, and resolve that ref to its
   commit SHA. Use an explicit, freshly resolved ref such as `origin/main`, not
   an unidentified working tree.
4. From that exact enforcement checkout, run the existing read-only scanner
   against the affected repository and its explicit governance source ref:

   ```console
   python3 -m enforcement.repo_settings_audit --repo <owner/repo> --source-ref main --output-format json --fail-on-drift --fail-on-error
   ```

   Add `--repo-root <path>` only when local-source comparison is also intended.
   Preserve the complete JSON stdout without filtering it and record the
   scanner's exit status. The scanner resolves the target governance ref before
   fetching its source files; use the `source_sha` reported by that run in the
   receipt rather than resolving a mutable ref again afterward.
5. Fail the completion gate if resulting-state retrieval is incomplete, the
   scanner exits nonzero, the hosted summary contains any drift or unknown
   result, or the report contains any error or incomplete coverage. Resolve the
   problem and repeat hosted-state retrieval and the scoped audit; do not waive
   or hide a finding in the completion receipt.

Append evidence by creating a new uniquely timestamped set under the existing
workspace `logs/repo-governance-audit/` directory. Do not replace or edit prior
evidence. Use names that keep the repository and run together, for example:

- `<UTC timestamp>-<repo>-post-change-hosted-state.json` for the raw resulting
  hosted-state retrieval
- `<UTC timestamp>-<repo>-post-change-audit.json` for the scanner's complete
  JSON output
- `<UTC timestamp>-<repo>-post-change-receipt.md` for the completion receipt

The receipt must identify the repository and mutation, operator or authority
context when supported, central-policy ref and resolved enforcement SHA, target
governance source ref and resolved source SHA, audit start and finish times,
hosted summary, scanner exit status, and the identities or paths of the raw
hosted-state and audit artifacts. Keep the full findings and errors in the raw
audit artifact and link it from the receipt. Link any earlier evidence that the
change supersedes or follows so the new receipt extends the history instead of
obscuring it.

## Propagation Targets

A repo-awareness refresh should inspect these target families and update only
the owning source when a change is needed:

- Playbook references: canonical docs and reusable prompts that describe
  inventory ownership without duplicating the current repository list.
- Incubator and bootstrap assumptions: staging checklists, bootstrap templates,
  examples, and evidence notes that need to mention the new workflow shape
  without becoming canonical policy.
- Automation allowlists and configuration: local Codex automations, enforcement
  configs, branch-cleanup coverage, drift-scan scope, scheduled validation
  targets, and org scanners. Inspect active local automation configuration and
  companion files; do not infer coverage from the filesystem or duplicate live
  allowlists in playbook prose.
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

For public repositories, verify that docs, descriptions, topics, examples,
workspace inventories, and validation notes do not leak local paths, private topology,
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
