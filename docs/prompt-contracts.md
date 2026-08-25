# Prompt Contracts

## Purpose

This page defines the canonical semantic contract for material prompts that
must be reviewable, recoverable, or replayable. It separates meaning from
attempt selection, derived evidence, executor representation, delivery, and
live authority.

These semantics do not require an operational workflow engine, prompt
generator, state store, schema implementation, or lifecycle orchestrator. An
owning repository may implement those mechanics under its local contract, but
the implementation must preserve the boundaries defined here.

The current versioned machine-readable companion for new selections is
[`prompt-contract-semantic-anchors-v2.json`](prompt-contract-semantic-anchors-v2.json).
The historical
[`prompt-contract-semantic-anchors-v1.json`](prompt-contract-semantic-anchors-v1.json)
remains immutable for compatibility-major v1 consumers. Version 2 supersedes
version 1 for new compatible selection, but no consumer adopts the new major
implicitly; replay and historical consumers remain pinned to their recorded
major and exact bytes.
RFC 8785 conformance cases are in
[`prompt-contract-canonicalization-vectors-v1.json`](prompt-contract-canonicalization-vectors-v1.json).

## Semantic Layers

Keep these layers distinct:

| Layer | Responsibility |
| --- | --- |
| Semantic meaning | Immutable prompt-contract purpose, phase, mode, guarantees, compatibility, authority references, validation requirements, and expected evidence. |
| Selected attempt inputs | Exact sources and implementations selected once for a fresh attempt or resolved exactly for replay. |
| Derived evidence | Source manifest, hydrated context, validation results, digests, checkpoint lineage, and append-only attempt receipt. |
| Executor representation | Product-neutral requirements mapped by a representation adapter and emitted by a deterministic renderer. |
| Delivery | Deterministic selection from a declared ordered transport policy. |
| Live authority | Current safety policy and durable authorization re-read immediately before execution or adoption. |

No downstream layer may redefine an upstream layer. In particular, a
representation adapter changes expression, transport changes delivery, and a
receipt records evidence; none changes semantic meaning or grants authority.

## Artifact Classes And Identities

The durable artifact classes are:

- **immutable semantic prompt contract**: the pre-hydration, pre-render
  semantic meaning and requirements;
- **source manifest**: the ordered exact source references selected for one
  attempt;
- **hydrated context**: the bounded, typed projection derived from selected
  sources;
- **rendered prompt**: the exact executor-visible bytes emitted by a
  deterministic renderer;
- **attempt execution record / receipt**: append-only evidence referencing the
  contract and recording selected and derived identities; and
- **checkpoint**: a recovery pointer bound to the creating contract, attempt,
  inputs, evidence, and authority lineage.

Material implementations must keep distinct identities for:

- schema version;
- canonicalization scheme and version;
- semantic prompt contract;
- validation profile;
- validator;
- source manifest;
- authority source and durable state or receipt lineage;
- hydrator;
- hydrated context;
- representation adapter;
- renderer;
- rendered prompt;
- transport policy and actual transport selection;
- attempt and checkpoint; and
- runtime safety-policy observation.

An identity names one boundary only. A contract digest is not a rendered
prompt digest, a schema version is not an adapter version, and a transport
selection is not the transport policy.

## Immutable Contract Boundary

Create and hash the immutable semantic contract before hydration or rendering.
The contract may include:

- contract identity and semantic version;
- schema and canonicalization requirements;
- purpose, phase, and mode;
- compatibility constraints;
- source ownership classes and reference requirements;
- authority-source references and the non-authoritative asserted action;
- required capabilities and product-neutral reasoning class;
- validation-profile and validator requirements;
- hydrator, representation-adapter, and renderer requirements;
- preferred transport, ordered allowed fallbacks, prohibited transports, and
  retained transport invariants;
- required outputs and expected evidence; and
- mandatory fail-closed conditions.

The hashed contract body must not include:

- its own digest;
- a selected source-manifest digest;
- a hydrated-context digest;
- a rendered-prompt digest;
- the actual transport selection;
- validation results;
- execution results;
- checkpoint output; or
- runtime safety-policy identity.

An external envelope may pair the computed digest with the immutable contract
body. The digest is never part of its own hash input. Derived identities and
outcomes belong in the attempt receipt, not in the contract.

## Append-Only Attempt Receipt

The attempt execution record / receipt references the semantic-contract digest
and records the exact selections and derived evidence for the attempt. It
includes, as applicable:

- attempt and parent-attempt or checkpoint lineage;
- ordered source manifest and its digest;
- exact durable authority, state, approval, and reconciliation references;
- hydrated-context digest;
- rendered-prompt digest and byte length;
- selected hydrator, representation adapter, renderer, validation profile,
  and validator;
- requested executor model and reasoning/thinking configuration, plus the
  effective values when the runtime exposes them;
- any observed runtime fallback or substitution event, including any available
  reason and the qualification consequence;
- deterministic transport selection and delivery evidence;
- acting identity and live-authority re-verification result;
- current runtime safety-policy observation;
- validation results, diagnostics, expected-evidence status, and execution
  evidence; and
- explicit zero-effect markers stating that the receipt grants no authority
  and performs no lifecycle or state transition.

Receipts are append-only and evidence-only. A later entry may reference the
previous receipt digest, but it cannot revise the semantic contract, make a
failed attempt valid, or authorize another attempt.

## Sources, Hydration, Adapters, And Rendering

### Source manifest

A source manifest is an ordered inventory of exact source identities and byte
references selected for one attempt. It records provenance and selection; it
does not create source authority. Selection comes from declared ownership and
compatibility constraints, never opportunistic filesystem discovery.

### Hydrated context

Hydrated context is a deterministic, read-only, bounded projection of selected
durable sources. It should contain only the context needed for the declared
purpose and phase, such as lifecycle state, accepted inputs, pending decision,
asserted next action, prohibited actions, validation state, recovery cursor,
and provenance.

Hydration must not concatenate whole doctrine documents, completed histories,
or conversation transcripts merely because they are available. It must not
mutate durable workflow state.

### Representation adapter

A representation adapter maps product-neutral semantic requirements to an
executor-supported form. It preserves mandatory capabilities, phase, authority
references, prohibited actions, validation, reasoning class, evidence, and
transport guarantees. It may not redefine or weaken them.

### Deterministic renderer

A deterministic renderer converts the selected semantic inputs and adapted
representation into exact executor-visible bytes. It owns presentation, not
meaning, source selection, validation, authority, or transport.

### Validation profile and validator identity

A validation profile is the exact set of semantic validation rules selected
for an attempt. Validator identity names the exact implementation that applies
that profile. Both are selected once for a fresh attempt, recorded in the
receipt, and exact-matched for replay. Validation output is evidence; neither
the profile, validator, nor a passing result grants authority.

## Canonicalization And Digests

### Structured identities

Structured semantic-contract, source-manifest, hydrated-context, receipt, and
checkpoint bodies use the JSON Canonicalization Scheme in
[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html), identified as
`RFC8785-JCS`, canonicalization version `1`.

The requirements are:

- input satisfies the I-JSON constraints in
  [RFC 7493](https://www.rfc-editor.org/rfc/rfc7493.html);
- canonical output is UTF-8 with no byte-order mark;
- object ordering, primitive serialization, and escaping follow RFC 8785;
- Unicode strings preserve their exact code-point sequences; no NFC, NFD, or
  other Unicode normalization occurs;
- invalid Unicode, including unpaired surrogates, is rejected;
- duplicate object names, non-finite numbers, and numeric values that cannot be
  represented compatibly by the declared I-JSON/JCS constraints are rejected;
- no insignificant whitespace is emitted; and
- an unknown or incompatible canonicalization major fails before identity
  production or comparison.

Hash canonical UTF-8 bytes with SHA-256. The textual digest form is
`sha256:<64 lowercase hexadecimal characters>`.

Do not reinterpret or rewrite historical prompt hashes. A historical digest
continues to identify the exact byte boundary under which it was created.

### Rendered prompt bytes

Rendered prompt bytes are not JCS. New deterministic renderers must declare and
enforce:

- UTF-8 encoding;
- no byte-order mark;
- LF (`0x0A`) line endings;
- an explicit final-newline rule; and
- SHA-256 over the exact emitted bytes after that rule is applied.

Transport must preserve those bytes exactly. Framing, request envelopes, or
provider metadata are outside the rendered-prompt digest unless a separate
contract explicitly assigns them another identity.

## Fresh Execution

A fresh execution creates a new attempt under current authority and the
accepted operational contract.

- The semantic contract declares compatibility and selection constraints.
- Exact source blobs, hydrator, representation adapter, renderer,
  validation profile, validator, model recommendation metadata, and transport
  inputs are selected once for the new attempt.
- Selection completes before hydration and the selected identities are
  immutable for that attempt.
- Schema and canonicalization majors match exactly.
- Semantic sources and implementations fall within explicit compatible ranges.
- A new major is never adopted implicitly.
- Missing, ambiguous, duplicated, conflicting, stale, out-of-range, or
  guarantee-weakening inputs fail closed.

"Current compatible" means eligible at new-attempt selection time. It never
means a moving dependency within an attempt. Drift may justify a later fresh
attempt, but it cannot mutate an existing fresh attempt or replay.

## Replay

Replay reproduces contract identity and the previously authorized inputs. It
does not promise deterministic executor or model output.

Replay exact-matches:

- semantic-contract digest and version;
- schema and canonicalization identities;
- source bytes and references plus source-manifest digest;
- hydrated-context digest;
- hydrator;
- representation adapter;
- renderer;
- validation profile and validator;
- exact rendered-prompt bytes;
- original ordered transport policy;
- creating attempt and checkpoint lineage;
- durable state or receipt lineage; and
- authority-source reference and originally asserted action.

Replay does not read current mutable semantic sources, redetect repository
instructions, recompute selection, change a reasoning recommendation, upgrade
an adapter or validator, adopt changed imperative wording, or widen fallback.
If a required historical dependency is unavailable, replay fails closed rather
than presenting a new execution as replay.

The actual replay transport may differ only when the original ordered policy
allows it. The replay selects the first currently available permitted route in
that original order and records the selection. Current safety policy and live
authority still control; their current identities and outcomes are observed in
the new receipt rather than pinned into the historical semantic contract.

## Checkpoints

A checkpoint is a recovery pointer, never authority. It binds the creating
contract, attempt, selected source manifest, durable state or receipt lineage,
hydrated context, hydrator, adapter, renderer, exact prompt bytes, validation
profile and validator, transport policy, lifecycle state, recovery cursor, and
prior receipt.

Resumption emits a new append-only receipt. A checkpoint is invalid when its
contract, selected inputs, validation identity, evidence, or authority lineage
cannot be reconstructed exactly.

## Ownership And Live Authority

Apply this ownership precedence:

1. Current system and human safety constraints.
2. Human intent, task ledger, and explicit authorization.
3. Durable lifecycle state, accepted identities, and live authority.
4. Shared Playbook semantics.
5. Repository-local `AGENTS.md` and repository sources.
6. Bounded phase profile.
7. Representation adapter.
8. Renderer.
9. Transport.

An incompatible downstream claim fails closed. Lower layers may narrow
execution but may not override lifecycle, authority, accepted source identity,
replay meaning, or a mandatory guarantee.

Prompt text is not authorization. A contract digest is not authorization.
Validation success is not authorization. A receipt or checkpoint is not
authorization. Transport delivery is not authorization.

Authority must be represented by durable reference, including:

- approval-source identity;
- the exact StartupState or durable-receipt identity supporting the assertion;
- the action asserted as permitted when the contract was created; and
- an explicit marker that the assertion is non-authoritative.

Within the ctrl-alt-keith workflow family, those references point to the
durable CAK-62 authority sources. CAK-63 artifacts do not copy mutable
held/consumed/expired/revoked values into the semantic contract.

Immediately before execution or adoption, the acting layer must:

1. re-read live durable state;
2. verify the acting identity;
3. resolve current authority from the durable authority source;
4. confirm the asserted action remains permitted; and
5. reject consumed, expired, revoked, stale, ambiguous, or mismatched
   authority.

Snapshot-versus-live disagreement fails closed. Hydrators, representation
adapters, renderers, validators, receipts, and checkpoints must not:

- mutate CAK-62 or another owning lifecycle state;
- drive lifecycle transitions;
- sequence phases;
- grant authority or emit authorization tokens; or
- gate multi-run lifecycle decisions.

They may read owning evidence and emit their own evidence only. This is the
no-authority, no-state-transition, and no-orchestration boundary.

## Reasoning And Executor Adapters

Semantic contracts express reasoning product-neutrally with these classes:

- `light`;
- `medium`; and
- `high`.

Each capability and reasoning requirement declares whether it is mandatory or
advisory, any allowed degradation, and the guarantees that degradation may not
weaken. Concrete model names, tiers, provider settings, and reasoning knobs are
adapter guidance and attempt-receipt metadata, not semantic contract meaning.

An executor adapter must provide a testable mapping for each supported
mandatory requirement. If the executor cannot satisfy a mandatory capability
without weakening a guarantee, the adapter reports the requirement as
unsupported and fails closed. A parity check is evidence that mappings retain
semantics; it does not create parity by assertion or authorize execution.

## Transport And Fallback

A transport policy declares:

- preferred transport;
- ordered allowed fallbacks;
- prohibited transports;
- prerequisites and availability rules;
- invariants retained across routes;
- retry and idempotency policy; and
- receipt requirements.

Selection is deterministic: choose the first currently available permitted
route in declared order. Fallback may change delivery only. It must not change
prompt bytes, contract identity, validation, provenance, evidence, authority
handling, or required capabilities.

If no permitted route is available, a prerequisite is unmet, retry could
duplicate an unsafe effect, or a route would weaken an invariant, delivery
fails closed and records diagnostic evidence when possible.

## Issue-Owned Durable Rendered-Prompt Handoff Profile

Use this profile when exact rendered-prompt bytes become a dependency for an
executor attempt, review, recovery, or replay. It is a compatible operational
profile of the prompt contract and governed-artifact lifecycle, not a
provider-specific storage schema, prompt-management platform, or requirement
to preserve routine prompts.

The candidate and storage-admission boundaries are inherited from
[`Governed Artifact Capture`](evidence-lifecycle.md#governed-artifact-capture),
and baseline capture mechanics are inherited from
[`Direct Durable Capture`](evidence-lifecycle.md#direct-durable-capture). The
conditions below project those owners onto rendered prompts and narrow capture
with the dated-and-versioned name, no-autorename, provider identity,
capability-conditional revision evidence, and content-hash requirements. They
also add prompt-specific delivery,
attempt-evidence, recovery, and cleanup semantics without creating a second
governed-artifact owner.

### Admission

A rendered prompt is eligible for durable handoff only when all six conditions
are affirmative:

1. the output is substantial rather than ordinary chat;
2. exact identity is required for execution, review, recovery, replay, or
   another authorized dependency;
3. regeneration or conversation-only retention would weaken that dependency;
4. storage, visibility, privacy, and retention admission are affirmative under
   the owning storage contract;
5. the bytes contain no secrets, credentials, prohibited material, or unrelated
   personal, employer, or client content; and
6. the governing issue and natural durable owner are unambiguous.

Routine prompts remain non-durable by default. Missing or uncertain permission,
visibility, retention, ownership, or exact-byte preservation fails closed.
Redaction produces a different rendered-prompt identity and must never be
represented as the original exact prompt.

### One durable identity

The owning storage contract selects one immutable issue-owned destination for
the rendered prompt. Create it with one writer, a semantic versioned and dated
name, absent-create semantics, no overwrite, and no autorename. Corrections use
a new immutable version with predecessor lineage; do not create mutable
`latest`, `current`, or status-driven aliases.

New text prompts use UTF-8 without a byte-order mark, LF line endings, an
explicit final-newline rule, exact byte size, and SHA-256 over the exact
rendered bytes. Immediately retrieve the raw stored bytes and verify the format,
size, digest, immutable human locator, provider locator, provider object
identity, provider content hash when available, and containment beneath the
owning issue destination. Record provider revision when the owning provider
exposes it. Otherwise record explicitly that revision evidence is unavailable;
never fabricate a revision or treat another identifier as its substitute.
Provider content hashes stay distinct from whole-file SHA-256.

The owning storage contract, rather than this provider-neutral profile, defines
the concrete provider, account, namespace, issue-path grammar, privacy,
visibility, and retention values. Do not copy those project-specific values
into reusable doctrine or executor adapters.

### External delivery envelope

Freeze the exact rendered-prompt bytes before deriving their final size,
SHA-256, provider object identity, provider revision evidence, or delivery
route. Record those derived identities in an external delivery envelope or in
delivery and producing-receipt evidence. The envelope is not part of the
referenced rendered-prompt bytes or rendered-prompt digest.

Do not embed a placeholder digest or other provisional self-identity in the
rendered prompt and later describe it as the final identity. A copied,
reformatted, or otherwise changed prompt is not byte-identical; when admitted,
it receives a new deterministic rendering and exact identity.

Keep operator metadata, the external delivery envelope, rendered prompt,
producing receipt, delivery evidence, and attempt receipt as separate
boundaries. The semantic prompt contract remains separate from all of them.

### Delivery

There is no separate durable exchange, handoff, inbox, registry, or transport
root. Select delivery in this order:

1. the executor retrieves the exact issue-owned durable object directly through
   a currently qualified connector or provider route; or
2. one private OS-managed executor-owned attempt-local retrieval carries the
   same exact bytes when direct provider retrieval is unavailable or
   unqualified.

The fallback is disposable transport mechanics, not a second durable artifact,
planning surface, queue, registry, or authority source. Operator-mediated exact
retrieval is permitted when the controller can verify the provider object and
the executor can verify the local bytes. Copy/paste is not an exact-byte route
unless the result is rendered, admitted, and identified as a new prompt.

Before acceptance, the receiving attempt verifies the durable identity,
delivery identity, local byte size and SHA-256 where a local copy exists,
encoding, BOM state, line endings, final-newline rule, and current authority.
Fallback changes delivery only; it cannot change prompt bytes, semantic
meaning, validation, provenance, evidence, authority handling, or required
capabilities.

### Evidence and coordination states

Keep separate identities for:

- the durable rendered prompt;
- the producing receipt;
- the delivery operation;
- executor acknowledgement;
- executor attempt;
- attempt receipt;
- executor output; and
- human disposition.

Every admitted durable prompt write inherits the requirement for exactly one
distinct producing receipt from
[`Producing Receipt And Compact Delivery`](evidence-lifecycle.md#producing-receipt-and-compact-delivery).
It is not the rendered prompt, delivery evidence, executor acknowledgement,
attempt receipt, output, or human disposition.

`Reconciled exact` is limited to recovery after an ambiguous result from a
prior absent-create attempt: the same frozen target and provider object identity
already exist, raw readback exact-matches the intended bytes and identity, and
the recovery proves that no second write occurred. Reuse the prior write's one
producing receipt when it is verified; if that write completed without a
receipt, recovery creates exactly one and records the ambiguity and lineage. A
pre-existing object without those facts is a collision, not reconciliation.

The smallest sufficient coordination evidence may report the following states
only when their minimum predicates are met:

| State | Minimum evidence |
| --- | --- |
| `PRESERVED` | One durable object was created, or a prior ambiguous absent-create was reconciled exact under the rule above; raw provider readback exact-matched the intended bytes, size, format, digest, and containment. |
| `DELIVERED` | One delivery operation identifies the exact rendered prompt, selected route, intended target, and observed delivery result. |
| `ACCEPTED` | The receiving executor explicitly acknowledges the prompt identity; delivery alone is insufficient. |
| `STARTED` | One unique executor attempt actually began; acknowledgement alone is insufficient. |
| `COMPLETED` | The attempt reached a terminal successful execution result and records the output identity where applicable. Completion does not imply correctness, human acceptance, merge, release, or adoption. |
| `FAILED` | A bounded failure class, attempt or delivery identity, and last verified state are recorded. |
| `UNKNOWN` | Required evidence is unavailable; no later state is inferred. |

Each state describes observed evidence under its owning operation; it is not
workflow approval, lifecycle authority, transition permission, or evidence
that a later state occurred. Preserve an append-only attempt receipt that binds
the contract, prompt, selected route, delivery evidence, consumed digest,
acting identity, current authority result, output identity, and terminal
outcome as applicable.

### Recovery, fresh execution, and cleanup

Recovery follows the owning planning decision to the immutable rendered-prompt
identity, delivery evidence, executor attempt receipt, and executor output,
then freshly retrieves current repository, provider, planning, and authority
state from their owners. Historical prompt bytes and receipts remain historical
evidence; they never become current authority or current mutable state.

Fresh execution selects current compatible inputs under current authority.
Replay uses the recorded contract and exact historical inputs under the replay
rules above. Do not present a new execution as replay when any required
historical identity is missing or mismatched.

This profile creates no durable transport object to clean. Remove only the
private attempt-local retrieval after the attempt no longer depends on it and
required delivery and attempt evidence is preserved. Revalidate containment and
identity, and fail closed on the shared cleanup conditions in
[`repo-readiness.md`](repo-readiness.md#repo-local-workflow-state). Never delete
or rewrite the durable prompt as transport cleanup, and do not infer recurring
cleanup or hygiene automation from this bounded rule.

Preservation, delivery, acknowledgement, hashes, provider state, validation,
receipts, execution, and cleanup transfer zero authority.

## Semantic Versioning

Use semantic versions to classify meaning and exact digests to identify bytes:

- **Major**: changes authority, lifecycle meaning, guarantees, replay,
  compatibility-major behavior, or fallback semantics.
- **Minor**: changes executor-visible imperative instruction wording, adds new
  required behavior, or adds compatible semantic meaning.
- **Patch**: strictly non-behavioral formatting, comments, or metadata that is
  invisible to the executor and changes no contract behavior.

Any executor-visible imperative wording change is at least Minor. A parity
check supplies classification evidence; it does not grant the classification.
Changed approved bytes remain subject to the owning reviewed-identity and
approval-retention rules, including CAK-62 rules where they apply. A version
label never preserves approval by itself.

## Mandatory Failure Boundary

Fail before rendering, delivery, adoption, or execution when an applicable
condition includes:

- missing contract, source, state receipt, authority reference, selected
  identity, or required evidence;
- a contract/receipt boundary violation or derived digest in the contract;
- digest, exact-byte, schema-major, canonicalization-major, source-range,
  validator/profile, or checkpoint-lineage mismatch;
- invalid Unicode, duplicate names, non-finite or incompatible numbers,
  malformed JSON, encoding mismatch, or rendered-byte policy violation;
- stale, ambiguous, duplicated, conflicting, or out-of-range input;
- unavailable replay dependency or replay selection drift;
- absent mandatory executor capability;
- live authority that is stale, consumed, expired, revoked, inferred,
  ambiguous, mismatched, or inconsistent with the recorded assertion;
- transport that changes bytes or weakens provenance, validation, evidence,
  capabilities, or authority controls;
- an attempt to mutate lifecycle state, emit authorization, drive a transition,
  or orchestrate phases; or
- deterministic canonicalization, hydration, adaptation, or rendering that
  disagrees for identical inputs.

Failure may emit a non-authorizing diagnostic receipt. It must not repair,
upgrade, transition, authorize, or execute.

## Scope Boundary

This semantic contract deliberately does not define an operational schema,
serializer implementation, hydrator implementation, renderer template,
attempt receipt instance, workflow state shape, or repository-specific path.
Those belong to the implementing repository and must pin this Playbook-owned
semantic version and exact artifact identities.

## Architecture Provenance

This semantic baseline implements the human-approved CAK-63 architecture
package merged through
[`knowledge-vault` PR #75](https://github.com/ctrl-alt-keith/knowledge-vault/pull/75)
at exact commit
[`d6f5f26f0db3f320489599c88f503558c4082925`](https://github.com/ctrl-alt-keith/knowledge-vault/commit/d6f5f26f0db3f320489599c88f503558c4082925).
The Knowledge Vault retains the proposal, decision record, independent review,
and finding disposition. This page retains only the promoted reusable
semantics.
