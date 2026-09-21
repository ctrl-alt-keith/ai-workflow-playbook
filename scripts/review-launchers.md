# Review Launchers

Use this reference when launching `claude-review` or `codex-review`,
interpreting an attempt record, or maintaining those launchers. The launchers
and tests are executable truth. Shared reviewer selection, exact-candidate,
authority, and finding-disposition rules remain in
[`external-ai-reviewer.md`](../docs/external-ai-reviewer.md).

## Shared launcher boundary

Use the active checkout's repository-owned launcher and an explicit absolute
provider binary. It binds the checkout to the requested exact candidate before
review; a mismatch stops the launch. Review prompts arrive on standard input;
canaries and probes use fixed prompts. Empty or failed provider output is
launcher failure, never a review verdict.

Before substantive review, retain one persistent session and deliver the prompt
through an EOF-producing route. Presentation timeout, quiet output, or a lost
session handle requires re-observation of the recorded launcher command,
candidate, and output destinations; a matching live process remains the same
attempt. Do not launch a successor before observed terminal state and contract
eligibility. Termination follows
[`orchestration-and-parallelism.md`](../docs/orchestration-and-parallelism.md#live-process-lifecycle).

Preflight establishes only route and authentication for that process context.
Its configured envelope declares requested controls; the reviewer still reports
sources actually inspected and access gaps. Operator-layer instructions and
configuration remain outside launcher control.

## Substantive health probe

Run `--health-probe` from the exact candidate checkout with the same absolute
binary, selection, fresh absolute `--diagnostics-file`, and exact
`--candidate-commit`. It ignores standard input, verifies
`scripts/reviewer-health-probe.txt`, and returns its contents exactly. Codex
runs selector acceptance before the probe; that canary sees neither fixture nor
probe prompt.

Interpret the returned probe through its terminal record or qualified
[diagnostics readback](#attempt-records-and-diagnostics):

- expected fixture content with `diagnostics_file: written` passes;
- no output, wrong output, provider exit, or another diagnostics state fails;
- the probe is diagnostic evidence, not a retry policy or review verdict.

## Attempt records and diagnostics

Each attempt carries the exact `configured_envelope` it used. Failures before
envelope validation have no envelope or runtime evidence. Acceptance canaries
and substantive reviews have separate envelopes; a failed Codex canary retains
only its acceptance record.

For `--diagnostics-file`, terminal state is `written`, `not_created`,
`incomplete`, or `unknown`. The file says `diagnostics_file: unverified`; only
the terminal record establishes `written`. A qualified post-execution observer
may instead use `verify_diagnostics_readback()` after independently observing
zero launcher exit and retaining the exact fresh requested path; it binds file
identity, raw-byte digest, provider, attempt kind, successful result, candidate,
and requested selection. Any other state fails the attempt and leaves the
destination untouched.

Failures retain ordered causes: provider exit, unacceptable output,
effective-selection failure, scratch cleanup, then diagnostics write. A
qualified Claude authentication failure takes precedence and exits 78; detailed
construction and terminal exit policy remain in `review_launcher.py`.

### Exact review-output capture

For a governed substantive review only, `--review-output-file` can retain the
provider-extracted response as raw bytes before stdout presentation. The path
must be a new absolute pathname beneath an existing directory. Creation is
exclusive and private (`0600`); the launcher binds the created regular-file
identity while its write descriptor remains open, then reads that same identity
back with `O_NOFOLLOW` as raw bytes and records its byte length and SHA-256
beside the candidate and terminal diagnostics record. A capture failure fails
the attempt and leaves any residue for the owning attempt rather than
overwriting or deleting it. If a provider attempt itself fails but produced
bytes, the launcher may still retain those exact bytes; they remain failed-
attempt residue and are not admissible merely because a capture file exists.

The capture file is attempt evidence, not automatic durable admission,
acceptance, reviewer correctness, or runtime-isolation evidence. Its exact
bytes—not terminal stdout presentation—are the recoverable source for a later
authorized storage-admission step. Preflight, selector-acceptance canaries,
and health probes reject this option and cannot create review-output artifacts.

## Retention and redaction

Retain configured envelope, requested selection, candidate, exit/status, and
artifact state exactly. Retain effective selection only after structural
qualification. Bound and redact provider stdout/stderr, versions, OS errors,
and failure causes; redaction does not establish that arbitrary prose is
secret-free.

## Provider deltas

### Claude

Claude uses read-only `Read`, `Grep`, and `Glob`, non-interactive permissions,
no memory/session persistence or slash commands, and an empty MCP configuration.
Only the qualified Claude diagnostic surface establishes authentication failure:
it exits 78 and requires operator reauthentication. Other preflight or review
failures exit 70.

### Codex

Codex requires an exact `--model`. Its catalog check is a pre-task observation,
not authentication or selector acceptance. Before delivery, the
selector-acceptance canary must succeed with the requested model and effort;
the review must independently report matching effective selection. Missing,
changed, reordered, duplicated, unknown, displaced, malformed, or overlong
elements in the finite stderr-prefix parser produce no effective evidence.

Codex configures a read-only sandbox, no approval, ignored user configuration,
ephemeral/no-history execution, disabled web/apps, and suppressed candidate
`AGENTS.md`. Candidate project suppression and network reach remain
unestablished; operator-layer `CODEX_HOME` instructions/configuration remain
outside launcher control. Every failed Codex canary or review exits 70 with
bounded diagnostics.
