# Experimental semantic projection pilot

This CAK-232 experiment describes eight existing Playbook units for read-only
repository design analysis. It is a reviewed-interpretation candidate, not
accepted doctrine, a startup replacement, or a live executor integration.
Current Markdown remains authoritative and every existing mandatory read stays
mandatory. No adapter, router, permission, lifecycle, or promotion behavior is
changed by this directory.

## Representation and ownership

The semantic input is [pilot.json](pilot.json): rules, terms, exact source
references and one consumer profile. Coverage classifications and evaluation
cases are review annotations. They do not infer policy. The
[validator](../../scripts/projection_pilot.py) checks this limited contract and
prints a deterministic analysis bundle. Generated manifests, selections,
coverage diffs and diagnostics are replaceable evidence with zero authority.

A sidecar keeps source prose untouched and makes removal straightforward. It
also makes drift possible: a matching digest proves byte binding, not correct
interpretation. Each source binds a repository path, full-document SHA-256 and
source revision. Each pilot section additionally binds an exact unique heading,
section hash and complete ordered block inventory. Block line ranges navigate
the recorded revision; block hashes bind the clauses. Canonical text is not
copied into a second doctrine corpus. Review the source at its recorded revision
alongside the candidate interpretation.

The small executable here demonstrates the proposed contracts only. It has no
network, executor, mutation or LLM compilation step. A future production compiler
or consumer integration needs its own scope and ownership decision. This pilot
does not adopt a compiler architecture or change repository boundaries.

## Eight units and coverage boundary

| Unit ID (prefixed `pb.`) | Exact source section | Candidate meaning |
| --- | --- | --- |
| `startup-floor` | [Required Repository Startup Contract](../start-here.md#required-repository-startup-contract) | Controller establishes the floor and applies activated owners before dependent action. |
| `conditional-activation` | [Conditional Repository Guidance](../start-here.md#conditional-repository-guidance) | Actual task triggers select specialized owners; narrower owners still control. |
| `mode-persistence` | [Required Repository Invariants](../start-here.md#required-repository-invariants) | Conventions persist; material changes refresh required sources. |
| `retrieval-triggers` | [Triggers](../source-first-retrieval.md#triggers) | Classify mandatory, optional and ambiguous retrieval before continuity. |
| `claim-verification` | [Verification Gate](../source-first-retrieval.md#verification-gate) | Evidence is claim-specific; preserve verified, partial, blocked and unknown states. |
| `retrieval-recovery` | [Recovery](../source-first-retrieval.md#recovery) | Perform available retrieval and correct assumptions before conversational repair. |
| `interaction-mode` | [Interaction Mode Preflight](../repo-readiness.md#interaction-mode-preflight) | Resolve the human's bounded deliverable before implementation actions. |
| `action-latch` | [Interaction-mode action eligibility latch](../repo-readiness.md#interaction-mode-action-eligibility-latch) | New narrower direction invalidates incompatible pending actions. |

The ledger covers every block in these eight sections, including headings,
supporting examples and normative clauses outside a unit's projected subset.
Sections end at the next ATX heading, including a subheading. This is a closed
pilot parser contract, not a general Markdown parser; fenced sections are
unsupported. Paragraphs and top-level list items form separate blocks; list
continuations remain attached. A new paragraph or list item must appear in the
coverage diff even if all old mapped blocks are intact. Whole-document hashes
also flag additions outside those sections for source review.

Every block is `normative`, `supporting` or `unresolved`. Normative clauses name
candidate rule IDs or explicit unprojected `canonical_reads`. Supporting and
unresolved blocks cannot supply normative rules; unresolved blocks require a
canonical read. All other sections and referenced owners remain unprojected.
In particular, the remaining repository invariants and the prompt completeness
and shared-policy-placement paragraphs are explicit unprojected reads. The
floor's detailed adapter choices, family alignment, instruction hierarchy and
task-routing taxonomy still require their canonical source contracts.

Eight units are deliberately incomplete. `complete: false` is mandatory for
this experiment even when every pilot block has been accounted for. Accounting
coverage is not semantic equivalence, complete startup closure, or adoption.

## Input contract

IDs are stable within a record class and unique across rules, terms and sources.
Do not recycle retired IDs. A move preserves the ID and changes its source
binding after review. Retire a rule explicitly with `status: retired`; optionally
name a distinct existing `superseded_by` rule. Active dependencies must be
retargeted explicitly. The selector never silently redirects them. Source Git
revisions track changes; there is no per-rule version counter.

| Record/field | Meaning |
| --- | --- |
| Rule `kind` | One of `invariant`, `trigger`, `requirement`, `prohibition`, `authority`, `fallback`, `completion_boundary`; kind alone does not mean always active. |
| Rule `source`, `owner` | Exact source reference and canonical owner for one bounded question. |
| Rule `when` | Typed applicability predicate; judgment-heavy facts must be externally established from their named owners. |
| Rule `consequence` | Typed constraint: kind, effect term, value and reviewable normative meaning. It reports an obligation, prohibition, routing requirement, authority-source check, completion condition or persistence constraint. |
| Rule `dependencies` | Typed source/rule relationships, with source-backed conditional scope where applicable. |
| Rule `persistence` | Start event, retained meaning and typed termination/invalidation condition; no runtime state is stored or changed. |
| Rule `failure` | Explicit condition, affected operation, response and canonical fallback sources, or specific inheritance/unresolved status. |
| Rule `execution_qualified` | All pilot rules are false. Structural checks can reject hypothetical qualified rules but never grant live qualification. |
| Rule `validation` | Supporting evaluation-case IDs; not proof that a model or executor passed those cases. |
| Rule `interpretation`, `supporting_sources` | Review rationale and context, separated from the normative consequence. |
| Term | Stable ID, fact/effect role, Boolean or closed enum domain, source and definition. |
| Source | Exact repository path, Git revision and SHA-256; selected sources add section/coverage bindings. |
| Consumer | One schema version, required supported capabilities, explicit canonical reads, `read_only_design` mode and `live_consumption: false`. |

Effect terms denote single-valued constraints within their declared meaning.
Different target terms are not presumed independent in natural language:
review must detect semantic aliases and cross-term contradictions. The
mechanical overlap check finds different typed consequences for the same effect
term. It reports matching consequences as possible duplication and never merges
them automatically. No document position, depth, proximity or global priority
number establishes precedence.

## Conditions and unknowns

The only predicate forms are `eq: [term, value]`, `in: [term, values]`,
`present: term`, `all: [conditions]`, `any: [conditions]` and `not: condition`.
Operands must match the declared finite type exactly; Boolean and integer are
not interchangeable. Arbitrary expressions, code, empty conjunctions and
unknown operators are rejected, including inside unreachable branches.

An omitted context key is unknown. Explicit JSON `null` means known absence;
it is not a Boolean false value. Presence of a false Boolean is still true.
Equality/membership against known absence is false. `not unknown` is unknown;
false dominates `all`, true dominates `any`; otherwise an unknown operand keeps
the result unknown. Unknown applicability retains the potentially applicable
rule and reports the missing fact. A false rule may still be retained as an
explicit dependency, with that reason and its original activation state shown.

Predicates are not judgments. For example, `source_available` means at least
one *permitted, qualified authoritative* route remains available. A rejected
transport does not establish that the source is unavailable. Similarly,
`feature_delivery_current` is determined by the lifecycle owner's narrower
activation boundary, not by the appearance of a feature-related noun.

The finite proof checks enumerate declared domains and known absence. They
reject mechanically impossible activation predicates and unresolved overlaps.
The 4,096-assignment bound is explicit: an input beyond that bound is outside
this demonstrator's supported capability, not proven safe. This mechanism does
not prove that supplied facts are true or that a prose mapping is exhaustive.

## Relationships, authority and failure

| Relationship | Contract |
| --- | --- |
| `requires` | Prerequisite rule or canonical read; preserve dependency closure even when independent activation is false/unknown. |
| `activates` | Another rule or source becomes relevant under its optional typed condition; false does not activate, unknown is retained conservatively. |
| `before` | Ordering constraint between rules; combine with prerequisites to reject ordering cycles. |
| `overrides` | Direct exception for the same bounded question, with source, scope condition and reviewed justification. |
| `refers_to` | Supporting reference, not an activation/prerequisite; ordinary reference cycles are allowed. |

Precedence edges must cover the entire incompatible overlap. The demonstrator
checks direct overrides only and rejects precedence cycles. It does not infer
transitive precedence or mathematical specificity from prose. It retains both
sides for review rather than deleting a rule or emitting a winning permission.
Scope containment that depends on human interpretation remains a review claim.

Authority rules must identify an external source and required checks, with an
`authority_source` consequence. No predicate, selected rule, successful check,
manifest or rendered bundle means permission. The bundle explicitly states
`permission: not_evaluated`. The eight units do not include a separate authority
unit; a synthetic fixture exercises this record kind without expanding the
pilot source scope.

Failure modes are `defined`, `inherited`, `not_applicable` or `unresolved`.
Defined failure needs a typed condition, operation and response. Inheritance
must name a specific rule and operation and terminate without cycles. The
demonstrator conservatively requires a resolved defined failure for any
hypothetical `execution_qualified` rule. Non-applicability requires a reason;
unresolved failure remains visible and cannot qualify live behavior. Review
must still establish whether the inherited failure applies to this operation.

## Validation and use

Run from the repository worktree:

```sh
make check
make projection-check
make projection-coverage
make projection-render
```

`make check` remains canonical Markdown and unit-test validation. The new tests
exercise machine-consumed contracts and source-drift fixtures through the
repository's actual demonstrator. They do not freeze canonical Markdown prose.
Source freshness is an opt-in experiment check, not a new general merge or
startup gate. A future ordinary prose edit may invalidate this pilot without
being blocked by its snapshots; invalid output must not be used even for a
claimed current analysis.

The projection targets print results only. A custom offline context can be
passed as a JSON file with `--facts` to the render command; absent facts remain
unknown. Successful render binds source references, exact sidecar and validator
hashes, schema, profile, context hash and selection digest. Wall-clock timestamps
are omitted. Identical bytes and context produce identical output. Source drift
invalidates check/render; `projection-coverage` reports drift for review and does
not regenerate or accept mappings.

For a source update, inspect `projection-coverage`, compare the old Git source
revision to the proposed source, classify every changed/new block, revise the
small affected interpretation and explicit reads, update bindings, and review
the semantic delta. Compare applicability, qualifiers, exceptions, owner,
ordering, consequence, persistence and failure separately. A new hash must
never automatically bless the interpretation. There is intentionally no
auto-rebind or auto-merge command.

Validation covers duplicate IDs, missing references, unknown kinds and terms,
typed conditions, dependency targets, impossible predicates, overlapping
incompatible effects, prerequisite/precedence/failure cycles, failure
qualification, source binding and complete block coverage, deterministic
rendering, consumer capability and false-completeness claims. Structural
success still cannot establish semantic equivalence or runtime safety.

## Evaluation boundary

The sidecar's cases define expected observable behavior from canonical owners.
Unit tests simulate selected predicate/selection boundaries; they do not show
that an AI followed the full workflow. In the bootstrap case, the required
source exists, raw API access is disallowed, and an approved connector succeeds:
the expected action is qualified retrieval, not a premature stop. With no
permitted route, the affected workflow remains blocked. Never interpret this
case as authorization to evade a policy denial.

Before any consumer trial, fix a paired canonical/projection/combined evaluation
with the same model, effort, facts, tools and source revisions. Score observed
retrievals, attempted actions, omissions and decisions against held-out cases;
keep supporting rationale out of the normative score. Include ordinary
continuation, material change, repository change, narrowed action eligibility,
partial verification, stale summaries, scoped precedence, unknown facts,
source additions and unavailable routes.

The design proposed zero observed critical violations, 30% relative reduction
in noncritical contract errors, no increase in unnecessary retrieval/intervention,
20% improvement in median context size or latency, and under ten additional
minutes of maintenance per changed clause. These are unaccepted experimental
decision criteria, not adoption gates created by this PR. No model comparison,
reliability gain or maintenance-cost result is claimed here. Follow current
human review and promotion requirements before any adoption changes required
reads, authority, lifecycle obligations or architecture.
