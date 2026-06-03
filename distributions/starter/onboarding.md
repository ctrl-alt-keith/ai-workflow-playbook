# Starter Onboarding

## Goal

Adopt the playbook through a work-local AI Workflow Playbook repository that
workplace AI tools can reference as the canonical guidance source.

Canonical workflow guidance stays in [`../../docs/`](../../docs/). This
distribution helps a team point to that guidance from local working files; it
does not replace it.

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
7. Use a local-only folder when the team is not ready to publish anything.
8. Apply the selected path with
   [`prompts/bootstrap-local-starter.md`](prompts/bootstrap-local-starter.md).
9. Fill in notes from observed source evidence, not memory or assumptions.
10. Use reviewable PRs for hosted repository changes when tooling is available.
11. Consider a root `AGENTS.md` only if the team explicitly wants repo-local
   agent instructions.

## First-Pass Outputs

For a hosted playbook repository, the bootstrap prompt should create a small,
reviewable branch that points workplace AI tools to canonical playbook docs and
captures adoption notes or templates without duplicating doctrine.

For a project repository, the bootstrap prompt may create local workflow
scaffolding such as:

- `.ai-workflow/repo-notes.md`
- `.ai-workflow/review-packet-template.md`
- `.ai-workflow/AGENTS.template.md` when useful

These files should describe current local practice and point to canonical
playbook docs. They should not impose requirements that the repository or team
has not accepted.

For a local-only folder, the bootstrap prompt should create files locally and
report the path clearly.

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
