# Notes Repositories

Use a notes repository as a staging layer for workflow material that is still
being explored, refined, or validated. Use this playbook repository as the
canonical source only after that material has been proven reusable.

This split keeps early capture lightweight without turning the playbook into a
scratch space.

## Model

- Notes repositories hold provisional material, project-local observations, and
  candidate guidance that may later be promoted.
- The playbook repository holds the cleaned, reusable guidance that now owns
  the cross-repo rule or pattern.
- A notes repository is not a second canonical source once promotion has
  happened.

## What Belongs In Notes

Keep material in notes when it is still one or more of the following:

- tied to one project, team, or delivery arc
- incomplete, exploratory, or still changing quickly
- useful as raw capture but not yet strong enough to guide action elsewhere
- awaiting confirmation that the pattern actually repeats across work

Notes are allowed to be early, messy, and local. The playbook is not.

## Promotion Criteria

Promote notes into the playbook when the guidance is:

- reusable across multiple projects or workflow arcs
- specific enough to tell people how to act, not just what was observed
- stable enough that the core rule is unlikely to churn immediately
- validated by real use, review, or repeated successful application
- scoped so the playbook receives the rule, pattern, or checklist rather than
  project-specific residue

If the content is still mostly retrospective detail, raw examples, or local
context, keep refining it in notes instead of promoting it early.

## Promotion Flow

Use this general sequence:

1. Capture the emerging pattern in notes while the work is fresh.
2. Tighten the wording until the guidance is reusable and actionable.
3. Promote the reusable rule into the playbook as the canonical version.
4. Update or trim the notes so they no longer compete with the promoted source.

Promotion should move the durable guidance, not copy the entire notes history.

## Cleanup Expectation

After promotion lands, clean up the notes repository so it converges on the
playbook as the source of truth.

- remove notes that are fully superseded by the promoted playbook guidance
- trim notes that still need to retain local context, examples, or history
- add or keep links that point readers to the canonical playbook location
- rerun the alignment pass until the remaining notes serve only a staging-layer
  purpose

Use the notes cleanup lifecycle in
[`playbook-integrity-check.md`](playbook-integrity-check.md) and the
[`Notes vs Playbook Alignment Audit`](prompts.md#notes-vs-playbook-alignment-audit)
prompt in [`prompts.md`](prompts.md) for the cleanup pass.

## Guardrails

- Do not promote project-specific implementation details into the playbook.
- Do not leave conflicting copies of the same rule active in both places.
- Do not treat a notes repository as permanent storage for already-promoted
  canonical guidance.

The healthy steady state is simple: notes stay useful as staging, and the
playbook stays authoritative once promotion is complete.
