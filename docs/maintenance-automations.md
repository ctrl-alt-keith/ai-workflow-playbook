# Maintenance Automations

Codex maintenance automations are part of the orchestration model: they keep
recurring checks visible, bounded, and reviewable without turning the playbook
into an automation implementation repo.

This document owns reusable policy, canonical prompt intent, and governance
expectations for maintenance automation. It does not own executable automation
state. Active local automation configuration under
`~/.codex/automations/*/automation.toml`, plus companion config files
referenced by those automations, remains the discovery and inspection source
for live automation state, current prompt/config content, schedules,
enablement, execution paths, and operator-controlled runtime fields.

## Automation Intent Registry

The registry below records intended prompt semantics and drift-handling
expectations for known maintenance automations. Refresh registry entries from
inspected active local automation config; do not maintain disconnected
handwritten rows that have not been compared with live `automation.toml` files
and referenced companion configs.

Registry entries are canonical only for intended semantics, governance
expectations, and reconciliation guidance. They are normalized summaries
derived from inspected local config, not raw TOML mirrors. They are not
executable automation state and must not be treated as proof that an
automation exists, is enabled, uses a particular schedule, or currently
contains a matching prompt.

### 🧹 Delete Merged Repo Branches

- Automation name: 🧹 Delete merged repo branches
- Automation ID: `delete-merged-repo-branches`
- Scope / target repositories: `knowledge-adapters`, `knowledge-vault`,
  `ka-destinations`, `ai-workflow-playbook`, `ai-workflow-enforcement`,
  `ai-workflow-incubator`, `linode-image-lab`, `linode-backup-lab`, `nexus`,
  and `.github`.
- Mode: Mutating only through the owning tool's explicit `--apply` path for
  Git-proven normal cleanup. Stale non-ancestor cleanup remains report-only
  unless explicit human-approved evidence exists in the companion config and
  the owning tool validates it.
- Purpose / intent: Keep local and remote branch refs tidy by delegating
  cleanup decisions to `enforcement.branch_cleanup`, while reporting preserved,
  blocked, failed, and stale refs.
- Canonical prompt intent summary: Read the playbook startup guidance,
  maintenance automation guidance, and branch-cleanup tool guidance before
  running. Use only configured target repositories. Treat the enforcement tool
  output as authoritative for cleanup classifications and never recreate branch
  cleanup or stale-validation policy in prompt text.
- Canonical execution expectations: Use direct Git and Python commands from
  the `ai-workflow-enforcement` checkout. Refresh the enforcement checkout and
  configured target repositories only through the safe local refresh rule
  below. Run bounded normal cleanup with
  `python3 -m enforcement.branch_cleanup --config <branch-cleanup-config> --apply --retry-normal-cleanup --max-apply-passes 3`,
  then run stale/non-ancestor audit with
  `python3 -m enforcement.branch_cleanup --config <branch-cleanup-config> --audit-stale --audit-github-prs`.
  Report deleted, preserved, skipped, blocked, failed, stale-candidate, and
  human-review refs from tool output.
- Companion config references:
  `~/.codex/automations/delete-merged-repo-branches/branch-cleanup.json`
  owns target repositories, protected branches, and stale approval evidence.
  `ai-workflow-enforcement/docs/branch-cleanup.md` owns tool behavior.
- Reconciliation / drift handling: Freshly inspect the active `automation.toml`
  and companion config before comparison. The inspected live prompt contains
  older prompt-content drift around branch switching and `merge --ff-only`
  fallback refresh behavior; reconcile that prompt content to the safe local
  refresh rule below only when explicitly directed. Do not copy stale approval
  entries, runtime state, or raw config into the playbook.

### 🧠 Staging Vs Canon Audit

- Automation name: 🧠 Staging vs Canon Audit
- Automation ID: `staging-vs-canon-audit`
- Scope / target repositories: The `ctrl-alt-keith` workspace guidance layer,
  including `ai-workflow-playbook`, repo-local `AGENTS.md` files,
  `ai-workflow-incubator` staging/reference material, and local workspace
  routing guidance.
- Mode: Report-only read-only audit.
- Purpose / intent: Detect documentation drift, accidental authority,
  shadow-canonical guidance, stale staging material, and repo-level
  duplication of canonical workflow rules.
- Canonical prompt intent summary: Treat `ai-workflow-playbook` as canonical
  reusable guidance, repo-local `AGENTS.md` files as repository execution
  layers, and `ai-workflow-incubator` as private noncanonical staging. Audit
  only inside the workspace boundary and treat sibling repositories as
  independent units.
- Canonical execution expectations: Stay read-only. Do not fetch, pull,
  checkout, merge, rebase, reset, or modify refs. Ignore generated,
  dependency, cache, virtualenv, and tool-managed paths. Classify findings as
  remove, trim, keep, defer, or promotion candidate, and report repository
  freshness only as context when it can be checked without mutation.
- Companion config references: None.
- Reconciliation / drift handling: Freshly inspect the active `automation.toml`
  before comparison. Prompt drift includes any change that makes staging
  material canonical, mixes repository findings as one shared working tree, or
  permits repository, automation, or workspace mutation.

### 🔍 AGENTS Drift Detector

- Automation name: 🔍 AGENTS Drift Detector
- Automation ID: `agents-drift-detector`
- Scope / target repositories: `ai-workflow-playbook`,
  `ai-workflow-enforcement`, `ai-workflow-incubator`, `knowledge-adapters`,
  `knowledge-vault`, `ka-destinations`, `linode-image-lab`,
  `linode-backup-lab`, `nexus`, and `.github`, plus the local-only workspace
  `AGENTS.md`.
- Mode: Report-only audit.
- Purpose / intent: Audit repo-local `AGENTS.md` guidance and local
  workspace-routing guidance against the canonical playbook.
- Canonical prompt intent summary: Treat `ai-workflow-playbook` as canonical
  reusable workflow guidance, each repo-local `AGENTS.md` as the repository
  execution layer, the workspace `AGENTS.md` as local-only routing guidance,
  and `ai-workflow-incubator` as private noncanonical staging.
- Canonical execution expectations: For each repository, fetch `origin main`
  and inspect current `origin/main` state without modifying files or branches.
  Mark repositories blocked when `origin/main` cannot be fetched or inspected.
  Inspect the local workspace `AGENTS.md` as local-only guidance. Compare
  repo-local guidance against the playbook and relevant workspace-routing
  guidance; report High/Medium findings separately from Low-only observations.
- Companion config references: None.
- Reconciliation / drift handling: Freshly inspect the active `automation.toml`
  before comparison. Prompt drift includes treating the workspace `AGENTS.md`
  as canonical repository policy, auditing local working trees instead of
  fetched `origin/main`, inventing missing repo details, or allowing mutation.

### 🛡️ Workflow Drift Audit

- Automation name: 🛡️ Workflow Drift Audit
- Automation ID: `workflow-drift-audit`
- Scope / target repositories: The `ctrl-alt-keith` workspace guidance and
  workflow-policy surfaces covered by the enforcement drift scanner config:
  `ai-workflow-incubator` notes roots, `ai-workflow-playbook/docs`, the
  workspace manifest, and the configured organization repositories `.github`,
  `ai-workflow-incubator`, `ai-workflow-playbook`,
  `ai-workflow-enforcement`, `linode-image-lab`, `linode-backup-lab`,
  `knowledge-adapters`, `knowledge-vault`, `ka-destinations`, and `nexus`.
- Mode: Report-only advisory scan.
- Purpose / intent: Invoke the calibrated `ai-workflow-enforcement` drift
  scanner directly and report workflow-policy drift findings.
- Canonical prompt intent summary: Treat the scanner as advisory, local
  automation config as runtime state, and generated reports as local-only.
  Do not auto-fix findings or duplicate scanner semantics in prompt text.
- Canonical execution expectations: Work from the `ai-workflow-enforcement`
  checkout. Verify the scanner config exists, inspect git status, skip if the
  working tree would make results ambiguous, record the tested commit SHA, and
  run `python3 -m enforcement.cli --config examples/drift-scan.json`.
  Do not fetch, pull, switch branches, commit, open PRs, modify files, delete
  worktrees, or delete branches.
- Companion config references: `ai-workflow-enforcement/examples/drift-scan.json`
  owns scanner roots, repository coverage, ignored paths, and scanner
  calibration thresholds.
- Reconciliation / drift handling: Freshly inspect the active `automation.toml`
  and scanner config before comparison. Prompt drift includes mutating
  repositories, treating advisory scanner findings as failures, changing
  scanner scope in prompt text instead of the companion config, or creating a
  secondary drift scanner.

### 🛡️ Repo Governance Audit

- Automation name: 🛡️ Repo Governance Audit
- Automation ID: `repo-governance-audit`
- Scope / target repositories: All visible repositories in the
  `ctrl-alt-keith` GitHub organization, discovered dynamically at runtime.
- Mode: Report-only advisory scan.
- Purpose / intent: Invoke the centralized `ai-workflow-enforcement`
  repository settings audit directly across visible organization repositories
  and report hosted governance drift.
- Canonical prompt intent summary: Use the merged `main` state of
  `ai-workflow-enforcement` as the audit implementation source. Enumerate
  repositories with `gh`; do not use a hard-coded allowlist as the source of
  repository scope. Report drift, unknowns, stale local/source-ref drift, and
  audit/runtime failures without remediation.
- Canonical execution expectations: Inspect the enforcement checkout, update
  local `main` only through safe local refresh, confirm it matches
  `origin/main`, record the tested commit SHA, verify `gh` organization
  access, and run
  `python3 -m enforcement.repo_settings_audit --repo ctrl-alt-keith/<repo> --source-ref main --output-format json`
  for each visible repository. Do not pass `--fail-on-drift`, mutate hosted
  settings, commit, push, open PRs, delete branches, delete worktrees, or edit
  automation config.
- Companion config references: None.
- Reconciliation / drift handling: Freshly inspect the active `automation.toml`
  before comparison. Prompt drift includes hard-coded repository scope,
  hosted remediation, failure-on-drift behavior, stale local source ambiguity,
  or unsafe local refresh semantics.

### 🔎 Org PR And Issue Scan

- Automation name: 🔎 Org PR and Issue Scan
- Automation ID: `org-pr-issue-scan`
- Scope / target repositories: All visible repositories in the
  `ctrl-alt-keith` GitHub organization, discovered by the owning enforcement
  scanner.
- Mode: Report-only inventory scan.
- Purpose / intent: Report current open pull requests and open issues across
  visible organization repositories.
- Canonical prompt intent summary: Use the owning `ai-workflow-enforcement`
  scanner directly, keep generated reports local-only, and treat the result as
  inventory rather than remediation.
- Canonical execution expectations: Work from the `ai-workflow-enforcement`
  checkout. Inspect git status, skip if the working tree would make results
  ambiguous, record the tested commit SHA, verify `gh` organization access,
  and run `python3 -m enforcement.org_pr_issue_scan --org ctrl-alt-keith`.
  Do not fetch, pull, switch branches, commit, open PRs, modify files, delete
  worktrees, delete branches, or create, edit, close, label, assign, or comment
  on GitHub issues or pull requests.
- Companion config references: None.
- Reconciliation / drift handling: Freshly inspect the active `automation.toml`
  before comparison. Prompt drift includes recreating scanner behavior in
  prompt text, mutating GitHub issues or pull requests, omitting skipped or
  inaccessible repositories, or treating inventory as remediation.

### 🧪 Knowledge-Adapters Weekly Chaos-All Validation

- Automation name: 🧪 knowledge-adapters weekly chaos-all validation
- Automation ID: `knowledge-adapters-weekly-chaos-all-validation`
- Scope / target repositories: `knowledge-adapters`.
- Mode: Report-only scheduled validation.
- Purpose / intent: Run exhaustive validation for `knowledge-adapters` and
  report the result.
- Canonical prompt intent summary: Refresh the target repository from current
  `origin/main` only when safe, run the canonical exhaustive validation command,
  report the tested commit SHA, and summarize failures with the smallest useful
  follow-up when validation fails.
- Canonical execution expectations: Use the safe local refresh rule below.
  Run `make chaos-all`. Do not modify files, open PRs, or run live-service or
  credential-dependent checks.
- Companion config references: None.
- Reconciliation / drift handling: Freshly inspect the active `automation.toml`
  before comparison. Prompt drift includes underspecified or unsafe refresh
  behavior, mutation, PR creation, live-service checks, or replacing
  `make chaos-all` with a narrower validation command.

### 🗜️ Compact Memory

- Automation name: 🗜️ Compact Memory
- Automation ID: `compact-memory`
- Scope / target repositories: Active Codex automation memory files matching
  `~/.codex/automations/*/memory.md`.
- Mode: Report-only proposal.
- Purpose / intent: Identify oversized automation memory files and propose
  compact replacements that preserve durable operational state.
- Canonical prompt intent summary: Treat 25 KiB as the default oversized
  threshold. Preserve automation purpose, durable decisions, active risks,
  unresolved TODOs or blockers, and recent operational state while reducing
  repetitive historical run detail.
- Canonical execution expectations: Inspect active `memory.md` files only.
  Do not mutate memory files, automation configs, repositories, branches, or
  working trees. Do not create archive copies or `memory.*.md` siblings under
  `~/.codex/automations/*/`. Do not introduce scripts, enforcement tools, or
  automatic rewriters. If preservation is explicitly requested for a rewrite,
  use an archive location outside active automation directories.
- Companion config references: None. Active `memory.md` files are inspected
  data for the report, not repository-owned companion config.
- Reconciliation / drift handling: Freshly inspect the active `automation.toml`
  before comparison. Prompt drift includes automatic memory mutation,
  repository mutation, archive sibling creation inside active automation
  directories, or discarding durable state.

## Guidance Layers

- Follow the authority boundary in
  [`start-here.md`](start-here.md#source-authority-map).
- Live local automation configuration is authoritative for discovered
  automation inventory, current runtime prompt/config state, schedules,
  enablement state, execution environment, model selection, runtime IDs,
  local environment config paths, and platform-managed state.
- This playbook is authoritative for intended semantics, governance
  expectations, source-first inspection requirements, safe refresh rules,
  drift review expectations, and canonical prompt intent.
- Workspace-level routing guidance may live in a local-only workspace
  `AGENTS.md`. It can describe multi-repository boundaries, scratch usage,
  command form, and how to enter target repositories, but it is noncanonical
  and must not define repository branch, commit, PR, or validation policy.
- Repo-local execution guidance belongs in each repository's `AGENTS.md`; see
  [`repo-readiness.md`](repo-readiness.md#agentsmd-responsibilities).
- Drift review should compare repo-local `AGENTS.md` files against the playbook
  and any relevant workspace-routing guidance, while comparing workspace-level
  routing guidance against reusable playbook expectations and observed
  repo-local execution patterns. Do not require the workspace file to duplicate
  repo-only rules.

## Prompt Drift Review

Automation prompt/config alignment is a source-first workflow:

1. Inspect active local automation config first:
   `~/.codex/automations/*/automation.toml` and companion config files
   referenced by those automations.
2. Compare the live prompt/config semantics against this registry's canonical
   intended semantics and the operating rules below.
3. Classify semantic drift separately from runtime/operator state. Prompt
   content that changes the intended behavior, safety predicates, authority
   boundaries, or skip conditions is semantic drift. Schedules, enablement,
   model choice, execution environment, timestamps, execution history,
   connector metadata, opaque platform IDs, and other runtime fields are not
   repository-doc drift.
4. Reconcile only intended prompt/content drift when explicitly directed.
   Preserve runtime and operator-controlled fields in the live automation
   platform/configuration unless the human explicitly asks to change that live
   state.

For repository changes, update this registry only with intent-oriented facts:
automation name, stable local ID when it is human meaningful, scope, mode,
purpose, expected prompt semantics, companion config references, and
drift-handling expectations. Do not copy raw `automation.toml` files, full
prompt dumps, schedules, enablement state, execution logs, timestamps,
connector metadata, secrets, tokens, runtime snapshots, opaque runtime IDs, or
platform-managed state into the repository.

## Operating Rules

- Name recurring automations by purpose so their intent is clear in schedules,
  reports, and follow-up.
- Automation prompts that touch repositories should state the interaction mode
  from [`repo-readiness.md`](repo-readiness.md#interaction-mode-preflight).
- Automation prompts intended for another agent or tool should be complete,
  self-contained, and ready to paste by default. If an automation prompt update
  asks to add or incorporate new guidance, provide the full updated prompt
  unless the human explicitly asks for a delta, patch, diff, or targeted edit.
- Report-only is the default for audits and validation checks.
- Mutating automations must be bounded, conservative, and skip on uncertainty.
- Automation prompts should delegate reusable safety predicates to owning tools
  when such tools exist, and should not duplicate full implementation logic in
  prompt text.
- When an authoritative module, CLI, reusable workflow, or Makefile target
  already exists, invoke it directly. Do not build secondary audit/check
  engines around it.
- Wrapper or helper artifacts must stay orchestration-only or report-only and
  non-authoritative. They may enumerate targets, call canonical commands, cache
  raw outputs, collate results, and summarize reports, but they must not fork
  parser behavior, reinterpret core semantics, or duplicate validation logic.
- Audit prompt/config alignment from the active local automation configuration
  files, not only from this registry. Use the registry to orient the review,
  then inspect the owning `automation.toml` prompt/config and any companion
  config files before classifying or correcting an automation.
- When automations use local checkouts for advisory diagnostics, canonical
  tool execution, or scheduled validation, they may refresh a checkout only
  when the checkout exists, the working tree is clean, the checkout is on the
  expected default branch, the branch tracks the expected upstream, and the
  update can be completed with `git fetch` plus `git pull --ff-only`. If the
  checkout is dirty, detached, on a feature branch, has unpushed work, lacks
  upstream tracking, or cannot fast-forward cleanly, do not modify it; report
  the local state as stale or blocked instead. Safe local refresh is not
  hosted remediation. Do not switch branches to normalize state, use
  `merge --ff-only` as a `pull --ff-only` fallback, reset, rebase, stash,
  force checkout, delete branches, force-clean, or discard work.
- When repository additions, removals, renames, archived state, visibility, or
  coverage expectations change, refresh automation scope through the
  repo-awareness and onboarding procedure in
  [`repo-awareness-onboarding-refresh.md`](repo-awareness-onboarding-refresh.md)
  instead of editing prompt allowlists in isolation.
- Skipped work should be reported with reasons, not hidden as a clean pass.
- Automations must not replace repo validation, pull request review, or human
  approval gates.

## Configuration Notes

- Entries reflect currently active maintenance automations at the time this
  registry was last refreshed from inspected local config.
- This document summarizes behavior, intent, and drift-handling expectations;
  it does not replicate full prompt bodies or local configuration.
- Treat automation configuration, run state, schedules, and logs as local
  operational state, not canonical workflow guidance.
- Detailed automation configuration should remain in local configuration files,
  not in the playbook.
- When local automation configuration is human-maintained, follow the TOML
  readability guidance in
  [`engineering-baseline.md`](engineering-baseline.md#human-maintained-toml-readability).
- Do not expose secrets, local-only paths, raw prompts containing private
  context, or environment-specific details in the playbook.
