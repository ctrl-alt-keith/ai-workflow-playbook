# CAK-233 pilot evaluation record

Status: implementation evaluation in progress; no continuation or adoption
decision. Existing prose remains operationally canonical. Counts refer to
selected corpora: **six rules, six units, three audiences, two edit rounds**.
No decomposition and no excluded readiness rules were introduced.

## Two bounded edit rounds

The frozen hypothetical bundles are `cases/edit-round-1.json` and
`cases/edit-round-2.json`. They are evidence fixtures, not alternate operational
owners. Each selects exactly six rules. Round 2 starts from round 1.

| Round | Hypothetical edits | Controller edit/inspection interval | Compiler correction |
| --- | --- | --- | --- |
| 1 | Require material change for conditional activation; add the existing trigger-failure response as a recovery alternative; end convention persistence only on repository change. | 2026-09-05 05:17:12–05:18:05 UTC (53 seconds). | One diff-report correction: fixture file relocations were initially mislabeled as unresolved normative impact. |
| 2 | Change startup action to start-here-only; redefine the imported operation term; change supporting startup context. | 2026-09-05 05:18:05–05:18:20 UTC (15 seconds). | None required to encode or distinguish the three edits. |

These intervals measure the observed local edit-and-inspection phase only.
Prior design, script preparation, later rendering, independent review and
correction effort are excluded. They are **not** total author-plus-reviewer
times and cannot establish the <=120% cost or >=20% gain thresholds. One
controller performed both rounds, with substantial carryover knowledge.
No third authoring round is authorized by this pilot.

## Controller audience-task inspection

The controller inspected the actual generated human files after generation.
These are eight read-only mock task answers, not an independent consumer study
or a timing comparison. All eight answers stayed correct or explicitly unresolved.

| View/task | Answer from the actual projection | Evidence clause |
| --- | --- | --- |
| Operator: startup incomplete | Stop the affected operation and name the prerequisite; retrieval alone is insufficient. | `action.startup-floor-failure/does` |
| Operator: ordinary continuation | Reuse still-current sources; do not blanket-rehydrate ordinary follow-ups. | `action.mode-persistence/does` |
| Operator: raw route denied, approved connector available | Recover through the permitted qualified connector; no premature all-routes failure. | `action.retrieval-recovery-failure/does` |
| Operator: partial verification | Separate verified facts and unknowns; do not recommend from missing evidence. | `action.claim-verification-failure/does` |
| Support: work began without context | Symptom navigation reaches startup failure and the external authority question. Sufficiency is unresolved. | `pb.startup-floor/failure`, `pb.startup-floor/authority_ref` |
| Support: a summary is treated as current state | Symptom navigation reaches retrieval triggers; a summary does not supply current verification. | `action.retrieval-triggers/does` |
| Support: source lookup rejected | The source-lookup symptom reaches recovery and distinguishes available qualified recovery from no remaining permitted route. | `action.retrieval-recovery-failure/does` |
| Support: unclear specialized guidance | Preserve conditional owners and inspect their actual applicability; no definite activation from topic nouns. | `action.conditional-activation-failure/does` |

The two Support entry routes for summary-based answers and rejected lookups are
distinct symptom navigation, not new policy. Whether that navigation reduces
reader effort remains unmeasured. The long appendix is a concrete cost concern.

The controller identified all six intended edit effects from typed diffs:
activation, fallback, lifetime, action definition, imported term definition,
and context only. This is author inspection, not an independent blind score.
The first three edits changed rule records; the action edit leaves rule text
unchanged and affects startup plus persistence; the shared term affects all six
declared dependents. Context remains a separate non-normative event.

## Friction and could-not-model-cleanly ledger

| ID | Observation | Disposition |
| --- | --- | --- |
| FR-01 | Copying a bundle into a fixture path generated 64 relocation events alongside three real edits, initially with misleading normative fan-out. | Bounded reporting correction separates provenance-only movement. Full evidence retained; one compiler correction charged to round 1. |
| FR-02 | Source-read, startup adequacy, materiality and source availability cannot be collapsed into trusted Boolean status. | Preserve aggregate facts as external judgment. Synthetic exact-read evidence is distinct. No phrase classifier or trust opt-out. |
| FR-03 | Exact prose clauses make large vocabulary appendices. The human views may have a substantial reading cost even with symptom navigation. | Preserve fidelity; practicality remains unproven. Do not claim smaller text or faster operation. |
| FR-04 | Inherited prose includes relative links and surrounding context that do not transfer cleanly to another directory. | Source-relative links receive pinned owner backlinks. Extra examples/context/link enrichment remain deferred evidence, not new language constructs. |
| FR-05 | Natural-language definition edits cannot be proven equivalent by the finite predicate evaluator. | Report unresolved semantic impact and all declared dependents. Review required; no synonym engine. |
| FR-06 | A complete recovery-unit body is much larger than a Support symptom summary. | Rehearse with full normative body and external boundaries. The Support summary alone is ineligible for reversal. |
| FR-07 | The bounded fixtures and one controller do not supply a qualified paired performance baseline or independent consumer population. | Total author/reviewer time, equivalent prose-plus-sidecar timing and AI reliability benefit remain unmeasured. Do not infer benefit from script execution time. |
| FR-08 | Canonical lint initially inspected old ignored build previews and flagged whitespace in exact normative payloads. | Exclude only experiment build/dependency state; bound the two whitespace lint exemptions to audited payloads. Canonical validation then passed. |

## Acceptance and stop disposition

Safety requires zero unexplained normative omissions/inventions, judgment-driven
pruning, invented authority, ownership gaps, dual owners or generated-output
drift. All seeded definition changes must be visible with correct declared
impact. Support and Operator tasks must be correct or explicitly unresolved.
The independent implementation review and final validation still own their
respective evidence; this file is not a success certificate.

Worth continuing also requires a measured practical gain: at least 20% lower
median author/review or audience-task time, or at least two fewer noncritical
consumer errors with no new consequential error. Equal safety alone does not
satisfy this decision rule. No qualified practical-gain result is currently
available. A third edit round, a general schema extension, more than six units,
thirteen rules, internal readiness units, broader exception, or live consumer
would exceed the authorized pilot.

The paired AI consumption dimension is currently unmeasured; no 48-trial
reliability claim is made. Missing measurements must remain explicit in the PR
and durable evidence. The human must decide whether observed safety and friction
justify any separately scoped continuation; passing checks cannot make that
decision. No merge is authorized.
