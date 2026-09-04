# CAK-220 Airtable Handoff Doctrine Candidate

Status: candidate only; not accepted Playbook doctrine

## Decision Requested

Promote the minimum Airtable protocol below as the default ChatGPT/Claude
transport for qualifying small canonical-text handoffs, and retire the current
Dropbox-backed prompt-handoff route and its file-specific ceremony from that
normal path.

This is a material doctrine change under `docs/feature-lifecycle.md` because it
changes a required cross-executor contract and reverses the accepted Dropbox
handoff doctrine. Governed independent review and Keith's explicit promotion
decision against this exact candidate identity are required before
implementation.

## Evidence Boundary

- Governing work: Linear CAK-220.
- Empirical evidence: CAK-216 final reconciliation comment
  `071b2216-29a9-4e1c-9ac9-8ee344c24f22`.
- Validated Airtable surface: base `appCJ4M8NJUxMj7K7`, table
  `tblUwz8PIkwS80SeH`.
- ChatGPT-produced record: `recJOlBg1CPYd2zMq`, independently verified by
  Claude as 77 UTF-8 bytes with SHA-256
  `979d5710e677ed841bd079ee13ae55707a0f6ed25f698a34d175d4c8afae04e0`.
- Claude-produced record: `recBmp6AVRDHnbK9A`, independently verified through
  the ChatGPT-connected Airtable action as 65 UTF-8 bytes with SHA-256
  `3abb7d37bdccc29483c4fc9a133c4bcaa4a13e9ac2bc78fd0bc1c64b06af1ae2`.

The CAK-216 base is test evidence, not a reusable account-specific destination
to encode in Playbook doctrine. Provider configuration and per-attempt base,
table, and record identities stay outside the repository and are carried in
the handoff envelope.

## Proposed Normative Effect

### Qualification

Use Airtable for a ChatGPT/Claude handoff when the complete payload is small
canonical text and both the producer and consumer have a permitted route to
the selected base and table. Airtable is not promoted as a general artifact
store or an arbitrary-byte transport.

If the handoff requires arbitrary bytes, provider file identity, provider
revision, or provider checksum behavior, use the separately justified
file-backed artifact workflow. Dropbox does not remain a fallback for the
normal small canonical-text route.

### Record and attempt contract

Create one new Airtable record per producer attempt with exactly these required
fields:

- `Handoff Key`
- `Payload`
- `Payload Bytes`
- `SHA-256`
- `Producer`

The payload is plain text encoded as UTF-8 without a BOM and with LF line
endings. The producer declares the final-newline state as `present` or
`absent`; that state is part of the frozen payload identity and the consumer
must verify it. `Payload Bytes` is the byte length of that exact UTF-8 sequence,
and `SHA-256` is its lowercase whole-payload digest.

A frozen record is append-only by protocol: never update it. A correction
creates a new handoff key and record, and the external envelope names the
predecessor when one exists. Airtable key uniqueness and record immutability
are not assumed.

`Producer` is declared metadata. It does not authenticate the executor because
the validated ChatGPT and Claude connectors act as the same Airtable user.
Executor and attempt identity remain external evidence.

### External handoff envelope

The producer hands over one compact envelope containing:

- exact base ID;
- exact table ID;
- exact record ID returned by Airtable;
- expected handoff key;
- text format (`UTF-8`, no BOM, LF) and final-newline state;
- expected byte length;
- expected lowercase SHA-256;
- producer executor and attempt identity; and
- predecessor identity when the attempt corrects an earlier record.

The envelope is external to the mutable Airtable record. Values stored only
beside the payload are not independent verification evidence.

### Consumer verification

The consumer retrieves the record by exact record ID, not by key search or
fuzzy search, and requires exactly one returned record. It then:

1. checks the record ID, handoff key, and required field set;
2. re-encodes `Payload` under the declared text and final-newline rules;
3. independently recomputes byte length and SHA-256; and
4. requires equality among the recomputed values, the stored metadata, and the
   external envelope.

Missing records, more than one result, wrong or missing fields, unexpected key
or record identity, stale attempts, text transformation, truncation, byte-count
mismatch, and digest mismatch fail closed. Key lookup is diagnostic only.

The protocol introduces no new lifecycle states, approval gates, fallback
ladder, helper framework, storage abstraction, or provider-wide schema.

## Canonical Ownership And Planned Implementation

- `docs/prompt-contracts.md` remains the narrow shared owner of exact material
  prompt identity, canonical text, external-envelope, verification, attempt,
  authority, and fail-closed semantics. Its current issue-owned durable
  rendered-prompt profile will be reduced to the Airtable record contract for
  qualifying small canonical-text prompts while retaining file-backed rules
  only where arbitrary bytes or provider-file evidence is genuinely required.
- `docs/prompts.md` will select the Airtable-backed thin handoff for qualifying
  ChatGPT/Claude machine recipients and will remove the Dropbox transport-only
  latch, confirmation workaround, file-backed Prose-DAG pilot, preview/link
  path, and Dropbox-specific delivery selection.
- The ChatGPT adapter will contain only current Airtable connector create/read
  projection and compact envelope presentation. The Dropbox confirmation,
  preview, download-link, and prompt-specific provider-checksum sections will
  be removed.
- The Claude adapter will contain only exact-record consumption/production
  projection for Claude surfaces with a currently qualified Airtable route.
  Its prompt-specific attempt-local Dropbox retrieval ceremony will be removed.
- The Codex adapter will change only where Codex receives the exact Airtable
  envelope and verifies the returned text. Prompt-specific attempt-local
  download mechanics will be removed.
- Nearby core wording, reusable delivery-envelope templates, semantic anchors,
  and mechanical conformance tests will be updated or removed so they express
  the new minimum once, without leaving Dropbox as an apparent active handoff
  route.

The prompt-contract change alters transport and fallback semantics, so the
existing semantic-version rule requires a new compatibility major for new
selections. Historical v1-v3 anchors and historical evidence remain unchanged;
new selections use a minimal v4 anchor reflecting the Airtable contract.

## Dropbox Retirement And Retention

Remove from mutable normal-flow guidance and tests:

- Dropbox as the default ChatGPT/Claude prompt transport or fallback;
- folder and absent-file creation for normal prompt handoff;
- the post-plan confirmation correction path;
- prompt preview and single-use download-link generation;
- prompt-specific Dropbox file identity, revision, content-hash, and raw-file
  verification;
- prompt-retrieval basenames, local downloads, and attempt-local cleanup; and
- Dropbox-specific latches, pilot transitions, examples, and diagnostics.

Retain Dropbox guidance only where the subject is actually file-specific, such
as arbitrary-byte governed artifacts, provider object identity, revision,
content hash, or historical provenance. Do not migrate or delete historical
Dropbox data, accounts, configuration, receipts, or immutable v1-v3 contracts.

## Scope, Exclusions, And Risks

In scope: shared prompt/handoff doctrine, the three affected executor adapters,
reusable handoff templates, compatibility anchors, and focused conformance
tests in `ai-workflow-playbook`.

Out of scope: a general Airtable artifact store, historical-data migration,
Dropbox account or data deletion, a new lifecycle engine, provider automation,
authenticated executor identity from the shared Airtable user, and merge.

Primary risks are leaving a stale Dropbox normal route, duplicating verification
rules across adapters, accidentally treating stored digest metadata as
independent evidence, or implying Airtable immutability/uniqueness. Final
validation must search every mutable Dropbox handoff reference, inspect each
remaining reference as historical or genuinely file-specific, and run
`make check`.

## Acceptance Criteria

- Qualifying small canonical-text ChatGPT/Claude handoffs select Airtable.
- Producer behavior is one new five-field record and one external envelope.
- Consumer behavior is exact-record retrieval and independent byte/digest
  verification.
- Missing or mismatched content fails clearly and closed.
- Shared invariants have one narrow canonical owner and adapters remain thin.
- Dropbox handoff ceremony is absent from the normal path while real
  file-specific guidance and historical contracts remain intact.
- The resulting documentation is materially simpler than the Dropbox design.
- `make check` passes and the final PR stops before merge for Keith's review.

## Current Stop Boundary

This candidate may be committed, pushed, and opened as a draft proposal PR for
inspection. Stop before governed Claude review at Keith's requested checkpoint.
The candidate, its review, and validation grant no promotion or implementation
authority. After Claude review, substantive findings must be dispositioned and
Keith must explicitly promote the exact reviewed proposal before implementation
continues on this branch.
