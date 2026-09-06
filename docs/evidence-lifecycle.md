# Evidence Lifecycle

## Purpose

Use this guidance when a workflow accepts, integrates, synthesizes, or reports
evidence. It defines a general evidence lifecycle and semantic-accounting
boundary; it is not a mandatory ceremony for routine repository work.

For domain-specific acquisition, provenance, licensing, and retention of
external material, use
[`knowledge-ingestion-patterns.md`](knowledge-ingestion-patterns.md). For
comparative agent convergence and divergence, use
[`multi-agent-synthesis.md`](multi-agent-synthesis.md). Those owners remain
authoritative for their narrower domains.

## Accepted Evidence And Freeze

Accepted evidence is the reviewed input set eligible for integration and
synthesis. Acceptance records eligibility under the current contract; it does
not make every claim true, resolve every conflict, or grant authority for a
downstream decision.

Before integration, synthesis, or decision production, freeze the accepted set
at exact reviewable identities or versions. Preserve what was accepted,
rejected, or unresolved and the decision that established the boundary. Later
corrections or additions create an explicit new acceptance decision and a new
evidence boundary rather than silently rewriting the frozen set.

A freeze protects the reviewed input boundary. It does not freeze later
interpretation, imply permanent retention, require a particular manifest or
storage system, or prevent a documented correction.

## Governed Artifact Capture

Use governed-artifact capture only when all three parts of this candidate floor
hold:

1. the output is substantial rather than ordinary chat;
2. its exact identity is required for review, citation, disposition, decision,
   recovery, or another authorized downstream dependency; and
3. regeneration or conversation-only retention would weaken that downstream
   dependency.

Meeting the floor identifies a governed-artifact candidate only. It does not
authorize capture, retention, or a destination. Ordinary answers,
brainstorming, transient explanations, routine status, and outputs without an
exact downstream identity dependency remain ordinary chat. Routine work does
not inherit governed-artifact ceremony.

### Cross-thread-useful intermediate artifacts

Apply the same three-part candidate floor to intermediate documents. An
expected downstream consumer is a useful signal, but it is not sufficient by
itself: the material must also be substantial, need an exact identity for the
downstream dependency, and be lossy or meaningfully weaker if reconstructed
from conversation or regenerated.

Select preservation from the artifact's role and downstream value, not from
the executor or provider that produced it. A complete review output, analysis
package, finding-disposition input, implementation handoff, or temporary design
document can qualify when another thread, executor, reviewer, or later phase
needs its exact findings, constraints, instructions, or evidence. Apply this
symmetrically to cross-executor handoffs. Disposable scratch, conversational
scaffolding, redundant summaries, and easily regenerated notes with no exact
downstream dependency remain disposable.

After storage admission and successful capture, record the artifact's semantic
role and give downstream consumers compact context plus its exact durable
identity. Do not reproduce the complete body in chat, a pull-request comment,
or a planning-system comment merely to keep it available; an incidental
discussion surface does not become the durable artifact store through
convenience. If the qualified durable route is unavailable, apply the
[`mandatory capture failure boundary`](#mandatory-governed-artifact-capture-failure-boundary)
rather than degrading to copy and paste.

A failed or non-verdict review attempt may still qualify when its complete
output or failure evidence has an authorized downstream review, diagnosis, or
disposition role and storage admission permits retention. Preserve its failed
or non-verdict status and keep it distinct from a successful review artifact.
Preservation never makes an intermediate artifact accepted evidence, canonical
doctrine, an approved decision, completed work, or transition authority.

When the candidate is a rendered prompt intended for exact executor handoff,
also apply the narrower
[`issue-owned durable rendered-prompt handoff profile`](prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile).
That profile projects this candidate and storage-admission boundary onto prompt
delivery and attempt evidence; it does not create a second governed-artifact
owner or storage permission.

### Storage Admission

After candidate recognition and before retaining any bytes, apply the owning
storage contract. All applicable privacy, visibility, licensing, retention,
destination, and verification conditions must be affirmative. Prohibited or
uncertain retention fails closed; importance, materiality, or a
dependency-bearing role never permits retaining prohibited bytes.

A downstream workflow or storage owner may narrow permission for its boundary
without redefining the shared candidate floor. The owning storage contract,
not this lifecycle, selects concrete destinations and handles prohibited
content.

### Direct Durable Capture

After the candidate floor and all storage-admission conditions pass, capture
the complete artifact durably during the producing task. Use one writer, a
unique semantic dated or versioned target, and exclusive no-overwrite
creation. Before the write, freeze the exact local bytes and derive their size,
whole-file SHA-256, declared text format, final-newline state, and any qualified
provider checksum from those same bytes.

After creation, verify exact retention by raw-byte readback or by a qualified
provider-integrity comparison that binds authoritative object identity, stored
size, containment, and an officially documented provider checksum to the same
frozen local bytes. All required values must be present and match. Keep the
provider checksum distinct from whole-file SHA-256. When that comparison is
unavailable, incomplete, ambiguous, or unqualified, exact raw-byte readback
remains required. Freeze the successful path immediately.

Corrections use a new identity with explicit lineage; never edit the frozen
artifact in place. Artifact preservation does not by itself require Git, a
branch, a worktree, a commit, or a pull request.

Ordinary repository-owned temporary state may remain temporary. Once an
artifact is admitted, the owning durable destination controls, and
attempt-local scratch is not a substitute for required durable capture; see
[`repo-readiness.md`](repo-readiness.md#repo-local-workflow-state).

### Dropbox issue-folder creation projection

For an admitted Dropbox issue-owned artifact, inspect `/issues/<ISSUE-ID>/`
only when the artifact is ready to write; do not pre-create issue folders or
persist approval state. If the folder exists, continue the already-authorized
write without a folder-creation approval.

If the folder is absent, ask once to create exactly `/issues/<ISSUE-ID>/` and
continue the already-authorized upload. If that confirmation is unavailable,
including during unattended execution, or creation cannot proceed, fail closed
without silently rerouting storage.

Current connector action requirements remain [runtime evidence](start-here.md#connector-availability-is-runtime-evidence);
Playbook prose does not override them, and Airtable canonical-text handoffs do not depend on Dropbox folder existence.

### Producing Receipt And Compact Delivery

Every admitted production that writes an artifact leaves exactly one
producing-receipt record. The producing receipt is distinct from the artifact,
prompt or review attempt evidence, reviewer output, finding disposition, human
decision, and stage-boundary receipt.

Select the smallest permitted append-only surface sufficient for recovery. An
adequate append-only planning record may satisfy the role. Use a separate
immutable producing-receipt artifact when the planning surface is unavailable,
offline recovery is required, the receipt becomes dependency-bearing, the
receipt is too substantial for the planning surface, or the governing contract
requires it. When that separate receipt coexists with an available and
permitted planning surface, the planning record references the separate
receipt's exact identity.

The artifact body defines the receipt-selection policy. The producing receipt
records the surface actually used. A later receipt-surface change creates a
new receipt identity and never rewrites the artifact or an earlier receipt.

Record, as applicable:

- artifact role and semantic status;
- a safe durable locator;
- exact size and SHA-256;
- encoding, line endings, and final-newline state;
- exact integrity-verification route and result, including exact-byte read-back
  when that route was used, plus containment result;
- predecessor, review, disposition, supersession, or other lineage;
- retention and visibility classification when the owning storage contract
  requires them;
- material capability gaps;
- the zero-authority boundary; and
- the exact next permitted action or fail-closed stop.

Containment is a fail-closed operational projection of the named destination,
no-overwrite creation, immutable path, and no-escape guarantees. It does not
create a separate semantic owner. Retention and visibility are applicable
storage-contract evidence, not universal producing-receipt fields.

Reserve *producing receipt* for the selected durable append-only receipt
surface. Conversation is a compact summary or compact delivery surface, not a
durable producing-receipt surface. Do not reproduce the complete durable
artifact in chat merely for transport. Consistent with
[`Operator Observability`](core-model.md#operator-observability), compact
delivery does not require routine item-level success narration when the owning
durable evidence preserves the complete item results.

When evidence has a distinct identity, describe the operation as `evidenced
separately`; do not imply an independent actor merely because the evidence is
separate.

### Mandatory governed-artifact capture failure boundary

Apply the general failure semantics in
[`prompt-contracts.md#mandatory-failure-boundary`](prompt-contracts.md#mandatory-failure-boundary).
Fail before retaining bytes or claiming capture-dependent completion when:

- a required source or parent identity is missing, stale, ambiguous, or
  mismatched;
- retention is prohibited or uncertain;
- the owning workflow supplies no permitted durable destination;
- exact retention verification through either qualified route is unavailable;
- the target exists, collides, escapes containment, or creates overwrite risk;
- encoding, line endings, final-newline state, size, or digest mismatches; or
- available transport or storage weakens ownership, authority, evidence,
  privacy, retention, or identity guarantees.

A bounded failure receipt is allowed only when its contents and surface are
permitted. It must not contain prohibited bytes or claim capture, acceptance,
transition, completion, or authority.

Successful capture, hashes, timestamps, synchronization, validation, reviews,
receipts, and storage transfer zero authority. Capture success does not
authorize doctrine promotion, repository implementation, merge, release,
planning mutation, or downstream work.

## Independent Evaluation Dimensions

Evaluate protocol conformance separately from substantive value. A conforming
execution can produce low-value findings, while a nonconforming execution can
surface useful material that still requires separate review before use.

Substantive value does not excuse unsafe or unauthorized execution, and a
protocol failure does not require useful evidence to disappear. Preserve the
failure and any potentially useful material when the applicable security,
privacy, licensing, and retention rules permit, while keeping its acceptance
status explicit.

## Information-Preserving Integration

Integration should preserve the information needed for later synthesis and
review. Keep source and contributor identity, relevant intent, provenance,
constraints, conflicts, uncertainty, unsuccessful searches, and unresolved
questions visible. Do not make the integrated result appear cleaner by
silently harmonizing disagreement or dropping negative outcomes.

Integration organizes accepted evidence; it does not decide what the evidence
means or convert contributor conclusions into shared findings without review.

## Synthesis And Semantic Classes

Synthesis consumes the frozen accepted-evidence set. When the distinctions
matter, keep these semantic classes explicit:

- Observation: what an accepted source or execution directly reports.
- Interpretation: what the observation means within the stated context.
- Inference: reasoning that extends beyond what the evidence directly states.
- Recommendation: a proposed action or decision supported by evidence and any
  named inference.
- Open question: an unresolved point that remains outside the supported
  conclusion.

Inference and implications are legitimate synthesis outputs when they are
identified as such. Do not restate them as observations or evidence, and do not
require or preserve private reasoning traces to make the distinction.

## Semantic Accounting And Traceability

Keep a reviewable path from each material recommendation to its motivating
evidence, relevant conflicts or constraints, and any inference that connects
them. Traceability should be proportionate: a link, citation, section reference,
or artifact identity is enough when it lets a reviewer reconstruct the basis
without a separate database.

When multiple sources or outputs agree, distinguish independent corroboration
from convergence caused by a shared source, dependency, or reasoning path.
Shared-source convergence is not independent corroboration. Apply
[`multi-agent-synthesis.md#reading-convergence-and-divergence`](multi-agent-synthesis.md#reading-convergence-and-divergence)
for the interpretation of convergence, divergence, and dependencies rather
than creating a second scoring or voting model here.

## Negative And Null Evidence

A completed-search receipt and an explicit negative outcome are evidence of the
scope searched and the result observed under that scope. They are not proof
that a fact, source, or alternative does not exist outside it.

Preserve enough bounded context to understand what was checked and what the
negative outcome means. Carry unsuccessful searches, constrained findings,
conflicts, and unresolved questions through integration and synthesis when they
affect the conclusion. Do not turn them into factual negatives or retain them
indefinitely without an applicable preservation decision.

## Validation Boundary

Deterministic validation can establish declared mechanical properties such as
artifact identity, required structure, internal traceability, and completion
against an explicit set. It cannot establish substantive truth, significance,
approval, or decision authority.

Use [`repo-readiness.md#validation`](repo-readiness.md#validation) as the owner
of the validation taxonomy and gate behavior. Evidence workflows should name
what a check establishes without forking that taxonomy or substituting checks
for semantic judgment.

## Reporting

When a report contains multiple output classes, distinguish factual findings,
operational observations, recommendations, and open questions. Preserve the
observation, interpretation, inference, recommendation, and open-question
distinctions above wherever collapsing them would obscure the evidentiary
boundary.

Simple reports do not need a fixed taxonomy or template. The requirement is to
keep materially different classes visible and retain access to the complete
supporting artifacts rather than hiding them behind a polished summary.
