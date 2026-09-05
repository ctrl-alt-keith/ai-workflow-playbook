# Recovery: one semantic-authored section

Readers open [Source-First Retrieval: Recovery](../../../docs/source-first-retrieval.md#recovery).
Authors edit `action.retrieval-recovery/does` in
[the semantic source](../semantics/source-retrieval.yaml), owned by
`pb.retrieval-recovery`. Only this body is generated; its heading, stable
`#recovery` target and surrounding document retain their normal placement.

## Ownership and implementation boundary

[PR #407](https://github.com/ctrl-alt-keith/ai-workflow-playbook/pull/407)
proved the replacement candidate, integrated at
`4219234c924d5bc519303a259e7017d9dbedc7db`. The human then explicitly authorized
this bounded implementation and a new PR under CAK-235. The implementation
changes the canonical section owner, so it is a **material doctrine transition:
cross-boundary contract**. The exact implementation head is the later review
and promotion surface. Implementation is authorized; independent-review launch,
doctrine promotion and merge remain pending separate human authorization.
The predecessor's [review disposition](review-disposition.md) concerns its
shadow candidate only and does not qualify this transition.

The [repo-local carve-out](../../../AGENTS.md#recovery-generated-section-ownership)
separates permanent Recovery ownership from the still-experimental CAK-233
infrastructure and its unchanged expiry. The shared semantic modules and
compiler stay in their existing location to avoid a duplicate compiler or a
broader infrastructure extraction. No other section or persona output is
adopted. Pilot removal must preserve these operational dependencies or undergo
a separately authorized reverse transition.

The source identifier `source.retrieval` continues to identify the surrounding
Source-First Retrieval owner. The precise author/reader direction is declared
in [contract.json](contract.json), validated by
[the section boundary](../compiler/recovery_section.py), and recorded in the
[source bindings](../provenance/sources.json). The body has one authoring source;
these mappings contain identities and hashes, not another normative body.

## Generation and authoring

From the owning worktree:

```sh
make code-first-setup
make code-first-recovery-render
make check
make code-first-recovery-source-check
```

The fixed [renderer](../recovery.py) uses the existing restricted parser and
validator. It emits the action body with only list-spacing normalization.
There is no LLM, new semantic-language construct, audience selector or
compiler-field appendix. One concise source link and two invisible boundary
comments distinguish generated content. The rest of the Markdown file is
preserved byte-for-byte during explicit generation.

`make check` checks the actual reader section and
[engineering provenance](generated/provenance.json) against freshly computed
bytes. A direct prose edit fails with `stale_or_hand_edited` and the semantic
source and generation command. Validation does not repair or silently overwrite
that edit. Missing or duplicate section boundaries also fail. Explicit rendering
updates only the marked body and provenance; damaged boundaries must first be
restored. A second shadow Recovery reader is no longer generated or admitted.

The provenance records declared semantic/compiler/contract input hashes and the
generated section's byte identity. It deliberately excludes the hand-maintained
document shell from the generated-output identity. Git and the delivery PR bind
the exact implementation; successful generation grants no authority.

Recovery's old mapped prose blocks have been removed from active binding
accounting. Its original prose revision/hash remain historical provenance only.
For all units sharing Source-First Retrieval, current binding checks hash the
surrounding document with only the Recovery body excluded. Other source files
retain their whole-file checks. Recovery itself must match its semantic source,
so an author never refreshes historical prose parity to change this body.

The existing persona checks still require their exact input-commit binding and
explicit preview refresh when shared inputs change. Those previews are evidence
only, not extra Recovery owners. This retained pilot maintenance is a known cost;
its removal or redesign is outside this transition.

## Semantic changes and surrounding owners

The 15-record compatibility guard covers `pb.retrieval-recovery` and its outgoing
referenced envelope, excluding only the rendered `action.retrieval-recovery/does`
field. Another rule is guarded at its boundary but its complete execution graph
is not traversed. Unknown judgments are not resolved or used to prune the body.
Unrendered authority, failure, lifetime, precedence, vocabulary and mapping
changes reject generation until their effect is explicitly reviewed. Do not
refresh the guard automatically to silence a failure.

Source selection, permitted transport, verification, precedence, live action
authority and judgment sufficiency remain owned by Source-First Retrieval,
Start Here, Repo Readiness and the executor adapters. This section is not a
complete executor contract.

New incoming references or changes elsewhere in the corpus are outside the
focused guard. Review the shared semantic diff of the complete old/new corpus,
as well as the generated prose diff; incoming semantics can matter even when
Recovery's rendered bytes do not change. The shared diff preserves changed
records, reference sites, affected rules and unresolved semantic impact. It
also names `docs/source-first-retrieval.md#recovery` for affected Recovery rules.
No claim of incoming-edge completeness is made by the focused guard.

`make code-first-recovery-diff` demonstrates a hypothetical meaningful action
edit through that shared diff. It changes no source. Actual bundle comparisons
use `pilot.py diff --old-bundle ... --bundle ...`, as documented in
[language.md](../language.md#f2-diff). Tests also edit the real semantic file in an
isolated fixture, regenerate the reader and show that no old prose parity is
needed. Review both semantic and reader changes before accepting new meaning.

## Exact cutover and rollback

At a clean committed implementation head, with the current pre-transition main:

```sh
make code-first-recovery-rehearse RECOVERY_BASE=origin/main
```

[The rehearsal](../recovery_transition.py) resolves exact base/head identities,
checks the current generated section, proves the action and 144-word meaning
are unchanged, checks surrounding bytes and the old/new ownership bindings,
and verifies that the old shadow reader is absent. It applies the exact binary
Git diff to an isolated repository-owned index initialized from the base. Its
resulting tree must equal the implementation tree. Applying that same diff in
reverse must restore the entire base tree exactly, including prose ownership,
source bindings, AGENTS, compiler, previews and Make targets. This exercises the
actual transition patch, not the predecessor's mock authority ledger. It changes
no live checkout, branch, provider or human authority.

To reverse this exact candidate under later explicit human authority, start a
dedicated rollback branch/worktree at the reviewed head and apply its exact
base-to-head patch with `git apply --reverse --index`, then validate and deliver
that atomic reversal as a PR. After a squash merge, the equivalent operation is
`git revert <verified-integrated-transition-commit>`. The delivery evidence binds
the precise pre-merge range; the eventual merge workflow must retrieve the
integrated commit rather than assuming it equals this head.

That reverse restores one hand-maintained prose owner and returns the semantic
body to shadow evidence, not dual authority. The historical body is eligible
only because this transition proves it preserves the same meaning. Later body
or overlapping contract changes invalidate this exact rollback qualification;
review the full then-current body and ownership, refresh the reverse rehearsal
and obtain the applicable human decision. Do not use an old generated copy to
restore old policy silently. Compiler-only or semantic-content rollback retains
semantic ownership and must still regenerate and validate its current reader.

## Reading cost and representational friction

The normative body remains the same **144 words**, in the same sequence, at the
same reader location. No appendix or extra navigation hop is required. The source
marker adds a small maintainer cue. Reading cost is unchanged apart from that cue;
no comprehension-time, authoring-effort or maintenance improvement is claimed.

| Observed edge | Handling and limit |
| --- | --- |
| Normative rationale, examples and unknowns | Existing action body already represents them; preserved verbatim after list spacing. |
| Reader navigation | Inline generation preserves the stable heading and surrounding reading flow. |
| Source link and provenance | One relative editor link; detailed hashes stay on engineering surfaces. |
| Mixed document ownership | Exact section boundary; generation preserves all surrounding bytes. |
| Historical parity | Retired for Recovery; external-owner freshness remains separately checked. |
| Unrendered normative envelope | Existing compatibility guard blocks drift; incoming changes still need corpus review. |
| Shared pilot dependencies | Retained in place with a narrow permanent permission; old preview rebinding still costs work. |
| Language pressure | No new construct required by this transition. New top-level headings or marker injection are rejected as outside the section contract. |

## Next governed review

No independent review is launched by this implementation run. The next human
decision is whether to authorize a bounded governed review of the exact PR head.
Recommended scope: changed ownership/reader/Make surfaces; this renderer,
section boundary and rehearsal; the shared parser/model/validator, provenance
and diff; the two semantic modules and source bindings; focused tests; current
surrounding owners; and required reviewer startup/authority guidance. Use
supplemental sources only for a concrete recorded gap.

Review one-source ownership, exact reader fidelity, boundary protection,
hand-edit behavior, unrendered and incoming semantics, pilot-expiry separation,
and the precise reverse operation. Require actual source attribution, capability
gaps, anchored findings and an explicit verdict. Preserve the complete review
and disposition substantive findings under the current governed-review contract.
Only after that boundary may the human promote and authorize merging the exact
reviewed transition.
