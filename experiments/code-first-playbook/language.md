# Bounded Recovery semantic contract

`playbook-semantics/0` is a closed, restricted YAML profile. It is not an
executable policy language or a general document generator. The semantic owners
are `startup` and `source-retrieval`; the latter imports the former's
vocabulary. No new records or semantic constructs are introduced by Recovery.

Each semantic record has an ID, kind, owner, status and explicit references.
The permitted kinds are source, term, fact, action, rule and context. The
parser rejects duplicate or non-string keys, aliases, anchors, merge keys,
tags, interpolation, multiple documents, BOM, CR and NUL. The validator keeps
typed references, finite condition analysis, rule ordering and authority
boundaries explicit. Structural validity does not establish policy equivalence,
review completeness or authority.

## Semantic and reader impact

The shared diff compares normalized record values and both old/new reference
graphs. It reports changed records, direct reference sites, affected rules and
unresolved semantic impact. Incoming references remain a separate corpus-review
obligation.

The Recovery renderer owns the only generated reader mapping. Its contract maps
`action.retrieval-recovery/does` to
`docs/source-first-retrieval.md#recovery`. A meaningful edit to that clause
reports that reader output. A change to an unmapped clause reports no reader
surface rather than inventing one. Missing, duplicate, malformed or stale
Recovery mappings fail before rendering or reporting can silently omit them.

The mapping reports output effect; it does not prove semantic equivalence,
outgoing-envelope approval, incoming-dependency completeness or merge
readiness.

## Deterministic Recovery generation

Recovery renders only its marked body. Its generated provenance records the
semantic/compiler/contract input hashes and body byte identity, while source
bindings separately protect the hand-maintained surrounding document. Checks
do not repair generated prose. The exact forward/reverse transition rehearsal
continues to prove the approved recovery ownership transition and rollback
shape; it is independent of the retired preview simulation.
