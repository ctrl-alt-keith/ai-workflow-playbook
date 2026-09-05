# Recovery semantic ownership support

This directory retains only the shared semantic compiler support required by
the generated [Recovery section](recovery/README.md). Recovery has one
semantic-authored body and one human reader surface; it does not introduce a
general generated-document platform or a new semantic-language construct.

## Current use

From the owning repository worktree, run:

```sh
make code-first-setup
make code-first-recovery-render
make check
make code-first-recovery-source-check
make code-first-recovery-diff
```

The parser, model, validator, semantic diff, source bindings and provenance
writer are shared dependencies of that one reader contract. They remain because
they protect deterministic generation, stale/hand-edit detection, source
freshness, semantic/prose diff visibility, and Recovery's explicit rollback
proof.

## Retired CAK-233 maintenance

CAK-238 retires the experimental AI, Operator/SRE and Support previews,
their committed outputs, input-commit rebinding and mock rehearsal ledger.
They had no operational reader, did not participate in Recovery ownership, and
duplicated guarantees now protected by the Recovery renderer and its exact
forward/reverse transition rehearsal. Historical CAK-233 evidence remains with
its governing issue; it is not an active regeneration obligation.

The virtual environment and build tree are ignored repository-owned state, not
durable evidence. No executor, router or automation consumes this directory.
