# Review Packet

Before merge or release, prepare a standard review packet for the human reviewer.

Use this packet at the release point described in [`feature-lifecycle.md`](feature-lifecycle.md), and use [`alignment-checkpoints.md`](alignment-checkpoints.md) when deciding whether a pre-merge sanity check is needed.

## Packet Format

The packet should include:

- Objective: what this phase was meant to accomplish
- Scope: what changed and what intentionally did not
- Validation: what was run and what the results were
- Risks: remaining concerns, edge cases, or follow-up work
- Recommendation: `ready to merge`, `needs decision`, or `blocked`

## What Codex Should Summarize

Codex should summarize:

- the objective
- the actual scope
- the validation evidence
- the main risks
- an explicit recommendation: `ready to merge`, `needs decision`, or `blocked`

The goal is not to restate the diff line by line. The goal is to make human review targeted and efficient.

If the repo does not have a formal validation path yet, say that directly and summarize the lightweight validation that was used.

## What The Human Should Focus On

The human reviewer should focus on:

- whether the phase objective was actually met
- whether the validation and acceptance criteria are correct, not just passing
- whether risks are understood and acceptable
- whether the change is appropriately scoped for the phase
- whether the work is ready to merge or release

Human review is for judgment, prioritization, and standards enforcement. It should not be wasted on reconstructing context that the review packet should have provided.
