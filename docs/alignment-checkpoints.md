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

## New Branch And PR Required When

A new branch and PR are required when:

- the current phase has merged and the next phase begins
- release is complete and post-release capture starts
- the work changes from delivery to reusable playbook capture
- the review audience or decision surface changes materially

The default should be smaller, phase-shaped branches rather than one branch that tries to carry the whole story.
