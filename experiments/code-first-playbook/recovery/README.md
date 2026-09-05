# CAK-235: one generated Recovery section

Decision surface: [read the replacement candidate](generated/recovery.md).
It is a candidate for **only** [Source-First Retrieval: Recovery](../../../docs/source-first-retrieval.md#recovery),
not the whole document or an executor contract. Existing prose remains
operationally canonical. This PR requests review of the candidate; adoption
requires the separate human transition below.

## Target and authority

The target was selected before implementation in CAK-235 comment
`89895ec3-ade7-41bd-bc63-ae8fca6a719d`, against main
`24453559a381301e9c222d1fd2303e4582f45b23` (merged PR #406).
Recovery already has an exact action definition in the six-unit CAK-233 corpus
and a unit-level rollback rehearsal. Its trigger list, five-step procedure and
uncertainty obligations need no new language. The startup floor reaches many
conditional owners; replacing the whole retrieval document would need broader
modeling. A clearly owned section is the smallest credible replacement scope.

The current human CAK-235 implementation request authorizes this one-view
successor and supersedes the predecessor's three-view-only restriction for
this task. It does not renew the predecessor's other work or adopt generated
doctrine. No AGENTS edit is included. The CAK-233 outputs remain unchanged
historical pilot evidence; their three audiences are not this MVP's interface.

## One source and one reader view

Edit `action.retrieval-recovery/does` in
[`semantics/source-retrieval.yaml`](../semantics/source-retrieval.yaml).
That definition is the sole authored body input for this candidate. The existing
module imports the shared startup vocabulary; there is one logical semantic
corpus, not a second independently maintained prose template.

The existing restricted parser, model validator, source bindings, definition
diff and rehearsal remain in use. The focused
[`recovery_candidate.py`](../recovery_candidate.py) emits the action body and
normalizes only list spacing. It does not consult live prose to generate the
body, interpret facts, select an audience, or use an LLM. The heading and
generated/source marker are presentation. Exact input hashes and the original
section binding live in [provenance.json](generated/provenance.json).

Counts: **one section, one existing action body, one owning rule, zero new
records, zero semantic-language extensions**. The shared corpus still contains
67 records and six rules. Fifteen existing records are guarded for this
section, including an external claim-verification rule boundary.

This is deliberately a projection of a normative prose-valued action, not a
claim that every sentence is a mechanically executable predicate. It proves
one-source publication for this section; it does not prove automatic semantic
equivalence or a generalized documentation platform.

## Envelope and failure boundaries

The section retains its existing surrounding owners. Source selection,
permitted transport, verification gates, precedence, live action authority,
and judgment sufficiency stay with Source-First Retrieval, Start Here,
Repo Readiness and the relevant executor adapter. The body preserves unknowns
and requires retrieval before correction/resumption. A section link does not
promise that those external rules have been read or applied.

[`contract.json`](contract.json) guards the existing rule and its referenced
definitions, excluding only the emitted action body. Unknown facts are never
resolved or used to prune this documentation. Changes to the rule's unrendered
fields and its referenced failure, authority, lifetime, precedence, context or
vocabulary definitions reject regeneration until the section mapping is
explicitly reviewed. New incoming edges from unguarded rules are outside this
guard; the shared semantic diff and corpus review remain necessary for them. The external
claim-verification rule is guarded at its boundary; its entire dependency
graph is not claimed as part of this section.

The guard is a reviewed compatibility lock, not another semantic source or
proof of completeness. It stores hashes, no substitute normative prose. Do not
refresh it automatically to make a check pass. Use the existing semantic diff
and inspect the affected owners first. A changed scope or meaning needs the
applicable review; a hash cannot supply that judgment.

## Authoring and checks

From the repository worktree:

```sh
make code-first-setup
make code-first-recovery-render
make check
make code-first-recovery-source-check
make code-first-recovery-diff
make code-first-rehearse
```

`make check` includes focused tests, the predecessor's committed-output check,
this candidate's exact two-file output check, Markdown lint and repository
tests. Checks detect missing, extra, stale and hand-edited candidate files;
they never repair the candidate. Explicit render updates only the two
committed candidate outputs. The source check additionally verifies all six
current prose bindings and exact Recovery body parity after list spacing.
Source freshness remains a separate readiness check, not a new gate on
unrelated prose maintenance.

`code-first-recovery-diff` is an explicitly hypothetical definition edit. It
exercises the existing semantic diff and adds this candidate's affected path
without relabeling the shared diff. The unchanged owning rule is reported as
affected even though the edit is in the action definition. For an actual
old/new semantic bundle comparison, use the existing `pilot.py diff`
interface described in [language.md](../language.md); retain its unresolved
semantic-impact classification and inspect the generated Markdown diff too.

During shadow operation, changing policy requires changing its current prose
owner and reviewing refreshed source bindings as well. That dual maintenance
is a temporary cost of evidence collection, not the intended adopted workflow.
Generation itself does not pull prose into the semantic source or accept drift.

## Evaluation and prose friction

The generated body is byte-identical to the 144-word original section after
removing the pilot's extra blank lines between list items. The visible heading
and marker add a small amount of navigation/status text. There is no appendix,
fact table, compiler field dump or persona selector. Reader procedure and order
are unchanged. Controller disposition: **reading cost acceptable for a section
candidate**, pending independent review and human judgment.

| Dimension | Observed evidence and limit |
| --- | --- |
| Semantic preservation | Exact section parity; external envelope unchanged and guarded. This does not prove the whole unit is self-contained. |
| Normal reading | Same 144-word body, same sequence; one marker. No claim of faster comprehension. |
| Authoring effort | Existing YAML block remains readable but requires regeneration; shadow parity and envelope review add work. No measured improvement. |
| Reviewer effort | Body and diff are small; reviewer must also inspect the explicit envelope boundary and compiler. No paired timing study. |
| Diff clarity | Definition edits are first-class events with affected-rule fan-out; prose diff remains directly inspectable. |
| Regeneration | Fixed output set and exact byte comparison; freshness check is separate. |
| Normal-file credibility | Credible as the normal Recovery section after an approved ownership/path transition; not ready for silent substitution today. |

| Prose edge | Concrete handling | Disposition |
| --- | --- | --- |
| URLs and external references | Recovery has no inline URLs. Marker links use paths correct for this candidate location. | Represented cleanly; moving output requires link review. |
| Rationale/background | The closing paragraph distinguishes acknowledgment from actual recovery. It remains normative action text. | Represented cleanly; not mislabeled as removable context. |
| Examples | The five triggering situations remain in the body in their original order. | Represented cleanly. |
| Troubleshooting | Failure when no permitted route remains belongs to surrounding retrieval/adapter owners. | Kept external with guarded definitions; no second troubleshooting schema. |
| Caveats/unknown state | Unverified assumptions and stated unknowns stay in the five-step procedure. | Represented cleanly. |
| Historical context | Predecessor and trial history live in this evaluation, not in the reader file. | Bounded contextual prose. |
| Navigation/onboarding | Candidate marker links to existing prose and the one edit source. | Bounded contextual prose. |
| Related reading | Surrounding owners remain linked from the source document and this contract. | Bounded contextual prose; no generated reading catalog. |
| Provider-specific notes | Raw API/connector recovery remains an external adapter boundary. | Deferred from the section; guarded, not deleted. |
| Representational pressure | Publishing one existing action body is sufficient. Envelope changes cannot be silently projected. | No concrete need for a new semantic construct. |

## Reversible transition plan

This PR does not perform these steps. The next human decision is whether this
exact reviewed section candidate merits a separately scoped authority-transition
PR. Merging this experiment alone would not change ownership.

1. Select the exact semantic/body identities and the normative scope: only
   Recovery, with its surrounding owners still explicit. Resolve any review
   findings and refresh mutable source bindings.
2. Authorize a bounded repo-local exception for the operational compiler and
   normal generated destination; the old pilot exception does not authorize
   live consumption or an indefinite runtime.
3. In one reviewed transition, make the semantic action the owner of this
   section, generate the normal reader file, replace the hand-maintained
   section with a link preserving `#recovery`, and update the section-specific
   source binding/ownership references and compatibility guard. Retire the
   experimental parity dependency on that hand-maintained section; retain
   checks for unchanged external owners. No dual active owner is permitted.
4. Review the generated marker, relative links, provenance, stale checks and
   actual routing diff at the exact transition head. Require a candidate-body
   forward/reverse rehearsal against that final routing and authority mapping.
   The existing nine-step CAK-233 rehearsal remains unit-level, simulation-only
   evidence; it does not qualify an unimplemented production cutover.
5. A compatible compiler rollback changes only compiler bytes. A content
   rollback changes the semantic source under the then-current authority and
   regenerates output; neither silently promotes a derivative.
6. To return to prose, independently review the full current section body and
   exact human decision, change routing atomically, and retire/tombstone the
   semantic section owner. A stale generated body is ineligible. Restoring old
   policy must be explicitly reviewed as an old-policy restoration.
7. For removal of this unadopted candidate, preserve issue evidence, then remove
   `recovery/`, `recovery_candidate.py`, its focused test and four Make targets,
   and remove only `code-first-recovery-check` from `check` dependencies. Run
   `make check`. The prior pilot, source prose and other targets remain intact.

## Bounded independent review

One qualified Claude Fable/High review is planned against the exact candidate
commit. Its source set is this candidate subtree/script/test and Makefile,
the two semantic modules, `compiler/`, `pilot.py`, `language.md`, the frozen
source bindings, the recovery rehearsal fixture, the canonical Recovery
section with its relevant surrounding owners, and the required reviewer
startup/authority guidance. Supplemental sources need a recorded concrete
reason; no broad adjacent-document exploration or persona re-review.

The reviewer must assess body fidelity, externally retained semantics, guard
coverage, determinism, links, reading cost and reversible ownership, and report
actual sources/capability gaps. A material architecture/safety defect stops
the task. Bounded corrections preserve the original review where applicable;
otherwise return incomplete/follow-up instead of an open-ended review loop.
Review and validation provide evidence only; the human owns adoption and merge.

The completed review and bounded clarification are recorded in
[review-disposition.md](review-disposition.md).
