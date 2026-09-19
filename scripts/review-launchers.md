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

Preflight is a bounded canary before expensive review. It establishes route and
authentication acceptance only; it establishes neither candidate quality nor a
guarantee for the later review. The launcher supplies the configured read-only
controls; its configured envelope is a declaration, not a runtime receipt. The
reviewer must still report sources actually inspected and access gaps. Launcher
controls do not establish total reviewer isolation: operator-layer instructions
and configuration can remain outside launcher control.

## Substantive health probe

`--health-probe` is the low-cost step between auth preflight and a real review.
Run it from the exact candidate checkout with the same absolute provider binary,
selection, new absolute `--diagnostics-file`, and exact `--candidate-commit`.
It accepts no stdin prompt. The shared launcher binds the candidate, verifies a
fixed opaque one-line `scripts/reviewer-health-probe.txt` fixture, and asks the
reviewer to return that file's contents exactly.

The probe uses the substantive provider envelope, candidate checkout, output
capture, scratch lifecycle, and terminal diagnostics path. Codex still runs its
separate selector-acceptance canary before the probe; that canary does not see
the fixture or probe prompt. The terminal stderr record has `attempt_kind:
health_probe`, identifies the fixture and expected output, and reports the
normal diagnostics-file state. A successful probe is evidence that the
configured substantive path returned the expected local-fixture content through
response capture and terminal diagnostics. It does not prove full-review
success, general filesystem confinement, runtime isolation, or absence of
Dropbox, network, MCP, connector, or other provider capability.

Interpret a returned probe only through its terminal record:

- expected fixture content with `diagnostics_file: written` is the minimum
  substantive-path evidence;
- no output, a wrong value, or a provider exit is a substantive-path failure
  with the launcher classification retained;
- any diagnostics state other than `written` is a diagnostics-finalization
  failure even when the provider returned `1`.

Use it for a controlled main-versus-candidate comparison by holding the exact
candidate commit, provider selection, binary, and diagnostics handling fixed
while changing only the launcher source being compared. It is diagnostic
evidence, not a retry policy and not a substitute for the governed
exact-candidate review.

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
