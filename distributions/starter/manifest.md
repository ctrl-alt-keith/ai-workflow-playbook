# Starter Manifest

## Package Role

`distributions/starter/` is a lightweight adoption scaffold for establishing a
work-local AI Workflow Playbook repository and, when needed, project-local
workflow notes.

It is not canonical doctrine. It is not a fork of the playbook. It is not an
enforcement layer.

Canonical guidance remains in [`../../docs/`](../../docs/), with these primary
entry points:

- [`../../docs/start-here.md`](../../docs/start-here.md): startup routing and
  invariants
- [`../../docs/source-first-retrieval.md`](../../docs/source-first-retrieval.md):
  source-first verification model
- [`../../docs/repo-readiness.md`](../../docs/repo-readiness.md): interaction
  modes, validation, PR readiness, and governance operating model
- [`../../docs/engineering-baseline.md`](../../docs/engineering-baseline.md):
  engineering expectations for small, validated changes
- [`../../docs/review-packet.md`](../../docs/review-packet.md): human review
  packet format

## Files

- `README.md`: distribution overview and boundaries
- `onboarding.md`: first-pass adoption path
- `manifest.md`: this package inventory
- `prompts/use-this-starter.md`: tiny copy/paste launcher prompt for URL-first
  adoption
- `prompts/bootstrap-local-starter.md`: LLM prompt for selecting an adoption
  destination and creating starter scaffold
- `prompts/upstream-refresh.md`: review-oriented prompt for evaluating upstream
  changes without blind synchronization
- `templates/AGENTS.template.md`: optional repo-local agent instruction
  template
- `templates/review-packet-template.md`: local review packet template
- `templates/repo-notes-template.md`: local repo notes template

## Expected Adopter Outputs

The primary expected destination is a GitHub or GitHub Enterprise playbook
repository that workplace AI tools can reference as canonical guidance. The
preferred entrypoint is the URL-first launcher prompt, which points an agent at
the canonical bootstrap prompt in this repository. Work-local playbook
repositories should retain a reference to the upstream refresh prompt for
periodic review. The destination itself is the playbook repository, so starter
content belongs at repository level rather than under `.ai-workflow/`.

Git-backed work-local repositories with upstream Git access should also use a
protected `upstream` remote. After the first trustworthy review, they should
record `upstream-review-baseline.md` when selected updates are implemented;
implemented refreshes should leave a small report under `refresh-reports/`.
Report-only reviews remain ephemeral. These files record review coverage and
local decisions, not synchronization or adoption state.

Expected work-local playbook skeleton:

- `README.md`
- `docs/start-here.md`
- `docs/source-first-retrieval.md`
- `docs/repo-readiness.md`
- `docs/review-packet.md`
- `prompts/upstream-refresh.md`
- `templates/AGENTS.template.md`
- `templates/review-packet-template.md`

Local `docs/start-here.md` is the canonical entrypoint for that environment.
The fully qualified upstream source,
`https://github.com/ctrl-alt-keith/ai-workflow-playbook`, provides source
material and future improvements to review and adapt. The local playbook and
upstream source may live on different repository hosts.

Secondary project-repository adoption can create advisory local files under
the target repository's `.ai-workflow/` directory, such as:

- `.ai-workflow/repo-notes.md`
- `.ai-workflow/review-packet-template.md`
- `.ai-workflow/AGENTS.template.md` when the repository would benefit from a
  draft template

The bootstrap prompt must not create or modify root `AGENTS.md` unless the
human explicitly requests that specific change.

Local-only folder output is a fallback for experimentation. Before creating
files, determine whether the folder is a future playbook repository or a
project-local scaffold. Report the created path and do not imply the team has
adopted durable process.

## Explicit Non-Goals

This starter must not:

- duplicate large amounts of doctrine from `docs/`
- introduce automatic synchronization with upstream
- create secondary governance, policy, or enforcement rules
- assume administrator rights
- assume solo-operator governance
- modify source code
- modify CI/CD
- modify GitHub settings or branch protection
- modify `CODEOWNERS`
- modify release automation
- modify enforcement controls

## Review Heuristic

A starter change belongs here when it helps a team adopt the playbook locally
with clearer notes, prompts, or templates.

A change belongs in `docs/` when it changes canonical workflow guidance.

A change belongs outside this repository when it implements automation,
enforcement, repository settings management, or project-specific operational
logic.
