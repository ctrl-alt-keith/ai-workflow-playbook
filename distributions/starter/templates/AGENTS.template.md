# AGENTS.md Template

This is a draft template for a repository that chooses to adopt repo-local AI
workflow guidance. Do not install it as root `AGENTS.md` unless the repository
team explicitly requests that change.

## Canonical Guidance

This repository uses the local AI Workflow Playbook as the canonical source for
reusable workflow guidance in this environment. Repo-local instructions
describe only this repository's execution details, such as setup, validation,
branch conventions, and team process.

Recommended canonical entry points are local to the generated playbook
repository. When installing this template into a project repository, replace
`docs/` paths with the URL or path to the local playbook repository.

- `docs/start-here.md`
- `docs/source-first-retrieval.md`
- `docs/repo-readiness.md`
- `docs/review-packet.md`

## Repository Startup

Before acting:

1. Read this repository's current contributor, setup, and validation docs.
2. Inspect current source state before relying on summaries or prior context.
3. Identify the interaction mode: implementation, review/audit, or
   orchestration/prompt-authoring.
4. Use the repository's documented validation path.
5. Respect existing team review, release, and approval processes.

## Local Commands

Replace this section with commands verified from repository sources.

- Setup: `[documented setup command or "not documented"]`
- Validation: `[canonical validation command or "not documented"]`
- Tests: `[test command or "covered by validation"]`
- Formatting or linting: `[command or "covered by validation"]`

## Working Expectations

- Prefer small, reviewable changes.
- Keep source-first evidence visible in summaries and review packets.
- Report validation evidence clearly.
- Keep suggested workflow changes advisory unless explicitly asked to implement
  them.
- Do not modify CI/CD, GitHub settings, branch protection, `CODEOWNERS`,
  release automation, or enforcement controls unless the team explicitly
  requests that specific work.

## Review Packet

Before requesting human review, include:

- objective
- scope and explicit non-scope
- source evidence inspected
- validation run and result
- risks, unknowns, and follow-up decisions
- recommendation for review
