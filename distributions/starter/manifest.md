# Starter Manifest

## Package Role

`distributions/starter/` is a lightweight adoption scaffold for applying the AI
Workflow Playbook in an existing team repository.

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
- `prompts/bootstrap-local-starter.md`: LLM prompt for creating local
  `.ai-workflow/` scaffolding
- `templates/AGENTS.template.md`: optional repo-local agent instruction
  template
- `templates/review-packet-template.md`: local review packet template
- `templates/repo-notes-template.md`: local repo notes template

## Expected Adopter Outputs

The bootstrap prompt is expected to create advisory local files under the
target repository's `.ai-workflow/` directory, such as:

- `.ai-workflow/repo-notes.md`
- `.ai-workflow/review-packet-template.md`
- `.ai-workflow/AGENTS.template.md` when the repository would benefit from a
  draft template

The bootstrap prompt must not create or modify root `AGENTS.md` unless the
human explicitly requests that specific change.

## Explicit Non-Goals

This starter must not:

- duplicate large amounts of doctrine from `docs/`
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
