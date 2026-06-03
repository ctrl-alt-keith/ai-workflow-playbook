# Bootstrap Local Starter Prompt

Use this prompt with an LLM inside the target repository.

## Prompt

You are helping adopt the AI Workflow Playbook in an existing workplace or team
repository.

Your task is to inspect the target repository and create local workflow
scaffolding only. Create a `.ai-workflow/` directory with repo-specific notes,
a review packet template, and, when useful, an optional `AGENTS.template.md`.

Canonical workflow guidance remains in the playbook `docs/` directory. Treat
this local scaffold as advisory adoption support, not a fork of the playbook
and not an enforcement layer.

Before writing files:

1. Inspect the repository's existing contributor docs, README files,
   validation commands, package metadata, Makefile or task runner, CI config,
   review guidance, and any existing `AGENTS.md`.
2. Identify the repository's current source of truth for validation, review,
   release, and team process.
3. Use source-first verification: rely on inspected files and command output,
   not memory, summaries, or assumptions.
4. Respect existing workplace and team processes.
5. Do not assume administrator rights.
6. Do not assume solo-operator governance.

Create or update only local workflow scaffold files under `.ai-workflow/`.
Recommended files:

- `.ai-workflow/repo-notes.md`
- `.ai-workflow/review-packet-template.md`
- `.ai-workflow/AGENTS.template.md` when useful

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

If repository write access and GitHub/PR tooling are available, create a
branch, commit the `.ai-workflow/` scaffold changes, and open a pull request
ready for review. If PR creation is unavailable or the user requested a
local-only pass, leave the changes in the working tree and report the exact
files changed.

When finished, report:

- files created or updated
- source evidence inspected
- validation commands discovered
- any unknowns or assumptions
- confirmation that no source code, CI/CD, GitHub settings, branch protection,
  `CODEOWNERS`, release automation, enforcement controls, or root `AGENTS.md`
  were modified
