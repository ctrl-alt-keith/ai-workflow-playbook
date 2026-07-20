# Starter Onboarding

## Goal

Adopt the playbook through a work-local AI Workflow Playbook repository that
workplace AI tools can reference as the canonical guidance source.

The generated work-local playbook becomes the canonical starting point for that
environment. Upstream `https://github.com/ctrl-alt-keith/ai-workflow-playbook`
remains provenance and refresh source material.

## Adoption Path

1. Create or identify the destination repository or local folder.
2. Choose the adoption destination:
   - an existing GitHub or GitHub Enterprise playbook repository
   - a new GitHub or GitHub Enterprise playbook repository
   - a project repository that needs `.ai-workflow/` scaffolding
   - a local-only folder for experimentation
3. Prefer a hosted playbook repository when workplace AI tools need one
   canonical place to read guidance.
4. Open Codex, Claude, ChatGPT, or another agent with access to the selected
   destination.
5. Copy the tiny launcher prompt from
   [`prompts/use-this-starter.md`](prompts/use-this-starter.md). It points the
   agent at the canonical bootstrap prompt in this repository.
6. Use project-repo `.ai-workflow/` scaffolding when a specific repository
   needs local notes or templates.
7. Use a local-only folder when the team is not ready to publish anything, but
   first decide whether that folder is a future playbook repository or a
   project-local scaffold.
8. Apply the selected path with
   [`prompts/bootstrap-local-starter.md`](prompts/bootstrap-local-starter.md).
9. Fill in notes from observed source evidence, not memory or assumptions.
10. Use reviewable PRs for hosted repository changes when tooling is available.
11. Consider a root `AGENTS.md` only if the team explicitly wants repo-local
   agent instructions.

## First-Pass Outputs

For a hosted playbook repository, the bootstrap prompt should create a small,
reviewable branch that points workplace AI tools to local `docs/start-here.md`
and captures adapted docs, prompts, and templates without duplicating upstream
doctrine. It should also retain a reference to
[`prompts/upstream-refresh.md`](prompts/upstream-refresh.md) for future
upstream review. This content belongs directly at the repository level; do not
wrap it in `.ai-workflow/`.

Minimum work-local playbook skeleton:

- `README.md`
- `docs/start-here.md`
- `docs/source-first-retrieval.md`
- `docs/repo-readiness.md`
- `docs/review-packet.md`
- `prompts/upstream-refresh.md`
- `templates/AGENTS.template.md`
- `templates/review-packet-template.md`

For a project repository, the bootstrap prompt may create local workflow
scaffolding such as:

- `.ai-workflow/repo-notes.md`
- `.ai-workflow/review-packet-template.md`
- `.ai-workflow/AGENTS.template.md` when useful

These files should describe current local practice and point to canonical
playbook docs. They should not impose requirements that the repository or team
has not accepted.

For a local-only folder, the bootstrap prompt should create files locally and
report the path clearly. If the folder is a future playbook repository, create
repository-level playbook content. If it is a project-local scaffold, use
`.ai-workflow/`.

## Ongoing Upstream Review

Use [`prompts/upstream-refresh.md`](prompts/upstream-refresh.md) periodically to
compare the local playbook with upstream
`https://github.com/ctrl-alt-keith/ai-workflow-playbook`. The goal is to review
and decide, not synchronize.

The local playbook and upstream source do not need to share a repository host.
Resolve upstream from the explicit URL, and ask for an alternate source if that
URL is unavailable.

For a Git-backed work-local repository with upstream Git access, use a
protected `upstream` remote whose fetch URL is canonical and whose push URL is
`DISABLED`. Record the last reviewed upstream commit and review date in
`upstream-review-baseline.md`, and keep each implemented refresh report under
`refresh-reports/`. Report-only reviews remain conversational and create
neither file. The baseline records review coverage, not adoption.

Classify candidate changes as adopt now, adapt with edits, not applicable, or
human decision required. Preserve local ownership and workplace context.

## Team Compatibility

When applying the starter in a workplace context:

- respect existing review, approval, release, and incident processes
- identify the repository's actual validation command before proposing changes
- prefer advisory notes over settings changes
- avoid assuming administrator access or solo-operator governance
- keep adoption reversible and easy to review

## What To Defer

Defer governance, automation, and enforcement until the team has used the local
scaffold and decided what, if anything, should become durable process.

Do not use this starter to change CI/CD, GitHub settings, branch protection,
`CODEOWNERS`, release automation, or enforcement controls.
