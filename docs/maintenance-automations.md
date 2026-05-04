# Maintenance Automations

Codex maintenance automations are part of the orchestration model: they keep
recurring checks visible, bounded, and reviewable without turning the playbook
into an automation implementation repo.

This inventory reflects the current local Codex `automation.toml` configs. It
summarizes purpose, cadence, scope, mutation behavior, and safety expectations
without copying long prompts or local execution paths.

## Inventory

| Automation | ID | Purpose | Cadence | Target Scope | Mode | Safety Expectations / Skip Conditions |
| --- | --- | --- | --- | --- | --- | --- |
| 🧹 Delete merged repo branches | `delete-merged-repo-branches` | Clean up branches Git confirms are merged, then report remaining unmerged branch state. | Daily at 08:00. | `knowledge-adapters`, `ka-destinations`, `ai-workflow-playbook`, `linode-image-lab`. | Mutating, bounded to merged local and remote branch deletion. | Skip repos with dirty working trees, failed fetch/switch/pull, unclear default branches, active worktrees, protected refs, symbolic refs, empty branch names, or any uncertainty. Never force-delete, remove worktree directories, delete unmerged branches, commit, or open PRs. |
| 🧠 Staging vs Canon Audit | `staging-vs-canon-audit` | Audit drift between staging notes, canonical playbook guidance, and repo-local execution layers. | Weekly on Monday at 08:15. | The `ctrl-alt-keith` workspace guidance layer, including the playbook, repo-local `AGENTS.md` files, and staging/reference material. | Report-only. | Stay read-only; do not modify files, refs, branches, working trees, automation prompts, or repository state. Ignore generated and dependency paths. Treat freshness findings as context only. |
| 🔍 AGENTS Drift Detector | `agents-md-vs-playbook-alignment-audit` | Audit repo-local `AGENTS.md` guidance against the canonical playbook. | Weekly on Monday at 08:15. | `ai-workflow-playbook`, `knowledge-adapters`, `ka-destinations`, `linode-image-lab`. | Report-only. | Inspect latest `origin/main` state only. If a repository cannot be fetched or inspected, mark it blocked. Do not modify files or branches, and do not invent missing repo details. |
| 🧪 knowledge-adapters weekly chaos-all validation | `run-weekly-chaos-all-validation` | Run exhaustive scheduled validation for `knowledge-adapters` and report the result. | Weekly on Monday at 08:30. | `knowledge-adapters`. | Report-only validation. | Refresh from current `origin/main`, run `make chaos-all`, and report the tested commit SHA. Do not modify files, open PRs, or run live-service or credential-dependent checks. |

## Operating Rules

- Name recurring automations by purpose so their intent is clear in schedules,
  reports, and follow-up.
- Report-only is the default for audits and validation checks.
- Mutating automations must be bounded, conservative, and skip on uncertainty.
- Skipped work should be reported with reasons, not hidden as a clean pass.
- Automations must not replace repo validation, pull request review, or human
  approval gates.

## Configuration Notes

- Current entries reflect active Codex cron automations.
- This document summarizes behavior and intent; it does not replicate full prompt
  bodies or local configuration.
- Treat automation configuration as local operational state, not canonical
  workflow guidance.
- Detailed automation configuration should remain in local configuration files,
  not in the playbook.
- Do not expose secrets, local-only paths, raw prompts containing private
  context, or environment-specific details in the playbook.
