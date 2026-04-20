# Feature Lifecycle

The delivery lifecycle is:

1. Design
2. Contract tests
3. Implementation
4. Hardening
5. Release
6. Capture

Each phase should have a clear goal, a clear review surface, and a natural stopping point before the next phase begins.

Use [`alignment-checkpoints.md`](alignment-checkpoints.md) to decide when to pause or split work, and use [`review-packet.md`](review-packet.md) to prepare the review surface before merge or release.

## Phase Guidance

### Design

Define the intended behavior, constraints, risks, and acceptance shape. The goal is alignment, not code volume.

### Contract tests

Write or update the tests, checks, or examples that define what must be true. This anchors implementation to an explicit contract.

### Implementation

Build only what is needed to satisfy the contract. Keep feedback loops short and avoid mixing extra polish into the first pass.

### Hardening

Address edge cases, refactors, failure handling, review findings, and CI quality. This is where robustness catches up to correctness.

### Release

Prepare the work to ship with a clean review packet, validation evidence, and any final release checks. If the repo does not have a formal validation path yet, record the lightweight validation that was used instead.

### Capture

Record what should become reusable guidance before the next delivery arc starts.

## Branch And PR Rules

After each merged phase, start a new branch and PR for the next lifecycle phase. This keeps the review surface narrow and preserves clean checkpoints.

The expected pattern is:

1. Merge the current phase
2. Open a new branch for the next phase
3. Open a new PR for that phase
4. Complete post-release capture before starting the next major arc

Do not roll multiple lifecycle phases into one long-running branch unless there is a strong reason and the review surface remains clear.
