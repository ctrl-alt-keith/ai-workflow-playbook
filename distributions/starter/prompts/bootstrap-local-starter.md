# Bootstrap Local Starter Prompt

Use this prompt with an LLM that can inspect the intended adoption destination.

## Prompt

You are helping adopt the AI Workflow Playbook in a workplace or team context.

Your task is to inspect the intended destination and create the correct starter
structure for that destination. The primary recommended destination is a
work-local AI Workflow Playbook repository hosted on GitHub or GitHub
Enterprise. Repo-local `.ai-workflow/` scaffolds are a secondary path for
project repositories, and local-only folders are a fallback for experimentation.

For a generated work-local playbook repository, local `docs/start-here.md`
becomes the canonical starting point for that environment. Upstream
`ctrl-alt-keith/ai-workflow-playbook` is the provenance and refresh source, not
the day-to-day authority. Treat this starter output as advisory adoption
support, not an enforcement layer.

## Destination Selection

Before writing files, determine which adoption target is intended:

- existing GitHub or GitHub Enterprise playbook repository
- new GitHub or GitHub Enterprise playbook repository
- existing project repository requiring `.ai-workflow/` scaffolding
- local-only folder

If the destination is ambiguous, stop and ask which target to use.

## Destination Outcomes

For a work-local playbook repository, the destination itself becomes the
playbook. Create repository-level content directly in the destination. Do not
create a top-level `.ai-workflow/` directory.

Expected playbook-repository structure should resemble:

- `README.md`
- `docs/start-here.md`
- `docs/source-first-retrieval.md`
- `docs/repo-readiness.md`
- `docs/review-packet.md`
- `prompts/upstream-refresh.md`
- `templates/AGENTS.template.md`
- `templates/review-packet-template.md`

Adjust that structure only when local context shows a better lightweight shape.
Keep the content lightweight and adapted to the environment; do not wholesale
copy upstream doctrine.

For an existing project repository, create local workflow scaffolding under
`.ai-workflow/`. This is the only destination type that should receive a
top-level `.ai-workflow/` directory by default.

For a local-only folder, determine whether the folder represents a future
playbook repository or project-local workflow scaffolding before creating
files. If that intent is ambiguous, stop and ask.

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

For an existing playbook repository, create or update only lightweight
repository-level content that points workplace AI tools to local
`docs/start-here.md`. Retain a reference to `prompts/upstream-refresh.md` for
periodic upstream review.

For a new playbook repository, create the repository when tooling, user-provided
repository details, and permissions allow. If repository creation is
unavailable, provide explicit repository creation instructions and stop before
making assumptions. Include local `docs/start-here.md` as the environment's
canonical starting point and `prompts/upstream-refresh.md` for future upstream
review.

For an existing project repository, create or update only project-local
workflow scaffold files under `.ai-workflow/`. Recommended files:

- `.ai-workflow/repo-notes.md`
- `.ai-workflow/review-packet-template.md`
- `.ai-workflow/AGENTS.template.md` when useful

For a local-only future playbook repository, create repository-level content
directly in the selected folder. For a local-only project scaffold, create the
selected scaffold files under `.ai-workflow/` and report the path.

Work-local playbook repository content should include:

- a `README.md` that tells users and tools to start with local
  `docs/start-here.md`
- a lightweight local `docs/start-here.md` that identifies this repository as
  the environment's canonical playbook entrypoint
- lightweight local docs for source-first retrieval, repo readiness, and review
  packets, adapted to local context
- `prompts/upstream-refresh.md`, describing upstream as source material and
  future improvements to review, not blindly sync
- `templates/AGENTS.template.md`, pointing adopters to local
  `docs/start-here.md`
- `templates/review-packet-template.md`

Project repo notes should capture:

- repository purpose and main technologies, based on inspected sources
- canonical local setup and validation commands, if discoverable
- current review or contribution process, if documented
- source-first retrieval reminders for this repository
- known unknowns where source evidence was not available
- links to the local playbook's canonical docs:
  - `[local-playbook]/docs/start-here.md`
  - `[local-playbook]/docs/source-first-retrieval.md`
  - `[local-playbook]/docs/repo-readiness.md`
  - `[local-playbook]/docs/review-packet.md`

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

For a local-only destination, create files locally using the selected
playbook-repository or project-scaffold structure and report the path.

When finished, report:

- files created or updated
- source evidence inspected
- validation commands discovered
- any unknowns or assumptions
- confirmation that no source code, CI/CD, GitHub settings, branch protection,
  `CODEOWNERS`, release automation, enforcement controls, or root `AGENTS.md`
  were modified
