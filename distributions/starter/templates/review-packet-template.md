# Review Packet Template

Use this template to make human review faster and more grounded. Canonical
review packet guidance for this environment starts in
`[local-playbook]/docs/review-packet.md`.

## Decision Requested

What exact human judgment or approval is needed?

## Reviewed Artifact, Commit, Or Byte Identity

Name the exact reviewed artifact and immutable identity. Link the complete diff,
evidence, validation output, and discussion rather than replacing them with this
summary.

## Objective

What was this change meant to accomplish?

## Scope

What changed?

## Explicit Non-Scope

What intentionally did not change?

## Invariants And Guarantees

What must remain true if the decision is approved?

## Exceptions

List known deviations, exclusions, and unresolved cases.

## Interaction Mode

Implementation, review/audit, or orchestration/prompt-authoring.

## Source Evidence

List the repository files, issue or PR links, docs, commands, logs, or other
authoritative sources inspected.

## Validation

Name the validation class under the canonical playbook taxonomy, list commands
run and results, and keep semantic review distinct from deterministic checks.
If validation is unavailable or incomplete, say so directly.

## Authority Consumed

What authority allowed the reviewed work to be prepared?

## Authority Granted

What authority did the human decision grant? Leave this pending until the
authorized human records the decision; an execution system must not infer or
author approval.

## Prohibited Or Unauthorized Next Stages

What actions remain outside the granted authority?

## Exact Next Permitted Action

What one bounded action may happen next?

## Risks And Unknowns

Name remaining risks, assumptions, follow-up decisions, or gaps between local
validation and real-world behavior.

## Review Effort Evidence (Optional)

When it helps improve a repeated workflow, note what the human had to inspect
or where decision-oriented context reduced review burden. Do not turn this into
a required metric or gate.

## Recommendation

Choose one and explain briefly:

- ready to merge
- needs decision
- blocked
