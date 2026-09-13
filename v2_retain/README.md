# Experimental exact-artifact retention

This is the opt-in CAK-301 exact-retention implementation. Start with the
repository's [current bootstrap](../docs/start-here.md), the
[accepted v2 architecture foundation](../docs/v2-architecture-foundation.md),
then this contract. The default bootstrap remains v1. A bounded Mac-local
Dropbox route has [accepted qualification evidence](https://www.dropbox.com/scl/fi/avq1lwwuakgtlnpnr25ll)
for its reviewed runtime semantics at pre-rebase head
`e6cebe4f6ee1891b56697a71b4846608a9034f66`, with two outcomes still held.
This package is not an operational
installation, general provider qualification, release, or Product promotion.

## Synthetic conditional-merge experiment

`merge_envelope.py` is a local-only CAK-301 dogfood model for one
`squash-merge PR X into main` retry decision. It has no GitHub integration,
storage, provider call, approval-creation path, or automatic replay. Its only
output is an explainable local eligibility decision. A retry is eligible only
after `known-no-effect`, unchanged exact PR/head/context and action, fresh
named conditions, and current authority scoped to that action/candidate.

An observed candidate or context divergence irreversibly invalidates the
envelope epoch. Returning later to the old SHA does not revive it: a new
qualification and new authority would be needed for a new envelope. An unknown
effect holds for reconciliation; an uncorrelated apparent output is not causal
success. The model exercises I1--I5 as source/condition inputs, authority,
uncertain-effect holding, exact applicability, and explicit route/claim
identity; it adds no sixth invariant and makes no remote guarantee.

## Synthetic recovery-join experiment

`recovery_join.py` is a second local-only CAK-301 dogfood model. A compact
breadcrumb names one durable decision and the current owners needed to join it.
Explicit supplied observations then recover an explainable next-action ceiling:
the historical decision must be exact and applicable, while repository,
authority, effect, and route facts must come from their named current owners.
The model performs no retrieval, storage, GitHub call, or effect; its caller
supplies all observations.

An approved durable summary, a worker reconstruction, matching output, or an
old instruction never creates current authority. Current owner contradiction,
owner mismatch, unknown effect, unavailable required owner, or unsupported
route produces a bounded hold for that conclusion. The sole positive result is
limited to the model's named local bounded action. This exercises I1--I5 as a
small experiment; it is not a universal handoff format, evidence graph,
manifest registry, or agent-memory layer.

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
folder, or qualifies a live route. CI uses the same canonical path and one
runtime. The separate live qualification command below is never part of
`make check` or the default CLI.

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

The default profile uses only a synthetic token and disables the socket
transport unless an explicit loopback fixture is selected. The separate
`live-qualification` profile requires a resolved `DROPBOX_ACCESS_TOKEN` in the
process environment and an explicit caller-supplied token matching that value.
It uses no ambient proxy, netrc, `.env`, keychain, refresh token, or 1Password
SDK path. The application never invokes `op`; the operator's local `op run`
process injects the credential. The selected Mac-local request/readback route has one
accepted bounded live qualification; broader operational use still requires
its own applicable authority and host/profile evidence. Local fixture success
is not a Dropbox guarantee.

`Qualification` records build/config identity, target scope, evidence, checked
date, create/retry intent, admission boundary, collision request/response
references, invalidation triggers, and claim ceiling. The live profile also
binds the actor account, account root/home namespace IDs, implicit App Folder
root, verified folder ID/path, credential-reference label, SDK version, and
exact head. Defaults explicitly mark collision evidence unqualified. There is
no free-standing qualification Boolean or route registry. Material
configuration/dependency changes invalidate use. Live qualification tests
identical- and distinct-content collision requests and responses on the
selected SDK route; the old E3 ALREADY_EXISTS/INVALID_ARGUMENT narrative is
not its classifier or evidence.

## Mac-local live qualification boundary

Keith completed the bounded `cak-301-v2-qual-20260912-01` run on the pre-rebase
reviewed head; its [post-run review](https://www.dropbox.com/scl/fi/avq1lwwuakgtlnpnr25ll)
accepted six retained files, two typed same-target conflicts, and two uncertain
outcomes correctly held. Reboot/power-loss durability and broader provider
guarantees remain unqualified. Its folder, objects, and local evidence are
retained; do not rerun or clean them up during repository reconciliation.

The commands below describe the interface for a separately authorized future
session on a fresh folder, with `REVIEWED_HEAD` replaced by that session's exact
40-character reviewed head and `FRESH_FOLDER` by a fresh single child of the
app's implicit root. The folder is created only during `--mode execute`.
The command requires the checkout to be at its worktree root with no tracked or
untracked changes before any credentialed request; ignored qualification state
cannot substitute for a clean source tree.
The read-only command checks that the credential is accepted, retrieves the
acting account and root/home namespace IDs, lists the implicit app root, and
checks that the selected folder is absent. It performs no write:

```console
DROPBOX_ACCESS_TOKEN='op://Private/CAK v2 Dropbox Qualification/access_token' op run -- .venv/bin/python -m v2_retain.qualify_live --mode preflight --folder /FRESH_FOLDER --expected-head REVIEWED_HEAD
```

After checking the non-secret account and namespace facts and confirming in
the Dropbox app configuration that this token belongs to an **App Folder**
app, the operator may run the same command with `--mode execute`. Before the folder
write, it repeats the read-only preflight and requires the operator to type the exact
observed account ID, home/root namespace IDs, and `APP FOLDER`. A missing,
changed, ambiguous, or mismatched fact blocks before upload. The command
creates one fresh folder with `autorename=false`, reads back its exact ID/path,
and then runs the fixed qualification cases:

```console
DROPBOX_ACCESS_TOKEN='op://Private/CAK v2 Dropbox Qualification/access_token' op run -- .venv/bin/python -m v2_retain.qualify_live --mode execute --folder /FRESH_FOLDER --expected-head REVIEWED_HEAD
```

The harness fixes six unique file destinations, at most eight planned upload
attempts, a hard reservation cap of eight unique paths and 12 upload requests,
and objects far below 1 MiB. It retains every created object and has no
destructive cleanup. Cases cover text and binary create/readback, distinct and
identical content collisions on one existing target, equal content at a
different authorized target, two local processes contending for one operation,
deliberate acknowledgement suppression, and a child killed after receiving
the provider response but before local acknowledgement. That interruption
does not prove behavior for an on-wire kill. Any exception, uncertain response,
or identity drift stops the one-shot run; it never retries an ambiguous write.

`.v2-live-qualification/<folder-name>/` is private repository-owned
qualification working state. It retains the installation/store, non-secret
preflight and request events, and on success `qualification.json` with exact
head, SDK version, actor/account, account root/home IDs, folder ID/path,
credential-reference label, date, strict-create/retry/admission configuration,
claim ceiling, invalidation triggers, case outcomes, and request count. No
resolved credential or raw SDK exception is stored or printed. A partially
completed folder/state blocks rerun; the operator reviews the retained evidence and
remote objects rather than starting automatic cleanup or replay.

Dropbox's [team-files guide](https://developers.dropbox.com/dbx-team-files-guide)
says App Folder calls are rooted implicitly in that app's folder. The
[SDK metadata route](https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html)
does not return root-folder metadata. Thus the SDK reads can verify the
account root/home IDs, readable implicit root, and exact child folder ID/path,
but cannot independently return a numeric App Folder root ID or prove the
credential's app access type. The authorized human's out-of-band App Folder confirmation is
part of the qualification evidence. A Full Dropbox token pointed at a fresh
same-named folder would not be distinguishable by these reads alone; that
residual identity limitation must stay visible in review and prevents a
stronger machine-verified App Folder claim.

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

The [accepted v2 architecture foundation](../docs/v2-architecture-foundation.md)
controls the current semantic obligations. Inputs also include the CAK-301 implementation plan 01
(`id:FHKdoRfTdTUAAAAAAAAL3g`, revision `0165b4d831d7fbb000000037baf16c3`)
and the human-accepted synthesis 02 (`id:FHKdoRfTdTUAAAAAAAAL3w`, revision
`0165b4de7738dae000000037baf16c3`, SHA-256
`77f6b487a74836b8514f3ee1892d1f3924a6b461a158d2ee87dcd99930a01914`).
Their historical experiments were not rerun or treated as current provider
proof. The authorized human explicitly authorized increments 0–2 and the bounded live run;
this repository reconciliation authorizes no new provider contact.

Accepted independent-review findings are reconciled as follows:

| Finding | Implementation assumption and boundary |
| --- | --- |
| R1 | The five accepted bounded obligations are a useful current partition, not proven irreducible or permanently minimal. The package follows the operation, not five services. |
| R2 | Candidate/property/owner/contract applicability is required. Permanent C0/C1 tests exercise actual stored decisions. Historical coverage remains unqualified. |
| R3 | Historical E3 collision-specific evidence remains insufficient. The later bounded direct-SDK run observed two typed same-target conflicts without changing the original object. |

V1 is preserved at annotated tag
`archive/v1-before-cak-301-v2-2026-09-12`, tag object
`95fc48f1d52ba7de3ff01b1186f83ab9906ce7e2`, pointing to
`f2b354ed632994f7d602dce24e78a550180f15f7`. Both identities were verified
remotely before v2 code edits. Treat this as a non-moving archive; it does not
claim a newly installed server-side tag-protection rule. Git history remains
intact and the repository was not archived.

Independent implementation review 01 accepted exact head
`9147aaeb44e692bf0d9c192e67f3b56fbbcb7218` for the Phase-A gate. Its
medium M1 finding identified missing reader-path fixture coverage; later
tests added mismatch, unavailable metadata, folder target, and multi-version
readback cases. Focused review accepted the pre-rebase head
`e6cebe4f6ee1891b56697a71b4846608a9034f66` before the completed live run.
The rebased head requires its own focused review of architecture fidelity and
the old qualification's applicability.

This remains one cohesive branch/worktree/PR. Live Dropbox requests are outside
repository validation; the completed bounded run is evidenced separately.
No bootstrap cutover, merge, auto-merge, release, or CAK-301 closure is
authorized by this implementation, its validation, or provider qualification.
