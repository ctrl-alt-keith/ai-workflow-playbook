# Experimental exact-artifact retention

This is the opt-in CAK-301 increments 0–2 development surface. Start with the
repository's [current bootstrap](../docs/start-here.md), then this contract.
The default bootstrap, v1 doctrine, and `main` remain unchanged. This package
is a provisional implementation candidate, not an operational installation,
qualified Dropbox route, release, or architecture promotion.

## Contract and ownership

One synchronous operation retains exact supplied bytes at one reserved target.
`prepare` freezes the operation and BLOB input; `run` admits at most one local
submission; `reconcile` observes through a reader; `show` derives historical
status from retained facts. Operation and effect identities are independent of
the content digest. Equal bytes in a new operation require a new target/grant.

Use one persistent operator-managed host and trusted participating processes.
The operator owns the installation note, source admission, local grant interface,
retention disposition, and recovery decisions. Linear/chat do not supply live
runtime grants. The executor has no grant-create or grant-extend path.
`python -m v2_retain.admin` is the separate operator interface. It faithfully
records explicit human provenance; this API separation does not authenticate
a human against a hostile process running as the same OS account.

Inputs are bounded at 16 MiB, including empty and arbitrary binary content.
Optional UTF-8 and final-LF checks apply only when declared. The operation binds
the source owner/ref, contract ref/hash, actor, exact target, original validity,
retention/visibility refs, route qualification, and optional decision scope.
The supported semantic version is `retain-exact/experimental-1`; unknown
versions fail closed. No compatibility layer or policy-resolution language is
provided. References must already be resolved by their owning operator.

The store is explicit operation record A with append-only observations, not
event sourcing. SQLite uses DELETE journaling, EXTRA synchronization, foreign
keys, schema/integrity checks, immutable-record triggers, and unique target and
dispatch constraints. Operation spec and input are checked on every load.
The external installation note binds IDs plus database/lock device and inode.
Missing state never initializes a replacement. File replacement, wrong owner,
unsupported schema, or corruption blocks. Trusted processes must not replace
the lock file to force takeover.

Grant creation/revocation and submission hold the same installation `flock`.
Admission rereads the original scope, actor, validity, and revocation state,
commits a sticky dispatch latch, rechecks at the last local gate, then calls the
adapter once while exclusion remains held. An unacknowledged latch commit
blocks submission. A post-latch refusal, crash, error, or missing response never
clears or rearms it. A revoke waiting behind a live submission is not yet an
accepted revocation and cannot cancel that request. No expiry timer, retry,
takeover, or automatic compensation exists.

Reconcile has no writer argument or import. The local reader opens the
destination database in read-only mode. The SDK reader has a separate
transport that admits only account, metadata, and download routes. Observation
does not renew write authority. Read access is supplied by the current bound
reader identity and its provider access; it is distinct from an expired write
grant. A target-only matching object without acknowledged causal identity stays
uncorrelated in the SDK seam, including across repeated reconciliations.

Exact verification compares actual bytes, size, ID/revision, and target.
Duplicate identities, conflicting revisions, corruption, and truncation remain
visible. A collision is not adoption. Empty, unavailable, or incomplete reads
after dispatch remain holds. Conflict history is not erased by a later healthy
read. `retained_verified` means the observed local object/version passed the
mechanical check; it grants no semantic acceptance or publication authority.
`show` is explicitly historical. Optional decisions bind operation, exact
candidate, property, owner, contract ref/hash, and validity; C0 acceptance cannot
satisfy C1. Conflicting applicable decisions remain conflicts.

There are at most 256 observations and 512 invocation records per operation.
Observation bodies are bounded to 64 KiB. Exhaustion blocks further recording;
it does not evict evidence. Inputs, reservations, latches, and observations are
retained while unresolved and through pilot review. Retirement needs explicit
operator disposition; this candidate has no purge command or infinite-retention
promise. An `abandoned` scoped disposition does not establish absence, clear a
latch, free a target, or authorize replacement.

## Development commands

The development baseline is Python 3.13 on Unix. Canonical validation is:

```console
make help
make v2-setup
make check
```

Setup is explicit and installs the pinned SDK/HTTP dependency set into `.venv`.
`make check` includes existing repository checks and `make v2-check`. The latter
runs actual operation/store tests, child process crash tests, and SDK requests
against a loopback HTTP fixture. `.v2-test-state/` is repository-owned synthetic
test state. No test contacts Dropbox, provisions credentials, creates a provider
folder, or qualifies a live route. No live qualification target is provided in
this increment. CI uses the same canonical path and one runtime.

The CLI accepts an exact operation JSON document with the fields in
[`Operation`](model.py). The local route fingerprint comes from
`LocalWriter(destination, target, actor).qualification.fingerprint`; it binds
the actual local destination file. The JSON's `input_hash` and `size` are the
SHA-256 and byte length of the supplied input, not extracted text.

For an explicitly owned local synthetic development directory, the command
sequence is below. `STATE`, `IDENTITY`, `DESTINATION`, `SPEC`, and `INPUT`
denote chosen file paths; the parent directory must already exist. The operator
retains the installation note independently of disposable conversations.

```console
python3 -m v2_retain.admin --store STATE --identity IDENTITY --owner operator init
python3 -m v2_retain.admin --store STATE --identity IDENTITY --owner operator init-local-destination DESTINATION
python3 -m v2_retain --store STATE --identity IDENTITY prepare --spec SPEC --input INPUT --owner operator
python3 -m v2_retain.admin --store STATE --identity IDENTITY --owner operator grant OPERATION --provenance HUMAN-REFERENCE
python3 -m v2_retain --store STATE --identity IDENTITY run OPERATION --destination DESTINATION --actor executor
python3 -m v2_retain --store STATE --identity IDENTITY reconcile OPERATION --destination DESTINATION --actor executor
python3 -m v2_retain --store STATE --identity IDENTITY show OPERATION
python3 -m v2_retain.admin --store STATE --identity IDENTITY --owner operator revoke GRANT-REFERENCE --provenance HUMAN-REFERENCE
```

`admin decision --record FILE` appends a JSON disposition with `op_id`,
`candidate`, `property`, `contract_ref`, `contract_hash`, `owner`, `verdict`,
`expires`, and `provenance`. The verdict is accepted, rejected, or abandoned;
expiry is a finite Unix timestamp. Dispositions do not mint execution grants.

The tests contain a complete synthetic spec construction and exercise both
the library and fresh-process CLI. Operational host selection/provisioning is
still deferred. An operational store must be on an explicitly owned persistent
local non-synced volume, outside Dropbox, a repository checkout, and disposable
task storage. The CLI does not certify a filesystem's persistence or mount
properties. Do not copy or restore an old store into active service. Known
restore/recovery uses a recovery-only installation note. In-place rollback of
the same inode is not detected; host loss, rollback, backup transitions, power
loss, and reboot durability require separate qualification and disposition.

## Direct Dropbox SDK seam and claim ceiling

The adapter uses the official SDK 12.2.1 with an explicit account, namespace,
parent ID/path, actor, credential reference, and timeout configuration. The SDK
serializes `files_upload` with add mode, `autorename=false`, and
`strict_conflict=true`. Account and parent are checked through the bound
namespace before admission. Readback uses `rev:<revision>` and verifies returned
identity plus subsequent target metadata. Returned acknowledgements and actual
byte observations are persisted separately.

SDK 5xx/rate-limit retries and HTTPAdapter retries are zero. Redirects, ambient
proxy/netrc credentials, and credential refresh are disabled. The installed
SDK has an expired-token refresh/retry branch separate from its retry counts;
`NoRefreshDropbox` refuses it. Tests observe actual HTTP requests for 5xx, 429,
expired token, redirect, and timeout cases. A preflight or SDK error never
becomes automatic retry permission, and exception payloads are not retained as
receipts because they may contain sensitive provider data.

This development build uses only a synthetic token and disables the socket
transport unless an explicit loopback fixture is selected. Real credential
provisioning and transport enablement require the next separately authorized
increment; there is no switch that silently enables provider writes now.
The adapter request/readback implementation is present, but its operational
route is unqualified. Local fixture success is not a Dropbox guarantee.

`Qualification` records build/config identity, target scope, evidence, checked
date, create/retry intent, admission boundary, collision request/response
references, invalidation triggers, and claim ceiling. Defaults explicitly mark
collision evidence unqualified. There is no free-standing qualification Boolean
or route registry. Material configuration/dependency changes invalidate use.
Live qualification must test exact identical- and distinct-content collision
requests and responses on the selected SDK route; the old E3
ALREADY_EXISTS/INVALID_ARGUMENT narrative is not its classifier or evidence.

Official references checked 2026-09-12:

- [Dropbox client and retry controls](https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html)
- [Dropbox strict conflict contract](https://dropbox-sdk-python.readthedocs.io/en/latest/api/files.html#dropbox.files.CommitInfo)
- [Dropbox file identity and revision addressing](https://developers.dropbox.com/dbx-file-access-guide)
- [Requests session, redirects, and HTTPAdapter](https://requests.readthedocs.io/en/latest/api/)
- [Python SQLite interface](https://docs.python.org/3.13/library/sqlite3.html)
- [SQLite synchronization](https://www.sqlite.org/pragma.html#pragma_synchronous)
- [SQLite atomic-commit assumptions](https://www.sqlite.org/atomiccommit.html)
- [Python Unix locks](https://docs.python.org/3.13/library/fcntl.html)

Documentation supports the selected calls/configuration. Local socket/process
tests establish the observed client behavior. Neither establishes real provider
atomicity, negative-read consistency, global cardinality, exactly-once commits,
host physical durability, or authority through remote commitment.

## Planning and review context

Inputs are the provisional CAK-301 implementation plan 01
(`id:FHKdoRfTdTUAAAAAAAAL3g`, revision `0165b4d831d7fbb000000037baf16c3`)
and architecture synthesis 01 (`id:FHKdoRfTdTUAAAAAAAAL3A`, revision
`0165b4d219e49cd000000037baf16c3`). They were retrieved for planning; their
historical experiments were not rerun or treated as current provider proof.
Keith explicitly authorized increments 0–2 and the narrow repo-scope exception.

Accepted independent-review findings are reconciled as follows:

| Finding | Implementation assumption and boundary |
| --- | --- |
| R1 | Five obligations are a useful provisional partition, not proven irreducible. The package follows the operation, not five services. |
| R2 | Candidate/property/owner/contract applicability is required. Permanent C0/C1 tests exercise actual stored decisions. Historical coverage remains unqualified. |
| R3 | Historical collision-specific evidence is insufficient. No legacy error narrative drives behavior; exact SDK collision qualification remains future work. |

V1 is preserved at annotated tag
`archive/v1-before-cak-301-v2-2026-09-12`, tag object
`95fc48f1d52ba7de3ff01b1186f83ab9906ce7e2`, pointing to
`f2b354ed632994f7d602dce24e78a550180f15f7`. Both identities were verified
remotely before v2 code edits. Treat this as a non-moving archive; it does not
claim a newly installed server-side tag-protection rule. Git history remains
intact and the repository was not archived.

This work stays one cohesive branch/worktree/PR. Controller inspection and
acceptance remain here. No mechanical worker was launched because the code and
fault tests share evolving admission/recovery semantics; handoff and acceptance
cost was not justified. T14 observations include source hydration cost, fixture
repairs, and controller review work. No telemetry infrastructure, savings, or
delegation-economics claim is added.

Stop at a locally validated draft PR. Next is the human join with synthesis 02
and review, followed only by a separately authorized increment 3 if selected.
No promotion, bootstrap cutover, ready status, merge, auto-merge, release, or
CAK-301 closure is authorized by this candidate or its validation.
