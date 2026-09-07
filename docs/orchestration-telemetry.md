# Orchestration Telemetry

## Purpose

Orchestration telemetry is lightweight local logging for AI-assisted workflow
runs. It records operational events such as orchestrator reasoning, worker-lane
progression, source-verification transitions, overlap detection, reconciliation
decisions, and final handoff notes.

This telemetry is useful because it makes a run inspectable after the fact
without turning the transcript into workflow truth. A future reviewer can
replay what the orchestrator believed, what each lane reported, where evidence
was verified, and why reconciliation happened in a particular order.

Telemetry is not a governance system, persistence layer, memory store, workflow
gate, or source of authority. It is append-only operational context.

## Boundary

Logs should remain noncanonical by default:

- Source-first retrieval still controls claims about current repository, PR,
  issue, CI, validation, branch, file, log, artifact, and provider state.
- Pull requests remain the durable evidence packet for retained code or
  documentation changes.
- Repository files, remote PRs, check runs, and validation output override any
  reported telemetry event.
- Review compression still happens at the PR or review packet boundary; logs
  preserve extra operational texture when it is useful, not every thought.
- Bounded autonomy still applies. Logs may show why an agent stopped, but they
  do not grant permission to continue, merge, release, upload, or widen scope.
- Optional logs may be kept for replay, deleted for cleanup, or ingested later
  only after an explicit human decision and under their owner's retention rules.
  Logs required for later evidence, recovery, or replay are not disposable;
  apply [storage classification](#local-shape) before relying on them.

Keeping logs append-only helps preserve the run as observed instead of
rewriting it into hindsight. If a later fact corrects an earlier report, append
a correction event rather than editing the previous event.

## Local Shape

Before capture, apply [workflow-state ownership](repo-readiness.md#repo-local-workflow-state)
and [governed-artifact capture](evidence-lifecycle.md#governed-artifact-capture):

- Keep adequate provider/runtime logs with their existing owner. For additional
  optional `events.jsonl` or `transcript.md`, use only a location and retention
  rule explicitly assigned by the owning tool or local operational contract.
  Do not create a workspace-level log directory or infer ownership from an
  available path.
- Use qualified attempt-local scratch only for disposable private mechanics
  whose loss cannot impair recovery. It must not be the sole copy of required
  evidence or replay inputs; promote and exact-verify those before cleanup.
- Retained, dependency-bearing telemetry follows the evidence lifecycle's
  admission, privacy, integrity, receipt, and recovery boundaries. Bounded
  issue-owned evidence uses that issue's permitted durable destination.
  Recurring report-only or cross-repository automation output uses its
  predeclared [operational-record location](maintenance-automations.md#authority-and-evidence-classes),
  not an issue created merely for storage. The owning workspace/storage
  contract supplies concrete locators and retention; this page creates none.
- If ownership, retention, or a permitted route is unavailable, omit optional
  capture and report the gap. Required evidence fails closed under the evidence
  lifecycle; do not substitute the workspace root or current directory.

`events.jsonl` carries replay-friendly structured events; `transcript.md`
carries compact human-readable notes, decisions, and reconciliation summaries.
Neither file is canonical workflow state. Preserve corrections by appending;
freeze retained artifacts under new immutable identities rather than editing
prior evidence.

Optional telemetry does not introduce databases, ingestion daemons, telemetry
agents, centralized orchestration frameworks, CI gates, automatic uploads, or
cloud dependencies. Any required durable capture uses its existing owner and
authorized route; telemetry itself grants no retention or upload authority.

## Event Shape

Use a flexible JSONL event shape. These fields are recommended, not a strict
schema contract:

```json
{
  "ts": "ISO8601 timestamp",
  "run_id": "workflow run identifier",
  "role": "orchestrator|worker|reviewer",
  "lane": "optional lane identifier",
  "repo": "repository name",
  "event": "event type",
  "summary": "human-readable summary",
  "source_ref": "optional PR/issue/file/check reference",
  "verification_state": "reported|verified|partial|blocked",
  "severity": "info|notice|warning|error",
  "next_action": "optional next step"
}
```

Prefer short summaries that a human can scan with `jq`, DuckDB, Loki,
OpenTelemetry tooling, or plain text tools later. Add fields only when they
make the run easier to inspect. Avoid stable taxonomies until repeated
operational use proves they are worth standardizing.

Recommended verification-state meaning:

- `reported`: a worker, tool, or transcript reported the state, but the
  orchestrator has not verified the controlling source.
- `verified`: the controlling source has been inspected for the claim being
  logged.
- `partial`: some evidence was verified, but required state remains unknown.
- `blocked`: verification could not complete because access, tooling, source
  availability, or scope prevented it.

## What To Capture

Useful events are sparse and decision-oriented:

- run started, scope, repository, and validation path
- lane launched, lane ownership, and explicit exclusions
- source retrieval requested, completed, partial, or blocked
- worker report received and whether it is only reported or directly verified
- overlap, ownership-boundary, or dependency detected
- reconciliation order selected or revised
- validation started, passed, failed, or blocked
- stop condition reached
- final summary, residual risk, and next human-controlled step

Avoid logging secrets, tokens, private account details, broad filesystem
inventories, hidden platform state, or raw prompt dumps containing unrelated
private context.

## Example Prompt Add-On

This add-on can be appended to an orchestration prompt when local telemetry is
useful. It is illustrative, not mandatory.

```text
Optional local telemetry:
- Apply `docs/orchestration-telemetry.md#local-shape` and its linked ownership
  and evidence contracts before append-only capture. Keep adequate runtime logs with their
  owner; otherwise use `[declared-tool-owned-run-location]` only when its owner
  explicitly permits `events.jsonl` and `transcript.md` with a retention rule.
- Omit optional capture and report an unavailable owner/route; required evidence
  fails closed. Never fall back to workspace logs or the current directory.
- Use `events.jsonl` for sparse JSONL events and `transcript.md` for compact
  orchestration notes. Required replay/evidence belongs in its natural durable
  owner, not solely in disposable attempt-local scratch.
- Record lane lifecycle events, source-retrieval attempts, reported-vs-verified
  transitions, overlap or ownership-boundary discoveries, reconciliation
  decisions, validation results, stop conditions, and residual risks.
- Mark each event's verification state as `reported`, `verified`, `partial`, or
  `blocked`.
- Treat logs as noncanonical operational telemetry. Do not use them to replace
  source-first retrieval, PR evidence, canonical validation, or human approval.
- Do not create databases, background agents, upload behavior, CI gates, or
  replay-driven automation.
```

## Why Preserve Reasoning

Orchestrator reasoning can be operationally valuable when it remains bounded
and inspectable. It shows why lane boundaries were chosen, where source-first
discipline was applied, when worker reports were still unverified, and why a
reconciliation order changed.

That record helps diagnose workflow misses without promoting the transcript
into memory or policy. The useful distinction is: logs explain how a run
unfolded; authoritative sources decide what is true now.
