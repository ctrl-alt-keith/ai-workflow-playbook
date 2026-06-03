# Starter Onboarding

## Goal

Adopt the playbook in an existing team repository with the smallest useful local
scaffold: notes, review packet shape, and optional repo-local agent guidance.

Canonical workflow guidance stays in [`../../docs/`](../../docs/). This
distribution helps a team point to that guidance from local working files; it
does not replace it.

## Adoption Path

1. Read the canonical startup guidance in
   [`../../docs/start-here.md`](../../docs/start-here.md).
2. Inspect the target repository's existing contributor guidance, review norms,
   validation commands, and team process.
3. Create local `.ai-workflow/` scaffolding in the target repository using
   [`prompts/bootstrap-local-starter.md`](prompts/bootstrap-local-starter.md).
4. Fill in repo-specific notes from observed source evidence, not memory or
   assumptions.
5. Use the review packet template for one or two small PRs before changing
   team-wide process.
6. Consider a root `AGENTS.md` only if the team explicitly wants repo-local
   agent instructions.

## First-Pass Local Outputs

The bootstrap prompt should create local workflow scaffolding only, such as:

- `.ai-workflow/repo-notes.md`
- `.ai-workflow/review-packet-template.md`
- `.ai-workflow/AGENTS.template.md` when useful

These files should describe current local practice and point to canonical
playbook docs. They should not impose requirements that the repository or team
has not accepted.

## Team Compatibility

When applying the starter in a workplace repository:

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
