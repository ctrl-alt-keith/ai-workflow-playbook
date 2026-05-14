# Trust Topology

Optional reference for describing how much confidence a reusable workflow
pattern has earned and what evidence supports that confidence.

This is not a required workflow step, metadata schema, promotion track, or gate.
If a pattern is already clearly evidence-supported, keep moving.

## Purpose

Use this vocabulary only when confidence is otherwise unclear:

- trust level: how settled the pattern is
- evidence: what proves the pattern works

Do not use this vocabulary to promote speculative ideas. The playbook remains
reusable, source-first, evidence-supported, and non-speculative.

## Trust Levels

- `weak`: plausible, but supported by little evidence.
- `emerging`: useful more than once, but its boundary is still unclear.
- `strong`: repeatedly useful across repositories, phases, or reviewers.
- `canonical`: settled reusable guidance that belongs in the playbook.

## Evidence

Evidence is the reason a pattern deserves its current trust level. Prefer direct
evidence over preference or memory.

Useful evidence includes:

- PRs that used the pattern successfully
- validation runs such as `make check`, tests, CI, or manual verification
- repeated usage across more than one repo, arc, reviewer, or delivery phase
- review feedback showing the pattern made inspection easier

Weak evidence includes:

- a single anecdote without a merged result
- a pattern that sounds right but has not been tried
- copied guidance from another context that has not been supported by local
  evidence
- broad claims without examples

Evidence does not need a formal schema. A short note, PR link, review packet, or
capture entry is enough when it lets a later reader understand why trust was
assigned.

## Promotion Guidance

Promote only when a pattern is reusable, evidence-supported, non-speculative,
and clear enough to guide action in the destination layer.

When moving a pattern into the playbook:

- keep only the reusable part
- include enough context to apply it
- remove project-specific detail
- avoid adding tracking requirements unless they already exist
- validate the docs change through the repo's normal check path

## Demotion Guidance

Demote or revise a pattern when evidence no longer supports its trust level.

Reasons to demote include:

- repeated exceptions show the rule is too broad
- reviewers find the guidance confusing or costly
- validation gaps were hidden by a too-confident summary
- the pattern only works in one repository or tool context
- newer canonical guidance makes the pattern redundant

Demotion does not have to mean deletion. A canonical rule may become strong
guidance with narrower wording. An emerging pattern may move back to notes while
more evidence is gathered. Weak patterns can be trimmed when they are no longer
useful.

## Background and Further Reading

This model is informed by broader ideas about trust as a networked property
rather than a binary state.

- Michael Roth, ["Trust Topology"](https://michael.roth.rocks/research/trust-topology/)
