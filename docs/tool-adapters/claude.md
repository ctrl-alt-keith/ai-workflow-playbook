# Claude Adapter

Claude-specific deltas for Claude Chat, Claude Cowork, and Claude Code. Use
with [`start-here.md`](../start-here.md), [`core-model.md`](../core-model.md),
[`source-first-retrieval.md`](../source-first-retrieval.md),
[`repo-readiness.md`](../repo-readiness.md), and the target repo's
`AGENTS.md`; shared rules stay in their canonical docs.

## Surfaces

Map each surface through the core
[surface roles](../core-model.md#interactive-and-execution-surfaces) and
[locality classes](../core-model.md#surface-classes):

- **Claude Chat**: interactive, conversational, no repository filesystem.
  Instructions for Claude are account-wide; project instructions apply only
  inside that project. Repository content arrives only through explicitly
  selected GitHub content, project knowledge, or another observed route;
  retrieval is best-effort per thread.
- **Claude Cowork**: interactive steering plus bounded execution. Sessions
  run in the cloud on every surface: agentic-remote by default, agentic-local
  only while a desktop-connected repository folder is attached. Scheduled
  Cowork is unattended. Dispatch is a human assignment that runs without the
  human present; Anthropic documents it as unavailable to new accounts, so its
  presence is runtime evidence.
- **Claude Code**: interactive and execution roles when human-driven; a
  controller-launched run is an execution surface. Agentic-local with the
  repository filesystem, otherwise agentic-remote until current sources and
  repo-local instructions are available.

Chat-to-Cowork transitions apply the
[interactive-to-execution consent boundary](../core-model.md#interactive-to-execution-transition-consent).
Controller-launched independent review applies
[Local Read-Only Reviewer Launch](#local-read-only-reviewer-launch).

## Hydration Transport

Apply the
[global bootstrap router](../../distributions/global-bootstrap/bootstrap-router.md)
and its [persistence boundary](../start-here.md#global-bootstrap-persistence)
at each independently starting Claude surface. Persistent instructions trigger
hydration; they do not prove success or source freshness.

- **Account transports.** Instructions for Claude is account-wide, not
  Chat-only; project instructions do not replace it. Treat each
  `user_preferences` block a run exposes as an independently observed
  transport until ownership and precedence are established. Cowork Global
  instructions are a separate field or part of Instructions for Claude
  depending on the current Claude experience; the field the runtime exposes
  is the transport. Anthropic publishes no precedence among these: verify each
  independently, and apply a router presented more than once only once.
- **Chat.** Router in the verified account transport; project instructions
  stay project-specific. Prefer explicitly selected current GitHub content; a
  prior project sync is not current-source evidence. If a required source
  cannot be retrieved after the
  [runtime-evidence rule](../start-here.md#connector-availability-is-runtime-evidence),
  stop the repository-dependent task.
- **Cowork.** Router in verified Global instructions; project or folder
  instructions stay thin pointers. Without a global transport, an interactive
  task may proceed only from a verified task, project, or folder trigger that
  obtains the required sources; record the gap. Unattended tasks stop when no
  qualified current-source route exists. Desktop Cowork skips
  outside-working-directory imports and linked user files; cloud, web, and
  mobile Cowork cannot rely on a workstation `~/.claude/CLAUDE.md`.
- **Code.** File-backed `CLAUDE.md` discovery below. A repo-local `CLAUDE.md`
  may point to `docs/start-here.md` and `AGENTS.md` but does not replace them.
  Remote Code retrieves them through the workspace or another observed route,
  or stops.

The remaining sections are Claude Code-specific unless stated otherwise.

## Instruction Discovery

Claude Code loads managed policy, then `~/.claude/CLAUDE.md`, then `./CLAUDE.md` or
`./.claude/CLAUDE.md`, then project-local instructions, concatenated: load
order is context order, not authority, and user-level `~/.claude/CLAUDE.md`
cannot override repo-local policy. Claude Code loads `CLAUDE.md`, not
`AGENTS.md`, unless imported or read: read `AGENTS.md` explicitly, keep
`CLAUDE.md` a thin pointer, and apply the
[repository instruction hierarchy](../start-here.md#repository-instruction-hierarchy).

Install the router in `~/.claude/CLAUDE.md` as an inline marked block per the
[distribution README](../../distributions/global-bootstrap/README.md); not as
an outside-working-directory import, symlink, or hard link (desktop Cowork
skips those). Keep the HTML markers: Claude Code strips them from context, the
drift validator needs them.

## Interaction Mode And Permission Mode

Select the playbook interaction mode first
([preflight](../repo-readiness.md#interaction-mode-preflight)); it expresses
intent and authority. Choose the Claude Code permission mode (`default`,
`plan`, `acceptEdits`, `bypassPermissions`) from the task's tool needs and
blast radius, never by inference from the interaction mode:

- Review/audit needs read-only shell (`git status`, `git diff`, `gh pr view`,
  `make check`): pick a mode that permits those reads and withholds write
  approval; `plan` is not the automatic choice.
- Implementation: `default` (per-action approval); `acceptEdits` only for a
  bounded, already-agreed scope.
- Permission rules evaluate `deny` -> `ask` -> `allow`, first match wins:
  prompting behavior, not an authorization boundary.
- `bypassPermissions` is documented for isolated containers or VMs only. Do
  not use it for repository work with meaningful blast radius; `deny` rules are
  not a safety boundary under it.

Permission mode changes capability, not
[authority](../core-model.md#authority-and-transitions).

## Command Execution

Bash commands run as separate processes: in the main session a working
directory change carries over only within the project or added directories,
shell environment never persists, and subagent working directories never
persist. Use direct single-purpose commands per the
[command-form rule](../repo-readiness.md#command-form-and-intent-visibility);
parallelize only independent read-only inspection. There is no writable-root
sandbox: apply
[repo-local workflow state](../repo-readiness.md#repo-local-workflow-state).

### Local Read-Only Reviewer Launch

Only when launching or interpreting a local `claude-review` or `codex-review`
attempt. Apply [`external-ai-reviewer.md`](../external-ai-reviewer.md) and
[`review-launchers.md`](../../scripts/review-launchers.md) first; the latter
owns records, diagnostics, redaction, runtime qualification, and incident
interpretation.

- Use the active Playbook checkout's launcher with its explicit absolute
  provider binary, invoked from the checkout under review, bound to the exact
  `--candidate-commit`; a mismatch stops before review. Keep the launch behind
  per-action approval, never an auto-approving mode.
- Run the launcher's required preflight before an expensive review.
- Claude: a qualified authentication failure (exit 78) requires the operator
  to log in again through the Claude CLI in their own interactive session,
  then rerun the unchanged preflight and review. Do not drive that login,
  mutate auth or session files, or retry automatically; restored
  authentication is capability, not evidence, and does not revive the failed
  attempt.
- Every other Claude failure, and every Codex failure, is generic launcher
  failure: not review evidence, not a verdict, not grounds for silent
  reviewer substitution.
- Retained diagnostics are evidence only when the terminal record says
  `diagnostics_file: written`; otherwise preserve the failed attempt and stop
  at the selected-review boundary.
- Codex: exact `--model` selector, successful selector-acceptance canary, and
  post-review effective model/effort matching the request; missing or
  mismatched effective evidence fails closed with no fallback.
- Launcher controls do not establish total isolation: operator-layer
  instructions and configuration stay outside them. Keep that visible when
  qualification relies on isolation.

## Worktrees And Subagents

Claude Code spawns subagents with the `Agent` tool (`Task` is a retained
alias for the same tool). A call selects the
subagent with `subagent_type` and may set `isolation: worktree` for a
temporary git worktree branched from the default branch. Resume a completed
subagent with `SendMessage` to its agent ID or name; Explore and Plan are
one-shot.

A non-fork subagent receives the delegation message and the `CLAUDE.md`
hierarchy (including `~/.claude/CLAUDE.md` and any `AGENTS.md` loaded as
project instructions), not the parent conversation, invoked skills, or
previously read files; `fork` inherits the parent conversation. Give each
non-fork subagent the standalone envelope from
[`orchestration-and-parallelism.md`](../orchestration-and-parallelism.md) and
apply [PR topology](../repo-readiness.md#pr-readiness). Claude Code's own
worktrees live under `.claude/worktrees/` and do not satisfy a repo-local
`.worktrees/` isolation policy. With agent teams enabled, a named
`Agent` call can launch a teammate in the main working directory regardless of
frontmatter `isolation`.

A harness default that discourages unprompted delegation is executor
behavior, not doctrine: report it as a runtime observation and apply the
Playbook's fan-out guidance.

## Context Compaction

Claude Code auto-compacts and supports `/compact`, `--resume`, and
`--continue`. Treat the summary as navigation; refresh mutable state under
[`source-first-retrieval.md`](../source-first-retrieval.md) and
[durable continuity](../core-model.md#durable-continuity).

## Connectors

Remote services are MCP connectors: apply the
[runtime-evidence rule](../start-here.md#connector-availability-is-runtime-evidence)
and the GitHub route in
[`review-packet.md`](../review-packet.md#direct-pr-inspection).

### Issue-Owned Durable Prompt Retrieval

When Claude receives an exact issue-owned prompt through a permitted Airtable
route, apply the
[Airtable canonical-text handoff](../prompts.md#airtable-canonical-text-handoff)
and the
[issue-owned handoff profile](../prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile):
use the envelope's exact base, table, and record IDs; retrieve with the exact
`recordIds` constraint and require exactly one result; no fuzzy search or key
lookup. Fail closed on a missing, duplicated, stale, transformed, truncated,
or mismatched record; never substitute a local file or reconstructed chat
text. Retrieval grants no read-only mode and no authority: choose tools,
permission mode, and persistence from the owning task or reviewer contract.

When producing the handoff: create one new five-field record, capture the
returned ID and creation time, retrieve that exact ID with `recordIds`,
complete the shared verification, then emit the envelope from that verified
identity. Never update a frozen record; a correction is a new record with
external lineage.

## Model And Effort Routing

Apply [model routing](../model-routing.md); do not map from OpenAI model
names or tiers. Claude Code defines `haiku` (simple fast tasks), `sonnet` (daily coding), `opus` (complex
reasoning), `fable` (hardest, longest-running tasks), and `best` (Fable where
available, else `opus`). Model IDs, availability, context variants, and
allowlists are runtime evidence. Fable needs a current Claude Code version;
under zero data retention its availability follows the Covered Models policy. Fable and Opus 5 safety
classifiers can trigger documented fallback: request Fable only when its
effective runtime identity can be observed and meets the task's
qualification.

| Claude task class | Default Claude Code model | Thinking/effort guidance | Escalate when | Downgrade/follow up when |
| --- | --- | --- | --- | --- |
| Deterministic external verification; hashes, inventories, evidence citations; simple source inspection; mechanical fallback verification | `haiku` | Use executor default; Claude Code does not document effort control for Haiku | a result is ambiguous, changes a decision, or source access is insufficient | substantive review has converged and a qualified deterministic check remains |
| Implementation review; evidence-package review; reviewer follow-up after substantive convergence; bounded long-context evidence synthesis | `sonnet` | Use the documented default (`high` absent an organization default); use `medium` or `low` only as an explicit cost/latency trade-off where bounded evidence supports it | residual findings repeat, evidence conflicts, or semantics remain unresolved | split inventories, hashes, and other externally checkable claims to Haiku or another qualified mechanism |
| Substantive adversarial code review; protocol/design review; architecture review; authority or security-boundary review | `opus` | Use the model's documented default; do not assume `xhigh` applies to every Opus runtime | a new trust boundary, unresolved architecture/security implication, conflicting authority, or a finding that changes qualification disposition appears | after substantive convergence, delegate only the remaining mechanical claim; do not relabel it as substantive review |
| Especially hard long-running investigation, outage/root-cause work, or architecture decision that exceeds a normal Opus review | `fable`, where available | Adaptive reasoning is always on; use the documented default (`high` absent an organization default), and reserve `xhigh`/`max` for a bounded demonstrated need | a safety fallback, unavailable Fable runtime, or remaining decision risk defeats the qualification requirement; stop, seek an explicit human decision, or use another independently qualified mechanism | keep Fable out of routine review and delegate only bounded deterministic follow-up |

Effort is separate from model choice. Use Claude Code's own values (`low`,
`medium`, `high`, `xhigh`, `max`), not the Playbook's `light`/`medium`/`high`
classes as numeric equivalents; accepted values per model are runtime
evidence. Documented default: `high`, except Opus 4.7 (`xhigh`) and an
organization default effort on its organization default model. Lowering
effort is the primary cost/latency lever. Do not invent a Haiku effort
setting. A prompt-contract reasoning class (`light`, `medium`, `high`) maps
to the model and effort selected here; fail closed when the surface cannot
meet a mandatory requirement.

Requested and effective configuration differ: `opusplan` switches Opus to
Sonnet at execution, fallback chains and safety-classifier fallback
substitute models with a transcript notice, and `/status` shows the current
model. For governed work record requested and effective model/effort and any
substitution; if effective identity is unavailable, record the limitation.
Requalify, escalate, or stop only when the effective result violates a
required capability or an exact-model reviewer qualification.

### Thread Routing

Apply the shared `FRESH THREAD`, `SAME THREAD`, and `CHILD TASK` vocabulary in
[`prompts.md`](../prompts.md#thread-routing-and-configuration-continuity):
FRESH THREAD selects this table's model and effort; SAME THREAD preserves the
parent configuration. No executor-applied visible-thread naming exists:
resolve `[resolved thread-name section when applicable]` to nothing and do not
ask Claude to rename itself or report a naming limitation.

### Prompt Operator Metadata

Precede an operator-prepared Claude prompt with one metadata block:

```text
Operator metadata (do not include in prompt)
Thread routing: <FRESH THREAD | SAME THREAD | CHILD TASK>
Recommended model: <FRESH THREAD/CHILD TASK: haiku | sonnet | opus | fable; SAME THREAD: Preserve requested thread model and observe effective runtime model; UNVERIFIED FROM AUTHORING SURFACE: resolve with the operator at launch>
Recommended thinking/effort: <FRESH THREAD/CHILD TASK: supported executor setting; SAME THREAD: Preserve requested thread setting and observe effective runtime setting; UNVERIFIED FROM AUTHORING SURFACE: resolve with the operator at launch>

Reason:
<one concise task-specific selection or continuity justification>
```

The metadata is guidance, not authority. Do not recommend a model, effort, or
child configuration the surface cannot support, and do not tell the
downstream task to change or preserve parent configuration when the surface
exposes no such control. The task body must be complete without the
metadata, may authorize child dispatch only where the surface supports it,
and carries requested/effective runtime evidence when validation or
qualification requires it. Record `UNVERIFIED FROM AUTHORING SURFACE` for an
unverified control and resolve it at launch; do not present it as
unavailable.

## Environment Preflight

Before driving repository automation or worker fan-out, run
`./scripts/codex-preflight` from the Playbook checkout (GitHub SSH, `gh`
auth, repository reachability) and stop on a non-zero exit.

## Delivery

Follow [`repo-readiness.md`](../repo-readiness.md) and repo-local
`AGENTS.md`. Report completion per the
[successful completion projection](../core-model.md#successful-completion-projection):
PR and status, validation and review summary, exact head when useful, stop
boundary; add file, blocker, risk, or forensic detail only when it changes
operator action.

## References

Runtime claims were checked against official Anthropic documentation on
2026-09-19 (Claude Code and platform) and 2026-09-21 (Claude Chat and
Cowork); the sources are recorded in the PR that last changed each claim.
