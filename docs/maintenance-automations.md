# Maintenance Automations

Codex maintenance automations are part of the orchestration model: they keep
recurring checks visible, bounded, and reviewable without turning the playbook
into an automation implementation repo.

This document owns reusable policy and pattern guidance for maintenance
automation. The inventory below is non-canonical reference material copied from
current local Codex `automation.toml` configs; the active local automation
configs remain the owning source for runtime state, schedules, prompts, and
execution paths.

## Reference Inventory

| Automation | ID | Purpose | Cadence | Target Scope | Mode | Safety Expectations / Skip Conditions |
| --- | --- | --- | --- | --- | --- | --- |
| 🧹 Delete merged repo branches | `delete-merged-repo-branches` | Clean up branches Git confirms are merged, then report remaining unmerged branch state. | Weekly. | `knowledge-adapters`, `ka-destinations`, `ai-workflow-playbook`, `ai-workflow-enforcement`, `linode-image-lab`, `linode-backup-lab`. | Mutating, bounded to merged local and remote branch deletion. | Skip repos with dirty working trees, failed fetch/switch/pull, unclear default branches, active worktrees, protected refs, symbolic refs, empty branch names, or any uncertainty. Never force-delete, remove worktree directories, delete unmerged branches, commit, or open PRs. |
| 🧠 Staging vs Canon Audit | `staging-vs-canon-audit` | Audit drift between staging notes, canonical playbook guidance, and repo-local execution layers. | Weekly. | The `ctrl-alt-keith` workspace guidance layer, including the playbook, repo-local `AGENTS.md` files, and staging/reference material. | Report-only. | Stay read-only; do not modify files, refs, branches, working trees, automation prompts, or repository state. Ignore generated and dependency paths. Treat freshness findings as context only. |
| 🔍 AGENTS Drift Detector | `agents-drift-detector` | Audit repo-local `AGENTS.md` guidance and local workspace-routing guidance against the canonical playbook. | Weekly. | `ai-workflow-playbook`, `ai-workflow-enforcement`, `ai-workflow-incubator`, `knowledge-adapters`, `ka-destinations`, `linode-image-lab`, `linode-backup-lab`, `.github`, plus the local-only workspace-level `~/src/ctrl-alt-keith/AGENTS.md`. | Report-only. | Inspect latest `origin/main` state for repositories. Review the workspace-level `AGENTS.md` as local-only, non-canonical routing guidance, not as a repository policy document. If a repository or the local workspace file cannot be inspected, mark that scope blocked. Do not modify files or branches, and do not invent missing repo details. |
| 🛡️ Workflow Drift Audit | `workflow-drift-audit` | Run the calibrated `ai-workflow-enforcement` advisory drift scanner and report workflow-policy drift findings. | Weekly. | `ctrl-alt-keith` workspace guidance and workflow-policy surfaces covered by the scanner drift config. | Report-only advisory scan. | Treat findings as advisory, not failures. Do not modify files, branches, worktrees, automation state, or repository state. Skip and report when the enforcement checkout, scanner config, dependencies, workspace scope, command result, or mutation safety is uncertain. |
| 🔎 Org PR and Issue Scan | `org-pr-issue-scan` | Report current open pull requests and open issues across visible repositories in the `ctrl-alt-keith` GitHub organization. | Weekly. | Dynamically enumerated repositories in the `ctrl-alt-keith` GitHub organization. | Report-only. | Use existing `gh` authentication and the `ai-workflow-enforcement` scanner. Do not create, edit, close, label, assign, or comment on GitHub issues or pull requests. Clearly report skipped or inaccessible repositories and skip when the scanner, auth, organization access, or mutation safety is uncertain. |
| 🧪 knowledge-adapters weekly chaos-all validation | `knowledge-adapters-weekly-chaos-all-validation` | Run exhaustive scheduled validation for `knowledge-adapters` and report the result. | Weekly. | `knowledge-adapters`. | Report-only validation. | Refresh from current `origin/main`, run `make chaos-all`, and report the tested commit SHA. Do not modify files, open PRs, or run live-service or credential-dependent checks. |

## Guidance Layers

- Canonical playbook guidance lives in this repository and defines reusable
  cross-repo workflow expectations.
- Workspace-level routing guidance may live in a local-only workspace
  `AGENTS.md`. It can describe multi-repository boundaries, scratch usage,
  command form, and how to enter target repositories, but it is non-canonical
  and must not define repository branch, commit, PR, or validation policy.
- Repo-local execution guidance lives in each repository's `AGENTS.md` and
  remains authoritative for that repository's validation path, file placement,
  branch conventions, PR expectations, and repo-specific constraints.
- Drift review should compare repo-local `AGENTS.md` files against the playbook
  and any relevant workspace-routing guidance, while comparing workspace-level
  routing guidance against reusable playbook expectations and observed
  repo-local execution patterns. Do not require the workspace file to duplicate
  repo-only rules.

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
- Skipped work should be reported with reasons, not hidden as a clean pass.
- Automations must not replace repo validation, pull request review, or human
  approval gates.

## Configuration Notes

- Entries reflect currently active maintenance automations at the time this
  reference was updated.
- This document summarizes behavior and intent; it does not replicate full prompt
  bodies or local configuration.
- Treat automation configuration, run state, schedules, and logs as local
  operational state, not canonical workflow guidance.
- Detailed automation configuration should remain in local configuration files,
  not in the playbook.
- Do not expose secrets, local-only paths, raw prompts containing private
  context, or environment-specific details in the playbook.
