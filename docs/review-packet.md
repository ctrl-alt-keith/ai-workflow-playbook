# Review Packet

Before merge or release, prepare a standard review packet for the human reviewer.

## Packet Format

The packet should include:

- Objective: what this phase was meant to accomplish
- Scope: what changed and what intentionally did not
- Contract: the tests, checks, or acceptance criteria that define correctness
- Validation: what was run and what the results were
- Risks: remaining concerns, edge cases, or follow-up work
- Review focus: where the human reviewer should spend attention

## What Codex Should Summarize

Codex should summarize:

- the purpose of the change
- the key files or surfaces affected
- the validation evidence
- the most important tradeoffs made
- any known weak spots or unresolved questions

The goal is not to restate the diff line by line. The goal is to make human review targeted and efficient.

## What The Human Should Focus On

The human reviewer should focus on:

- whether the phase objective was actually met
- whether the contract is correct, not just passing
- whether risks are understood and acceptable
- whether the change is appropriately scoped for the phase
- whether the work is ready to merge or release

Human review is for judgment, prioritization, and standards enforcement. It should not be wasted on reconstructing context that the review packet should have provided.
