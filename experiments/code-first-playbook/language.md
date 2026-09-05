# Bounded language and evidence contract

`playbook-semantics/0` is a closed experimental profile over the pure Python
PyYAML 6.0.3 event/node parser. It is not general YAML conformance or an
executable policy language. Semantic owners are `startup` and
`source-retrieval`; the latter explicitly imports the former's vocabulary.
There are six baseline rules and no decompositions. Frozen evaluation bundles
select the same six identities, not additional simultaneous rules.

## Authoring

Each YAML file has `language`, `module`, `owner`, `imports`, and `records`.
Every record has an ID, kind, semantic owner, status, and explicit references.
The six record kinds are source, term, fact, action, rule, and context. Unknown
fields fail. `compiler/model.py` owns the closed field/reference inventory.

Sources identify canonical external reads. Terms define finite Boolean or
string-enum domains. Facts declare questions, resolution class, evaluators,
sources, and context/time freshness. Actions define exact normative `does`,
typed parameters, and excluded guarantees. The action kinds behavior, boundary,
and evidence make ordering/completion references concrete without a verb registry.
Rules specify activation, typed consequence, requires/activates/overrides,
ordering, lifetime, failure or failure inheritance, completion evidence, and a
live external authority question. Context remains subordinate.

Conditions support `is`, `in`, `all`, `any`, and `not`, with finite declared
operands. Empty/unknown expressions fail, including unreachable branches.
The parser rejects duplicate/non-string keys, aliases/anchors, merge keys,
tags, interpolation, multiple documents, BOM, CR and NUL. Only lower-case
plain `true`/`false` are Boolean; ambiguous YAML spellings are rejected.
Definitions may be exact multiline strings. Files are bounded to 256 KiB,
YAML depth to 32, expression depth to 24, and finite analysis to 4,096 assignments.
Exceeding logical capacity yields conditional `analysis_incomplete`, never
inapplicability or a proof of consistency. The pilot rejects every request for
a complete executor contract.

## F1: observation envelopes

Declarations are separate from observations. An observation names the fact,
state, typed value, permitted evaluator, unchanged resolution class, basis,
exact task/attempt/repository/context, observed-at time, rationale and diagnostics.
Known, unknown, stale, unavailable and conflicting remain distinct. Missing
means unknown; incompatible duplicates retain all inputs as conflicting.
Judgment always remains unassigned for selection, even when confidently supplied
as known false. This applies to all condition sites and all three audiences.

Only known, current, scope-matching observed evidence with a separately bound
acquisition record can fix a finite variable. The CLI admits synthetic fixture
acquisitions only: their record and artifact bytes must match explicit hashes,
and their artifact ID must name the exact fixture path. The compiler does not
authenticate outside truth or operate an acquisition service. A synthetic
source-read observation proves neither source sufficiency nor application.

False-for-all-remaining-assignments proof may exclude a rule or conditional
edge. Its report includes qualified facts, evidence IDs, scope and as-of.
A required rule is retained even if independently inapplicable. External reads
remain visible; they are not satisfied by being named. Conditions governing
failure, lifetime and completion remain visible rather than being executed.
Permission is always `not_evaluated`; completion grants no authority.

## F2: diff

Normalized record values preserve normative scalar bytes and meaningful list
order. Mapping/serialization order alone is not a semantic change. Definitions,
authority, failure, activation, lifetime, references, owners and status changes
produce events. Reverse-reference traversal includes both old and new graphs.
Explicit declared references, not words appearing in prose, determine fan-out.
Definition impact defaults to unresolved. No synonym/equivalence inference,
severity assignment or approval is produced. Source relocation is separately
labeled provenance-only. Context changes remain labeled context-only even when
their placement affects the presentation of a dependent rule.

## F3: fixed rehearsal

`cases/authority-rehearsal.json` is nine fixed mock scenarios, not a runtime
state machine. The real clause serializer supplies complete recovery-unit
bodies and external owner boundaries. Exact body hashes, separate mock human
decisions, routing, retirement and one controlling owner are checked. Forward,
compiler rollback, semantic-content rollback, language inadequacy, reverse,
stale rejection, disclosed old-policy restoration and a new current recovery
body are exercised. No real source is retired or promoted.

## F4: rendering and reproducibility

One selected clause set feeds AI JSON, Operator/SRE cards and Support symptom
navigation. Presentation cannot select facts or alter normative values. Actual
serialized clause payloads are audited against the selected set. Relative
links inside inherited prose resolve against their semantic owner's source
path at the frozen prose revision; normative values remain unchanged. Every
clause also links to the exact semantic input commit.

Exact normative payloads may retain meaningful whitespace. Only Markdown's
trailing-space/multiple-blank rules are locally disabled inside each audited
payload; all other lint and semantic checks still apply. The ignored pilot
build/dependency directories are excluded from Markdown source discovery.

`provenance/input-commit.json` is produced by an explicit bind against Git object
bytes after input commit creation. It may include the two frozen evaluation
bundles. Generation verifies every selected working input against that binding;
it does not discover HEAD or fetch remote state. CI therefore needs no parent
commit checkout or remote compiler. The local bind check proves pinned links
resolve to the exact source bytes, and repeat checks preserve those identities.

Exactly six baseline outputs are committed. Generation writes only to a named
experiment-owned `.build/` destination. Check regenerates there and compares
the full independent expected output set, including extra/missing files and
hand edits even when the stored manifest is also edited. Checks never repair
tracked output. Semantic/context/compiler/renderer/profile/raw-input identities
remain distinct; the output manifest does not recursively hash itself.

Frozen block accounting and current source binding are separate. Ordinary
checks use attributed frozen blocks; source-check compares entire current prose
files. Drift blocks current pilot fidelity claims. Hypothetical evaluation
bundles are explicitly labeled as divergent and never claim baseline parity.

## Review and limitations

The 24 scenario expectations were frozen before results. They are synthetic
behavioral checks; parameterized corruption seeds are not independent live
trials. Structural success does not prove semantic fidelity, usable framing,
or practical benefit. See [evaluation.md](evaluation.md) for friction, missing
measurements and the human continuation decision. No test or review authorizes
adoption, inversion, scope expansion, merge or automatic removal.
