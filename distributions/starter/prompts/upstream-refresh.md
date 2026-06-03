# Upstream Refresh Prompt

Use this prompt in a work-local or organization-local AI Workflow Playbook
repository when you want to review upstream changes from
`ctrl-alt-keith/ai-workflow-playbook`.

## Prompt

You are helping review upstream AI Workflow Playbook changes for a local
workplace or organization playbook repository.

This is an upstream review workflow, not synchronization.

Do not blindly synchronize. Do not overwrite local decisions. Do not assume
upstream is automatically correct for the local environment. Evaluate
applicability and intent. Prefer adaptation over copying when local context
differs.

## Inputs

- Local playbook repository: `[local repository URL, owner/name, or path]`
- Upstream repository: `ctrl-alt-keith/ai-workflow-playbook`
- Review range or period: `[since last refresh, date range, commit range, or recent merged PRs]`
- Requested output: `[review report only | implement recommended updates]`

If the local repository, upstream source, or review range is ambiguous, stop
and ask for the missing target.

## Review Process

1. Inspect the local playbook repository, including its README, local adoption
   notes, templates, prompts, and any local `AGENTS.md`.
2. Inspect upstream `ctrl-alt-keith/ai-workflow-playbook`.
3. Review relevant canonical upstream docs, especially:
   - `docs/start-here.md`
   - `docs/source-first-retrieval.md`
   - `docs/repo-readiness.md`
   - `docs/engineering-baseline.md`
   - `docs/review-packet.md`
4. Review recent merged upstream pull requests in the requested range.
5. Identify candidate upstream changes that may affect the local playbook.
6. Classify each candidate:
   - adopt now
   - adapt with edits
   - not applicable
   - human decision required

## Evaluation Guidance

For each candidate, consider:

- upstream intent and problem addressed
- local workplace or organization context
- existing local decisions and documented deviations
- whether adopting the change would improve source-first verification,
  reviewability, validation evidence, or team compatibility
- whether adaptation is safer than copying
- whether the change would introduce governance, enforcement, CI/CD, settings,
  branch protection, `CODEOWNERS`, release automation, or automatic promotion
  behavior

Do not create a requirement to track every upstream change. Preserve local
ownership.

## Deliverables

Produce a review report with:

- upstream changes reviewed
- recommended actions
- rationale for each recommendation
- proposed implementation plan when updates are recommended
- explicit unknowns or source evidence that could not be inspected

If repository modifications are requested and tooling is available:

1. Create a branch.
2. Commit only the selected local playbook updates.
3. Open a reviewable pull request.
4. Report the PR link, files changed, validation run, and residual risks.

Otherwise, produce a review report only.

## Boundaries

Do not introduce automatic synchronization. Do not introduce enforcement
behavior. Do not overwrite local decisions. Do not create a requirement to
track every upstream change. Do not duplicate large amounts of upstream
doctrine.
