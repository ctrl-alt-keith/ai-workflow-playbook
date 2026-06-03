# Bootstrap Local Starter Prompt

Use this prompt with an LLM that can inspect the intended adoption destination.

## Prompt

You are helping adopt the AI Workflow Playbook in a workplace or team context.

Your task is to inspect the intended destination and create workflow
scaffolding only. The primary recommended destination is a work-local AI
Workflow Playbook repository hosted on GitHub or GitHub Enterprise. Repo-local
`.ai-workflow/` scaffolds are a secondary path for project repositories, and
local-only folders are a fallback for experimentation.

Canonical workflow guidance remains in the playbook `docs/` directory. Treat
this local scaffold as advisory adoption support, not a fork of the playbook
and not an enforcement layer.

## Destination Selection

Before writing files, determine which adoption target is intended:

- existing GitHub or GitHub Enterprise playbook repository
- new GitHub or GitHub Enterprise playbook repository
- existing project repository requiring `.ai-workflow/` scaffolding
- local-only folder

If the destination is ambiguous, stop and ask which target to use.

Before writing files:

1. For any repository destination, inspect the repository's existing
   contributor docs, README files, validation commands, package metadata,
   Makefile or task runner, CI config, review guidance, and any existing
   `AGENTS.md`.
2. For any repository destination, identify the repository's current source of
   truth for validation, review, release, and team process.
3. Use source-first verification: rely on inspected files and command output,
   not memory, summaries, or assumptions.
4. Respect existing workplace and team processes.
5. Do not assume administrator rights.
6. Do not assume solo-operator governance.

For an existing playbook repository, create or update only lightweight adoption
scaffold that points workplace AI tools to canonical playbook docs. Retain a
reference to `distributions/starter/prompts/upstream-refresh.md` for periodic
upstream review.

For a new playbook repository, create the repository when tooling, user-provided
repository details, and permissions allow. If repository creation is
unavailable, provide explicit repository creation instructions and stop before
making assumptions. Include a reference to
`distributions/starter/prompts/upstream-refresh.md` for future upstream review.

For an existing project repository, create or update only local workflow
scaffold files under `.ai-workflow/`. Recommended files:

- `.ai-workflow/repo-notes.md`
- `.ai-workflow/review-packet-template.md`
- `.ai-workflow/AGENTS.template.md` when useful

For a local-only destination, create the selected scaffold files locally and
report the path.

The repo notes should capture:

- repository purpose and main technologies, based on inspected sources
- canonical local setup and validation commands, if discoverable
- current review or contribution process, if documented
- source-first retrieval reminders for this repository
- known unknowns where source evidence was not available
- links back to canonical playbook docs:
  - `docs/start-here.md`
  - `docs/source-first-retrieval.md`
  - `docs/repo-readiness.md`
  - `docs/engineering-baseline.md`
  - `docs/review-packet.md`

The review packet template should help contributors report:

- objective
- scope and explicit non-scope
- source evidence inspected
- validation run and results
- risks, unknowns, and follow-up decisions
- recommendation for human review

The optional `AGENTS.template.md` should be a draft template only. It may show
how repo-local agent guidance could point to canonical playbook docs and local
validation commands, but it must not be installed as root `AGENTS.md` unless the
user explicitly requests that in a separate instruction.

Hard boundaries:

- Do not create or modify root `AGENTS.md` unless the user explicitly requests
  it.
- Do not modify source code.
- Do not modify CI/CD.
- Do not modify GitHub settings.
- Do not modify branch protection.
- Do not modify `CODEOWNERS`.
- Do not modify release automation.
- Do not modify enforcement controls.
- Do not create new governance requirements.
- Do not make settings or process changes on behalf of the team.

Make every suggested workflow change advisory unless the user explicitly
requests implementation.

## Deliverable

For an existing repository destination, create a branch, commit changes, and
open a reviewable pull request when tooling is available. If PR creation is
unavailable, leave the changes in the working tree and report the exact files
changed.

For a new repository destination, create the repository when tooling,
user-provided repository details, and permissions allow. If creation is
unavailable, provide explicit repository creation instructions and stop before
making assumptions.

For a local-only destination, create files locally and report the path.

When finished, report:

- files created or updated
- source evidence inspected
- validation commands discovered
- any unknowns or assumptions
- confirmation that no source code, CI/CD, GitHub settings, branch protection,
  `CODEOWNERS`, release automation, enforcement controls, or root `AGENTS.md`
  were modified
