# Maintenance Automations

Codex maintenance automations are part of the orchestration model: they keep
recurring checks visible, bounded, and reviewable without turning the playbook
into an automation implementation repo.

This document owns reusable policy and pattern guidance for maintenance
automation. The inventory below is noncanonical reference material copied from
current local Codex `automation.toml` configs; the active local automation
configs remain the owning source for runtime state, schedules, prompts, and
execution paths.

## Reference Inventory

| Automation | ID | Purpose | Cadence | Target Scope | Mode | Safety Expectations / Skip Conditions |
| --- | --- | --- | --- | --- | --- | --- |
| 🧹 Delete merged repo branches | `delete-merged-repo-branches` | Use `enforcement.branch_cleanup` to dry-run and apply Git-proven merged branch cleanup, then report preserved stale or blocked refs. | Weekly. | Automation-owned config currently covers `knowledge-adapters`, `knowledge-vault`, `ka-destinations`, `ai-workflow-playbook`, `ai-workflow-enforcement`, `ai-workflow-incubator`, `linode-image-lab`, `linode-backup-lab`, `nexus`, and `.github`. | Mutating through the tool's explicit `--apply` path for normal Git-proven cleanup; stale non-ancestor cleanup remains report-only unless explicit approval evidence is supplied in the automation config. | Refresh the enforcement tool from current `origin/main`, run dry-run first, and rely on tool output for reporting. Skip dirty repos; preserve protected refs, symbolic refs, unsafe worktrees, ambiguous refs, and stale non-ancestor refs without explicit approval evidence. Never recreate cleanup logic in the prompt, force-delete ad hoc, commit, or open PRs. |
| 🧠 Staging vs Canon Audit | `staging-vs-canon-audit` | Audit drift between staging notes, canonical playbook guidance, and repo-local execution layers. | Weekly. | The `ctrl-alt-keith` workspace guidance layer, including the playbook, repo-local `AGENTS.md` files, and staging/reference material. | Report-only. | Stay read-only; do not modify files, refs, branches, working trees, automation prompts, or repository state. Ignore generated and dependency paths. Treat freshness findings as context only. |
| 🔍 AGENTS Drift Detector | `agents-drift-detector` | Audit repo-local `AGENTS.md` guidance and local workspace-routing guidance against the canonical playbook. | Weekly. | `ai-workflow-playbook`, `ai-workflow-enforcement`, `ai-workflow-incubator`, `knowledge-adapters`, `knowledge-vault`, `ka-destinations`, `linode-image-lab`, `linode-backup-lab`, `nexus`, `.github`, plus the local-only workspace-level `~/src/ctrl-alt-keith/AGENTS.md`. | Report-only. | Inspect latest `origin/main` state for repositories. Review the workspace-level `AGENTS.md` as local-only, noncanonical routing guidance, not as a repository policy document. If a repository or the local workspace file cannot be inspected, mark that scope blocked. Do not modify files or branches, and do not invent missing repo details. |
| 🛡️ Workflow Drift Audit | `workflow-drift-audit` | Run the calibrated `ai-workflow-enforcement` advisory drift scanner and report workflow-policy drift findings. | Weekly. | `ctrl-alt-keith` workspace guidance and workflow-policy surfaces covered by the scanner drift config. | Report-only advisory scan. | Treat findings as advisory, not failures. Do not modify files, branches, worktrees, automation state, or repository state. Skip and report when the enforcement checkout, scanner config, dependencies, workspace scope, command result, or mutation safety is uncertain. |
| 🔎 Org PR and Issue Scan | `org-pr-issue-scan` | Report current open pull requests and open issues across visible repositories in the `ctrl-alt-keith` GitHub organization. | Weekly. | Dynamically enumerated repositories in the `ctrl-alt-keith` GitHub organization. | Report-only. | Use existing `gh` authentication and the `ai-workflow-enforcement` scanner. Do not create, edit, close, label, assign, or comment on GitHub issues or pull requests. Clearly report skipped or inaccessible repositories and skip when the scanner, auth, organization access, or mutation safety is uncertain. |
| 🧪 knowledge-adapters weekly chaos-all validation | `knowledge-adapters-weekly-chaos-all-validation` | Run exhaustive scheduled validation for `knowledge-adapters` and report the result. | Weekly. | `knowledge-adapters`. | Report-only validation. | Refresh from current `origin/main`, run `make chaos-all`, and report the tested commit SHA. Do not modify files, open PRs, or run live-service or credential-dependent checks. |
| 🗜️ memory-compaction | `memory-compaction` | Inspect Codex automation memory files for oversized repetitive run history and propose compact durable replacements. | Weekly. | Local Codex automation memories under `~/.codex/automations/*/memory.md`. | Report-only proposal. | Use 25 KiB as the default oversized threshold. Preserve durable operational state and recent context. Do not rewrite, delete, truncate, or otherwise mutate memory files unless a human explicitly approves a later follow-up. |

## Memory Compaction

Codex automation memory files can grow indefinitely when scheduled runs append
historical detail. Treat memory growth as operational maintenance: oversized
memory can make recurring runs noisier, slower to inspect, and more likely to
carry stale context forward.

Use 25 KiB as the default oversized threshold unless an automation has a clear
reason to retain more local state. Repetitive run logs, duplicate summaries,
old validation transcripts, and resolved transient errors are lower-value than
compact durable operational state.

Prefer preserving:

- automation purpose
- durable decisions
- active risks and gotchas
- unresolved TODOs or blockers
- recent operational state

Operators should compact memories manually when a memory file exceeds the
threshold, repeated run logs crowd out the current state, stale history starts
shaping automation behavior, or an automation prompt or cadence is being
reviewed. Manual compaction should start from the current file, draft a compact
replacement, compare the replacement against the original for lost durable
context, and only then apply the change with explicit human approval.

### Suggested Prompt

Use this prompt for the `🗜️ memory-compaction` automation:

```text
Task:
Run a report-only Codex automation memory compaction review.

Scope:
- Inspect local Codex automation memory files at
  `~/.codex/automations/*/memory.md`.
- Treat 25 KiB as the default oversized threshold.
- Identify memory files at or above the threshold.

Goal:
For each oversized memory file, propose a compact replacement that preserves
durable operational state while reducing repetitive historical run detail.

Preserve:
- automation purpose
- durable decisions
- active risks and gotchas
- unresolved TODOs or blockers
- recent operational state

Lower-value content to summarize or omit from the proposed replacement:
- repetitive run-by-run logs
- duplicate summaries of the same outcome
- old validation transcripts or command output
- resolved transient errors
- stale historical detail that no longer changes future operation

Constraints:
- Report-only proposal mode.
- Do not rewrite, delete, truncate, or otherwise mutate memory files.
- Do not modify automation configs, repositories, branches, or working trees.
- Do not introduce scripts, enforcement tools, or automatic file rewriters.
- Do not discard useful durable context.
- If a file is unreadable or contains sensitive content that should not be
  repeated in full, report the blocker or summarize with redaction.

Output:
1. Summary
   - Number of memory files inspected.
   - Number over the threshold.
   - Any files skipped or blocked.

2. Oversized Memories
   - Path.
   - Approximate size.
   - Main sources of low-value growth.
   - Durable state that must be preserved.

3. Proposed Replacements
   - For each oversized memory, provide a proposed replacement body in
     Markdown.
   - Keep each proposal compact and directly reviewable.
   - Include enough recent operational state for the next automation run to
     continue safely.

4. Follow-Up
   - State whether human review is recommended.
   - State that no memory files or automation configs were modified.
```

## Guidance Layers

- Follow the authority boundary in
  [`start-here.md`](start-here.md#source-authority-map).
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
  reference was updated.
- This document summarizes behavior and intent; it does not replicate full prompt
  bodies or local configuration.
- Treat automation configuration, run state, schedules, and logs as local
  operational state, not canonical workflow guidance.
- Detailed automation configuration should remain in local configuration files,
  not in the playbook.
- When local automation configuration is human-maintained, follow the TOML
  readability guidance in
  [`engineering-baseline.md`](engineering-baseline.md#human-maintained-toml-readability).
- Do not expose secrets, local-only paths, raw prompts containing private
  context, or environment-specific details in the playbook.
