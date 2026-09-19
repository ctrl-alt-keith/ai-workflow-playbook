# Supplied Review Evidence

`review_evidence.py` stages and verifies selected local evidence for a governed
review. The controller owns authorized provider access, exact issue ownership,
source selection, provider identity/revision verification, storage admission,
and the applicability decision under
[Evidence Lifecycle](../docs/evidence-lifecycle.md). Local bundle verification
establishes structure and byte integrity only; it does not independently observe
Dropbox, authenticate the controller, resolve external references, or grant
reviewer network/connector capability.

## API and manifest

- `BUNDLE_SCHEMA = "governed-review-evidence-bundle/v1"`
- `MANIFEST_NAME = "manifest.json"`
- `stage_bundle(bundle_dir: Path, manifest: Mapping[str, Any], source_bytes:
  Mapping[str, bytes]) -> dict[str, Any]`
- `verify_bundle(bundle_dir: Path) -> dict[str, Any]`

Both return a validated, detached manifest. Invalid claims raise `EvidenceError`
(a `ValueError`); filesystem access failures may raise `OSError`. There is no
provider client or archive migration. The v1 schema is intentionally closed:
unknown keys, tags, and providers fail closed.

The manifest has exactly `schema`, `reviewed_candidate`, `applicability`, and
`sources`. The schema equals `BUNDLE_SCHEMA`. Candidate tags are:

- `repository_commit`: `kind`, canonical `repository` as `owner/repository`,
  and `commit` as a full 40- or 64-character lowercase hexadecimal identity.
- `immutable_artifact`: `kind`, `provider` (`dropbox` in v1), `namespace`
  (`ns:<digits>`), `object_id` (`id:<opaque identifier>`), nonempty `revision`,
  positive integer `byte_length`, and whole-file lowercase hexadecimal `sha256`.

Applicability has `status` (`applicable`, `superseded`, or `unobservable`), a
nonempty `basis`, and optional `evidence_ref` naming a selected source ID or an
exact external record. Only `superseded` requires `superseded_by`, another tagged
candidate distinct from the reviewed candidate. Supersession preserves the
original candidate; it does not declare historical invalidity. The controller
must resolve referenced evidence and record each new decision append-only in
its owning record. This module preserves the supplied declaration without
deciding its truth or maintaining a historical ledger.

Each source has `id`, `provider`, `namespace`, `object_id`, `revision`,
nonnegative `byte_length`, whole-file `sha256`, and `content_path`. Provider
identity fields use the artifact conventions above. Source IDs are unique
`[A-Za-z0-9._-]+` basenames excluding `.` and `..`; `content_path` is exactly
`evidence/<id>`. At least one source is required. The supplied bytes mapping must
have exactly those IDs and matching lengths and digests. Manifests contain no
raw content and no provider checksum in place of whole-file SHA-256.

## Local boundary

Select a fresh bundle directory beneath an already authorized private attempt
directory. The parent and any existing empty bundle root must be owned by the
current user with mode `0700`; path components may not be symlinks. Staging is
exclusive: existing content is never overwritten. Bundle directories use
`0700`, regular files use `0400`, and verification rejects unexpected or missing
files, symlinks, hardlinks, special files, path escapes, duplicate JSON keys,
invalid modes, and content mismatch. A failed staging attempt may leave partial
output for its owning attempt's cleanup; never reuse it. Preserve required
durable evidence under its existing storage contract before cleanup.

These permissions prevent incidental writes; they are not a sandbox against
the same operating-system user. The caller must bind the verified manifest to
the exact review candidate, provide the reviewer only local read access, and
retain the existing reviewer isolation controls. A self-consistent replacement
of the entire bundle cannot be authenticated by its own manifest. Filesystem
checks do not claim absence of every concurrent same-user mutation.

Attribute provider verification to the controller and content inspection to
the reviewer. Runtime capability that is not observed remains unobservable;
supplied evidence does not establish live provider observation or capability.
Deterministic tests use synthetic bytes and provider identities and do not
qualify a real provider.
