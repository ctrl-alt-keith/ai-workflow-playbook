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

## Working States

Use these states to keep capture, defer, repo action, and playbook promotion
separate:

- Raw notes: fresh capture, partial observations, and rough ideas that are not
  ready to guide action yet
- Deferred ideas: notes worth revisiting later, but still too broad,
  speculative, duplicated, or blocked to become repo work now
- Bounded repo issues: action-ready work for a specific repository with a clear
  scope, value, and acceptance shape
- Playbook candidates: validated lessons that may later become reusable
  cross-repo guidance after repo work proves the pattern

Do not treat these states as a conveyor belt where every note must advance.
Many notes should stay raw, many ideas should stay deferred, and only a narrow
subset should become repo issues or playbook guidance.

## Deferred Work Promotion

Promote deferred notes into GitHub issues only when at least one of the
following is true:

- the same friction, gap, or cleanup need shows up repeatedly
- the value is clear enough that repo-local action is justified now
- the work is ready to be scoped, assigned, and validated in a specific repo

Keep the item as a deferred idea when it is still mostly brainstorming,
duplicate with existing backlog items, blocked on outside decisions, or too
large to describe as one bounded change.

When promotion is justified:

- group related notes into one issue by theme instead of filing one issue per
  line item
- target the repository that would actually own the work
- write the issue so it can be completed in a focused PR or short arc
- include acceptance criteria that show what done looks like

Do not create issues for every interesting thought immediately. Use notes for
capture, use deferred ideas for backlog staging, and create repo issues only
when the work is concrete enough to support action.

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
2. Defer, group, or trim ideas that are not ready for action yet.
3. Promote only action-ready, repo-local work into bounded repository issues.
4. Tighten validated reusable guidance until it is ready for the playbook.
5. Promote the reusable rule into the playbook as the canonical version.
6. Update or trim the notes so they no longer compete with the promoted source.

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
