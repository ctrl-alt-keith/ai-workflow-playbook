# Alignment Checkpoints

These checkpoints are the explicit version of the "back-channel glue" that keeps AI-assisted delivery coherent.

Use these checkpoints alongside [`feature-lifecycle.md`](feature-lifecycle.md) and [`review-packet.md`](review-packet.md).

## Pause When

Pause and realign when:

- scope changes materially
- the task crosses into a new lifecycle phase
- validation results conflict with the current plan
- the AI is about to make a non-obvious tradeoff
- the work starts looking reusable enough to capture

## Ask Whether Capture Is Needed

Ask whether capture is needed when:

- a pattern worked well more than once
- a repeated failure mode produced a useful guardrail
- a review habit clearly improved delivery quality
- release or post-release work exposed a reusable heuristic

Capture should happen before the next major arc, while context is still fresh.

## Optional Pre-Merge Sanity Check

Use a pre-merge sanity check when:

- the PR is large relative to the phase goal
- the change path was unusually twisty
- validation passed but confidence still feels soft
- the reviewer needs a compact re-baseline before approving

This check is optional, but useful when the branch technically passes while the narrative still feels fuzzy.

## Start A New Thread When

Start a new thread when:

- the work moves into a different lifecycle phase after merge
- the context window is carrying too much stale implementation detail
- the new task needs a clean brief and a fresh review surface
- capture work would otherwise be buried inside delivery chatter

## Split A Branch Or PR When

A semantic phase boundary retains any applicable review and authority boundary,
but it does not require a new branch or pull request. Keep one focused
implementation branch and pull request when the same change can carry a clear
review surface through its lifecycle. Required review or approval may apply to
the exact implementation identity in that pull request; a later semantic change
to the reviewed material requires renewed review.

Split into a new branch and pull request when:

- the current pull request has merged and a separately authorized change begins
- the human or a narrowly applicable workflow explicitly requires a separate
  delivery surface
- scope, ownership, validation, merge timing, revert strategy, or review
  audience differs enough to make the next change an independent deliverable

Do not split work merely because its lifecycle phase label changes.
