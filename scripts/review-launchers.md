# Review Launchers

Read this reference only when launching `claude-review` or `codex-review`,
interpreting an attempt record, or maintaining those launchers. The launchers
and their tests are executable truth. This page explains their evidence and
diagnostic contract; shared reviewer selection, exact-candidate, authority, and
finding-disposition rules remain in
[`external-ai-reviewer.md`](../docs/external-ai-reviewer.md).

## Shared launcher boundary

Use a repository-owned launcher from the active Playbook checkout with its
explicit absolute provider binary. It passes only model and effort options,
delivers the prompt on standard input, and binds the current checkout to the
requested exact candidate immediately before review. A candidate mismatch stops
the launch rather than selecting a different candidate. Empty or failed provider
output is launcher failure, never a review verdict.

Preflight is a bounded canary before expensive review. It establishes neither
candidate quality nor a guarantee for the later review. The launcher supplies
the configured read-only controls; its configured envelope is a declaration,
not a runtime receipt. The reviewer must still report sources actually
inspected and access gaps. Launcher controls do not establish total reviewer
isolation: operator-layer instructions and configuration can remain outside
launcher control.

## Attempt records and diagnostics

An attempt that runs carries the exact `configured_envelope` it used. A failure
before the launcher validates enough requested selection/configuration to
construct that envelope has no envelope or runtime evidence; a later pre-launch
failure retains the intended envelope as a declaration only. Acceptance canaries
and substantive reviews are separate attempts with their own envelopes.
If a Codex selector-acceptance canary fails, its `acceptance` record retains that
canary's configured envelope and evidence. There is no top-level substantive
review envelope because the substantive review never started.

When `--diagnostics-file` is requested, its terminal state is one of
`written`, `not_created`, `incomplete`, or `unknown`. The file's own bytes say
`diagnostics_file: unverified`; only the terminal stderr record can establish
`written`. Every state other than `written` fails the attempt, and no destination
path is deleted. States are about the attempt-created artifact, not the pathname
namespace; see `write_record()` for the exact identity and close behavior.

Failures preserve all causes in priority order: provider exit, unacceptable
output, effective-selection failure, scratch cleanup, then diagnostics write.
An established Claude authentication failure takes precedence and retains exit
78. The detailed cause construction and terminal exit policy remain in
`review_launcher.py`.

## Retention and redaction

Wrapper-owned structured evidence is validated at ingress and retained exactly:
configured envelope, requested selection, candidate, exit/status, and artifact
state. A provider-derived effective selector is retained exactly only after
structural qualification and validation; malformed or overlong values fail
instead of being truncated into a different selector.

Provider stdout/stderr, version and OS-error text, and failure causes are
bounded and redact recognized credential structures. Redaction is deliberately
non-comprehensive: it does not prove arbitrary provider prose is secret-free.
See `redact()` and its tests for the recognized structures and bounds.

## Provider deltas

### Claude

Claude receives read-only `Read`, `Grep`, and `Glob`, non-interactive
permissions, no memory/session persistence or slash commands, and an empty MCP
configuration. Its preflight uses the effective account context. Only the
qualified Claude diagnostic surface can establish authentication failure: that
case exits 78 and requires operator reauthentication. Wrong canary output,
timeout, empty output, and other provider failures are generic exit 70;
substantive review prose is not an authentication diagnostic surface.

For controller-supplied evidence, pass `--evidence-bundle` with the absolute path
of a fresh private attempt-local bundle staged under the
[`review-evidence.md`](review-evidence.md) contract. This is the shared Claude/Codex
review-execution contract; it is never accepted for an auth preflight. The launcher verifies local structure, permissions,
bytes, and the manifest before invoking the provider executable, including its
version probe. It requires an `applicable` repository-commit candidate matching
the observed HEAD and the locally configured GitHub origin (`https`, SSH, or
SCP-style URL). Other origins and immutable-artifact review candidates are not
supported by this repository-review launcher.

The existing local read-only tool set receives one additional directory via
the documented [`--add-dir` option](https://docs.anthropic.com/en/docs/claude-code/cli-usage)
(checked 2026-09-19); the bundle remains controller-owned and is neither copied nor
deleted by the launcher. Bundle verification repeats before and after review;
a failure suppresses the review result. The controller must preserve required
evidence before disposing of its attempt directory. Only the selected bundle is
supplied as external evidence; the candidate checkout remains the separate
repository-review surface.

Diagnostics retain the validated manifest and its canonical JSON SHA-256
(`sort_keys=True`, compact separators, ASCII escaping, UTF-8, no trailing
newline). They distinguish local verification from controller-supplied provider
claims, reviewer self-report in the review output, and unobservable live provider
state/runtime capability. The `network_access.granted` field describes only
launcher-configured tool capability. It is not a process-level network sandbox,
an observation of runtime reach, or a claim about provider inference transport.
The launcher does not authenticate the controller's claims, prove issue
ownership/current Dropbox state, or infer actual reads from bundle delivery.
The `configured_local_bundle` diagnostic access value means only that the wrapper
rendered the selected bundle path into the provider command. It is deliberately
not a claim that a provider's directory option alone proves read-only filesystem
confinement. Permissions and revalidation do not exclude concurrent same-user mutation or
establish filesystem confinement of every provider read. Operator-layer and
provider-native residuals remain unobservable pending separately authorized
real-provider qualification; deterministic fixtures do not qualify them.

### Codex

Codex requires an exact `--model`. Its catalog check is a cheap fail-closed
observation, not acceptance: `codex debug models` is undocumented, does not
take `--ignore-user-config`, and can return the bundled catalog when
unauthenticated. Before the review prompt is delivered, the selector-acceptance
canary must succeed with the requested model and effort. The review then must
independently report matching effective model and effort; the canary never
stands in for that evidence, and exact-model qualification does not fall back.

Effective selection comes only from the finite sequential stderr-prefix parser
observed for `codex-cli 0.154.0`. A missing, changed, reordered, duplicated,
unknown, displaced, malformed, or overlong element yields no effective evidence.
This syntactically qualifies a free-form stream, not provider provenance; a
runtime-layout change fails closed unless it is syntactically indistinguishable.
See `runtime_layout()` for the accepted grammar.

Codex's configured controls are read-only sandbox, never approval,
ignored user configuration, ephemeral/no-history execution, disabled web/apps,
and suppressed candidate `AGENTS.md`. Candidate project-layer suppression is a
trust/config derivation, not an observed runtime fact; network reach is likewise
unestablished. Operator-layer `CODEX_HOME` instructions and configuration remain
outside launcher control. No Codex stderr position qualifies authentication, so
every failed Codex canary or review, including auth-shaped output, is generic
exit 70 with bounded retained diagnostics.

For the same controller-supplied `--evidence-bundle` contract, the substantive
Codex review receives the selected path through `codex exec --add-dir`; the
selector-acceptance canary intentionally does not receive it. The wrapper keeps
Codex's read-only sandbox configuration and disables web/apps, then repeats the
same pre-launch candidate binding, local verification, and post-review
revalidation used for Claude. Current Codex CLI help describes `--add-dir` as an
additional directory writable alongside the workspace; the wrapper therefore
records the path only as `configured_local_bundle`, rather than claiming that the
option itself proves confinement. The configured sandbox/web/apps restrictions
are configuration evidence, while actual runtime network, MCP, connector, and
filesystem capability remain unobservable here. As with Claude, supplied bytes
are controller-supplied evidence, never a reviewer claim of independent Dropbox
or other provider observation.
