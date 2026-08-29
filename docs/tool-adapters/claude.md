# Claude Adapter

Claude Code-specific deltas on top of the core playbook. Use with
[`start-here.md`](../start-here.md), [`core-model.md`](../core-model.md),
[`source-first-retrieval.md`](../source-first-retrieval.md),
[`repo-readiness.md`](../repo-readiness.md), and the target repo's `AGENTS.md`.
Record only what differs for Claude Code here; shared rules stay in their
canonical docs.

## Instruction Discovery And Precedence

[Claude Code's current memory guidance](https://code.claude.com/docs/en/memory)
documents four instruction scopes in broad-to-specific load order: managed
policy, user instructions at `~/.claude/CLAUDE.md`, project instructions at
`./CLAUDE.md` or `./.claude/CLAUDE.md`, and personal project-local
instructions. Project instructions appear in context after user instructions,
and discovered files are concatenated rather than one scope overriding another.
Claude Code reads `CLAUDE.md`, not repo-local `AGENTS.md`,
unless the latter is imported or explicitly read; yet `AGENTS.md` is the
canonical repository execution layer the startup contract requires. Therefore:

- Explicitly read the target repository's `AGENTS.md`; do not assume auto-loaded
  memory covers repo-local policy.
- Do not fork `AGENTS.md` or shared doctrine into a `CLAUDE.md`. If a `CLAUDE.md`
  exists, keep it a thin pointer to `docs/start-here.md` and the repo's
  `AGENTS.md`, not a second policy source. See
  [`repo-readiness.md`](../repo-readiness.md#agentsmd-responsibilities).
- Memory files are a transport for instructions, not an authority layer. The
  [Repository Instruction Hierarchy](../start-here.md#repository-instruction-hierarchy)
  governs; a user-level `~/.claude/CLAUDE.md` is operator context and does not
  override repo-local policy. The documented load order places project
  instructions after user instructions, but load order is context ordering,
  not authority transfer.
- For the broader CAK-187 provider rollout, use the copy-ready
  [`global bootstrap router`](../../distributions/global-bootstrap/bootstrap-router.md)
  as an inline marked block in the regular user-level file. It applies the shared
  [`global bootstrap persistence`](../start-here.md#global-bootstrap-persistence)
  timing invariant across repositories; it is not a per-turn retrieval rule.
  Validate a completed local Claude rollout with
  `python3 scripts/check_global_bootstrap.py --require-claude` from the Playbook
  repository.
- Do not implement the user-global router as an import that resolves outside a
  Cowork session's working directory, or as a symlink or hard link. Claude Code
  documents that Cowork desktop skips those user-scope imports and skips a
  linked `~/.claude/CLAUDE.md`. The inline managed block remains available in
  Cowork without either indirection.
- Keep the managed HTML markers around the inline router. Claude Code strips
  block-level HTML comments before injecting `CLAUDE.md` content into context,
  so the markers remain available to the drift validator without consuming
  model context or becoming model instructions.

## Interaction Mode And Permission Mode

These are two separate axes. The playbook interaction mode (implementation,
review/audit, orchestration/prompt-authoring) expresses intent and authority;
select it first via the
[interaction-mode preflight](../repo-readiness.md#interaction-mode-preflight).
Claude Code's permission mode (`default`, `plan`, `acceptEdits`,
`bypassPermissions`) controls execution capability. Choose the permission mode
from the task's actual tool requirements and blast radius, not by inferring it
from the interaction mode.

- Review/audit work usually needs read-only shell such as `git status`,
  `git diff`, `gh pr view`, and `make check`. Choose a mode that permits those
  reads while withholding write/mutation approval; do not assume `plan` mode is
  the right default merely because the interaction mode is review/audit.
- For implementation, prefer per-action approval (`default`); reserve broader
  auto-approval (`acceptEdits`) for bounded, already-agreed scope.
- Verified evaluation: permission rules are checked `deny` -> `ask` -> `allow`,
  first match wins. This is approval/prompting behavior, not an authorization
  boundary.
- `bypassPermissions` skips approval prompts; Anthropic documents it for use
  only in isolated environments such as containers or VMs. Do not use it for
  repository work with meaningful blast radius, and do not treat repository-level
  `deny` rules as a sufficient safety boundary under it.

Approval is capability, not authority
([`core-model.md`](../core-model.md#authority-and-transitions)). Being allowed to
run a tool does not authorize merge, release, tag, destructive, or externally
visible actions; those remain human-gated (see
[Delivery And Stop Conditions](#delivery-and-stop-conditions)).

## Command Execution

Claude executes Bash commands as separate processes. In the main session,
working-directory changes may carry over within the project or explicitly added
directories, but shell environment changes such as `export`, `source`, aliases,
and virtual-environment activation do not persist between calls; subagent
working-directory changes do not persist. Keep commands self-contained and
follow the
[command-form rule](../repo-readiness.md#command-form-and-intent-visibility):
run ordinary repository operations in direct, single-purpose form (`git status`,
`gh pr view <n>`, `make check`) rather than wrapping them in extra `bash -lc`,
aliases, or compound-shell layers that hide intent. Claude may issue independent
tool calls in parallel; keep parallel calls to independent read-only inspection
and never parallelize mutating Git or overlapping worktree operations.

Isolation comes from the permission model and the working directory or Git
worktree, not from a writable-root sandbox. Keep durable artifacts under their
natural durable owner and repository working state in its repository-owned
paths; use attempt-local scratch only for short-lived private process mechanics
whose loss cannot impair recovery. See
[`repo-readiness.md`](../repo-readiness.md#repo-local-workflow-state).

### Governed read-only reviewer launch

Claude Code treats the invocation working directory as its project root and
may create project-local startup mechanics before any model tool call.
`--add-dir` makes each declared source directory available. The governed
launcher therefore treats the configured launch root as the logical source
anchor, passes that root and every additional source root exactly through
`--add-dir`, and runs the provider from fresh qualified attempt-local scratch.
This contains provider bootstrap state without excluding any reviewed source.
Read a representative object from every root before review. Do not infer
candidate reachability from a prompt-package launch directory.

The CLI controls have different effects:

- `--tools` restricts the built-in tool set; `--allowedTools` auto-approves
  matching tools but does not restrict other tools.
- `--permission-mode dontAsk` suppresses permission prompts but still permits
  Claude's built-in read-only Bash classification; it is not an exact command
  allowlist.
- permission rules evaluate `deny`, then `ask`, then `allow`, first match, and
  Bash string patterns are not a substitute for argv validation.
- `--strict-mcp-config` restricts MCP configuration supplied for the launch;
  use it with an empty declared MCP config when the review forbids connectors.
- `PreToolUse` hooks can block a tool call before execution, while sandbox
  filesystem controls can deny writes. A nested host sandbox can also make the
  provider sandbox unavailable. Settings and hooks can merge from
  higher-precedence managed sources, so neither control alone proves the
  effective posture; never request or permit `dangerouslyDisableSandbox` as a
  workaround.

The repository [`claude-review`](../../scripts/claude-review) source composes
these controls for governed review. Production auth and review run only through
the exact machine-local installation rendered by
[`install-claude-review`](../../scripts/install-claude-review). That installed
launcher verifies its reviewed bytes, immutable schema-v3 entry contract,
active Codex rule, singular flat current qualification receipt, and the exact
absolute Claude selector plus resolved user-owned, non-writable executable
file identity without starting unqualified bytes; it does not select `claude`
from inherited `PATH`. Only after that non-executing identity matches the
schema-v3 qualification receipt may it query the recorded version. It then
re-observes the file identity. Before provider process creation it repeats that
ordering and compares the current receipt, entry contract, canonical path,
ownership, mode, executable status, device, inode, size, digest, and version.
The residual operating-system race between the final recheck and process
creation remains explicit; the launcher does not claim to eliminate it.
A versioned JSON review config binds the
source graph, launch root and exact additional directories, guard roots,
candidate and exact `HEAD`, disjoint evidence directory, immutable
preflight-receipt and final-output paths, exact stream and terminal-receipt
paths for every permitted attempt, observational
command argv, retry cap, observation intervals, and cancellation policy. Mutable
live-state mechanics remain in private controller attempt-local scratch. The
launcher accepts
only model and supported effort selection after `--`; it owns the tool,
permission, MCP, settings, hook, output, and persistence flags.

Production execution derives `HOME` from the effective account's passwd entry,
not inherited environment. The launcher has one explicit fixture-only seam for
selecting an isolated effective home so integration tests can prove the exact
runtime `HOME` recorded in the attempt receipt and prove that `.local`,
`.cache`, and `.config` are not created there. The seam is ignored outside the
explicit fixture execution path.

A selector advance is capability drift, not a candidate finding. Ordinary auth
and review fail closed before Claude receives substantive input and expose only
the exact launcher's prompt-gated identity-qualification transition. The
transition derives and re-observes the configured selector from the immutable
entry contract, requires the expected current receipt and expected
non-executing file-identity digest, and rejects a no-op. Only after the lock,
predecessor, file, ownership, mode, digest, path, and forbidden-root checks pass
does the prompted operation first query the new bytes for their version. It
re-observes the file identity before writing one immutable predecessor-linked
receipt and compare-and-swap replacing the singular current selection with an
exact private, flushed temporary file. It cannot accept an arbitrary executable
or selector. Ordinary drift diagnostics do not claim a version for unqualified
bytes. Unchanged execution and identical-contract installer reruns never
rewrite current selection. Historical receipts do not silently reauthorize
rollback; returning to older bytes is a new transition. Qualification is
evidence and capability gating only and grants no review, candidate, merge, or
other task authority.

The generated `PreToolUse` hook permits `Read`, `Grep`, and `Glob`, and permits
`Bash` only when its command text exactly equals the shell rendering of one
configured argv vector and the tool input does not request sandbox bypass. The
launcher does not force-enable Claude's provider sandbox because bounded review
under a nested host sandbox showed that it can make every granted Bash command
unusable. Instead, the controller independently executes each configured
command before review under a safe environment that disables system Git
and user Git configuration, repository hooks and filesystem monitors, external
diffs, optional Git locks, background auto-maintenance, pagers, Python bytecode
writes, Claude instruction memory loading, and Claude auto memory, with the
provider working directory and temporary state redirected to fresh
attempt-local scratch through the qualified
macOS or Linux route in
[`repo-readiness.md`](../repo-readiness.md#repo-local-workflow-state).
It accepts only the exact Git status, diff, log, and revision forms needed by
the qualifying review, each with one explicit `git -C` declared root. Exact
revision grammar prevents unresolved operands from falling through to Git's
filesystem comparison behavior. Explicit or inferred `diff --no-index`, path
operands, traversal, unadmitted pathspec magic, shell forms, configuration
overrides, text conversion, and external diff fail before provider launch.

Disabling background auto-maintenance removes the controller as a source of
`objects/maintenance.lock` in the candidate repository. It does not remove
another operator's Git, which does not share this environment. A lock created
by that actor remains reviewer side-effect contamination and still fails
closed, because the reviewer cannot establish the writing actor and
[`external-ai-reviewer.md`](../external-ai-reviewer.md) admits only a
controller-owned transient lock identified by exact path, actor, and lifetime.

Linked-worktree modelling requires `git worktree list --porcelain -z`, which
Git introduced in 2.36.0. The launcher probes that exact capability before
taking its first snapshot and fails closed naming the requirement and the
observed version, because the unsupported switch would otherwise surface from
inside snapshot collection and be reported as a review contract failure that
names neither Git nor the version.

The first configured exact command is also an in-provider capability canary.
The system prompt requires it before substantive analysis, and the controller
accepts reviewer output only when the structured stream contains its successful
tool result without a sandbox-bypass request. A missing, failed, or bypassed
canary is reviewer infrastructure failure even if the provider returns a
nominally successful result.

Use `--output-format stream-json --verbose` initialization as effective runtime
evidence. The first `system/init` record must report exactly `Bash`, `Glob`,
`Grep`, and `Read`; no MCP servers, plugins, skills, slash commands, or
capability-startup error; `dontAsk` permission mode; the requested model family;
and the exact attempt-scratch runtime directory. Stop the process on a mismatch
and reject any eventual output. The launcher still performs whole-source,
Git-index, and Git-administration integrity checks because provider flags,
hooks, command-canary evidence, and initialization metadata are defense in
depth, not proof that no effect occurred. It snapshots candidate-worktree and
shared Git administration separately, protects candidate HEAD, branch/ref logs,
admitted command revisions, semantic Git controls, and candidate-reachable
objects, then classifies every raw administration change. It explicitly models
the primary worktree and every linked worktree, including their exact `HEAD`,
`index`, `logs/HEAD`, `COMMIT_EDITMSG`, and `ORIG_HEAD` paths. Only a change to
one of those exact paths, correlated with that worktree's HEAD and symbolic-ref
transition, may be attributed to another worktree; every other path beneath a
known worktree Git directory and every unknown common-root path remains
blocking. Only another worktree's proven administration, unprotected ref/reflog activity, or shared
object-storage layout may be tolerated, and only while protected resolution
and reachability exact-match the baseline and the changed identities contain no
lock, symlink, mode, vanished, special-object, or other ambiguity. Git
configuration, packed refs, replacement, alternate, shallow, graft, attribute,
candidate-specific, and unknown shared changes remain blocking.

The configured candidate commit is reverified immediately before every attempt
baseline and again immediately before provider process creation, including on
retries. Each observation includes the symbolic-ref identity. A mismatch stops
before the provider starts and is preserved as structured evidence; the newly
observed commit cannot silently become the next attempt's baseline.

Git may write a commit object or an exact per-worktree administration file
milliseconds before updating the unrelated HEAD/ref transition that attributes
it. Live monitoring may defer only those exact ambiguous changes for one
bounded stabilization interval, then reclassify from a fresh complete snapshot.
Candidate, protected-ref, lock, unknown administration, mixed, and persistent
unattached changes do not gain that exception, and terminal postflight remains
fully fail-closed.

Use that classification unchanged in preflight, live monitoring, emergency
stopping, terminal postflight, retry eligibility, and receipts. Receipts retain
exact Git-directory-relative paths, owner scope, change type, before/after
identities, proof, and blocking or tolerated disposition. Proven-unrelated raw
change can coexist with a passing candidate-integrity result; it must not be
reported as an aggregate `git-admin` delta or as no observed change. Only a
blocking or ambiguous classification triggers the unauthorized-mutation stop,
so independent linked-worktree commits and pushes require neither a clone nor
serialization. Git-administration lock files remain in the decisive baseline
and terminal snapshot. New, removed, replaced, or changed locks contaminate the
attempt; an exact unchanged pre-existing lock is distinguished from
reviewer-attributable delta.

Anthropic documents `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and
`CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` in its
[environment-variable reference](https://code.claude.com/docs/en/env-vars).
They suppress memory loading and writes; attempt-scratch runtime placement and
whole-source no-delta checks remain required controls rather than assumptions
about undocumented provider internals.

Claude's structured `system/api_retry` event is an in-process provider retry
inside the same attempt. Only a terminal `overloaded` or `server_error` result
may qualify for the launcher's bounded fresh exact-input repeat. Rate limiting,
authentication, billing, capability, access, command, mutation, cancellation,
and unknown errors stop without an outer retry. After the direct provider
process exits, the launcher keeps awaiting the same process group until it is
terminal, then waits for both output collectors to reach end-of-stream before
freezing the stream artifact or considering a retry. The launcher records the
exact process group as required by the shared
[`live-process lifecycle`](../orchestration-and-parallelism.md#live-process-lifecycle).
Mutable control state in controller scratch preserves request, decline,
graceful authority, and separately authorized force authority even after the
direct provider pid exits while another recorded group member remains live.
Do not infer a portable SIGTERM result or exit-code mapping from Claude Code;
record the observed local process outcome.

Keep routine commands, provider retries, stream details, and successful
per-step results in the governed stream and attempt evidence instead of
duplicating them as operator narration. Authentication or execution-context
mismatch, a failed capability canary, unauthorized mutation, source delta,
terminal collection failure, or postflight failure remains an immediate
material blocker. Treat product-rendered traces as runtime behavior unless
current official evidence establishes control; do not claim provider or client
trace suppression.

## Worktrees And Subagents

Apply the one-repository, one-branch, one-worktree, one-PR rule and
`<repo>/.worktrees/` placement from
[`repo-readiness.md`](../repo-readiness.md#pr-readiness) unchanged; create
repo-changing worktrees with direct `git worktree add` naming the full
`.worktrees/<task-name>` path.

Non-fork Claude subagents (`Task` tool) start with a separate context and do not
receive the parent conversation history or files the parent previously read, so
give each one a complete, self-contained envelope rather than relying on implicit
conversational context: repository and working directory, interaction mode and
deliverable, goal, scope and exclusions, source evidence or retrieval
instructions, validation path, and stop conditions (this is the standalone-worker
requirement in
[`orchestration-and-parallelism.md`](../orchestration-and-parallelism.md)).
Worker authority stops at the envelope; a worker must not merge, enable
auto-merge, update other branches, or continue into downstream reconciliation
unless the human authorizes that step.

## Context Compaction And Recovery

Claude Code auto-compacts before the context window fills and supports `/compact`
and session resume (`--resume`, `--continue`). Compaction replaces earlier turns
with a summary. Treat compacted or resumed conversation as navigation, not
authority: after either, re-retrieve authoritative repository, PR, issue, CI, and
file state before relying on it, per
[`source-first-retrieval.md`](../source-first-retrieval.md) and
[durable continuity](../core-model.md#durable-continuity).

## Connectors

Claude reaches remote services, including GitHub, through MCP servers. Apply the
[runtime-evidence rule](../start-here.md#connector-availability-is-runtime-evidence):
inspect available connector actions or attempt the operation before claiming a
capability is unavailable, and treat a successful call as evidence it remains
available. For GitHub PR and issue work, prefer connector-first inspection per
[`review-packet.md`](../review-packet.md#direct-pr-inspection); direct `git` and
`gh` supplement it and remain appropriate for verified connector gaps or
repo-local workflows.

### Issue-Owned Durable Prompt Retrieval

Apply the shared
[`issue-owned durable rendered-prompt handoff profile`](../prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile)
when Claude Code receives an exact issue-owned prompt. Direct provider
consumption is qualified only when the current Claude surface can retrieve raw
bytes and the required provider identity metadata through a permitted,
observed route. Do not infer that qualification from connector presence,
extracted text, a synced folder, or another actor's successful retrieval.

Otherwise use one private OS-managed executor-attempt copy produced by an
authorized controller or operator from the raw durable object. Bind the launch
to its exact path, expected size, SHA-256, and declared text format. Retrieval
and byte verification require only the minimum read capability needed to
inspect the prompt. Record whether Claude computed the digest itself or relied
on controller-bound digest evidence plus exact read evidence. A direct Claude
provider limitation does not block this profile when the exact attempt-local
route succeeds.

After prompt acceptance, choose Claude's tools and permission mode from the
bounded task's authorized execution requirements. Read-only tools are mandatory
only when the owning task is read-only or a narrower reviewer or qualification
contract requires read-only inspection. Disable session persistence only when
the owning execution, reviewer, or qualification contract requires it. Prompt
handoff alone does not prohibit write tools, tests, repository mutation, output
creation, or session persistence already authorized by the bounded task.
Preservation and exact retrieval still grant no substantive execution
authority.

Keep delivery, acknowledgement, Claude attempt, attempt receipt, and output
identities separate. Preserve required evidence, then remove and verify removal
of only the private attempt-local copy after the attempt no longer depends on
it. Revalidate containment and identity, and fail closed on the shared cleanup
conditions in [`repo-readiness.md`](../repo-readiness.md#repo-local-workflow-state).
The concrete provider, account, namespace, destination, retention, and
visibility values remain outside this reusable adapter.

## Claude Model, Thinking, And Thread Routing

Choose the lowest-cost Claude Code model/configuration expected to preserve the
confidence required by the bounded task. Do not infer a mapping from OpenAI
model names or tiers. Current Claude Code documentation, checked 2026-08-10,
establishes the executor-native `haiku`, `sonnet`, `opus`, and `fable` aliases:
Haiku for simple fast tasks, Sonnet for daily coding, Opus for complex reasoning,
and Fable for the hardest and longest-running tasks.
Anthropic's current platform model guidance independently positions Haiku 4.5
for fast, high-volume, cost-sensitive work; Sonnet 5 for coding, agents, and
enterprise workflows; and Opus 5 for complex agentic coding and enterprise
work. Exact model IDs, aliases, model availability, context variants, and
administrator allowlists are runtime evidence, not this adapter's assumption.
Claude Code documents `best` as Fable where available and otherwise the latest
Opus; it is not a durable qualification guarantee. Fable requires a current
Claude Code version and is unavailable under zero-data-retention. Its safety
classifiers can trigger documented fallback, so use an explicit Fable request
only when its effective runtime identity can be observed and meets the task's
qualification requirements.

| Claude task class | Default Claude Code model | Thinking/effort guidance | Escalate when | Downgrade/follow up when |
| --- | --- | --- | --- | --- |
| Deterministic external verification; hashes, inventories, evidence citations; simple source inspection; mechanical fallback verification | `haiku` | Use executor default; Claude Code does not document effort control for Haiku | a result is ambiguous, changes a decision, or source access is insufficient | substantive review has converged and a qualified deterministic check remains |
| Implementation review; evidence-package review; reviewer follow-up after substantive convergence; bounded long-context evidence synthesis | `sonnet` | Use the documented default `high`; use `medium` or `low` only as an explicit cost/latency trade-off where bounded evidence supports it | residual findings repeat, evidence conflicts, or semantics remain unresolved | split inventories, hashes, and other externally checkable claims to Haiku or another qualified mechanism |
| Substantive adversarial code review; protocol/design review; architecture review; authority or security-boundary review | `opus` | Use the model's documented default; do not assume `xhigh` applies to every Opus runtime | a new trust boundary, unresolved architecture/security implication, conflicting authority, or a finding that changes qualification disposition appears | after substantive convergence, delegate only the remaining mechanical claim; do not relabel it as substantive review |
| Especially hard long-running investigation, outage/root-cause work, or architecture decision that exceeds a normal Opus review | `fable`, where available | Adaptive thinking is always on; use the documented default `high`, and reserve `xhigh`/`max` for a bounded demonstrated need | a safety fallback, unavailable Fable runtime, or remaining decision risk defeats the qualification requirement; stop, seek an explicit human decision, or use another independently qualified mechanism | keep Fable out of routine review and delegate only bounded deterministic follow-up |

The table is a conservative routing hypothesis, not a quality-parity claim. A
large evidence package does not automatically require Opus, and a small
authority-boundary change may. Do not downgrade when error consequences are
high, ambiguity is material, independent verification is weak, work is hard to
reverse, or failure could silently corrupt authority or evidence.

### Thinking And Effort

Claude's thinking and effort controls are distinct from model choice where the
active Claude surface supports them. Anthropic documents adaptive thinking and
an `effort` parameter on current supported models; its Claude Code documentation
lists the actual model/effort combinations and says the effort scale is
calibrated per model. Use the executor's canonical terminology and supported
values rather than treating `light`, `medium`, and `high` as portable numeric
equivalents. For current Claude Code, `low`, `medium`, `high`, `xhigh`, and
`max` availability depends on the selected model; verify the effective choice
at runtime. Claude Code documents `high` as the default for every
effort-capable model except Opus 4.7, which defaults to `xhigh`; lowering effort
is the primary cost/latency lever for a bounded task. Do not invent a Haiku
effort setting where the executor does not offer one.

### Thread Routing And Review Boundaries

Apply the shared `FRESH THREAD`, `SAME THREAD`, and `CHILD TASK` vocabulary in
[`prompts.md`](../prompts.md#thread-routing-and-configuration-continuity). For
a FRESH THREAD, choose this matrix's task-appropriate model and supported
thinking/effort setting. For a SAME THREAD, preserve the existing parent model
and thinking/effort configuration by default: a cheaper setting being sufficient
for the current sub-phase does not itself justify changing the running task.
For a CHILD TASK, select the lowest-cost sufficient Claude configuration for the
bounded child and preserve its inputs, configuration, execution identity,
durable result, and authority boundary where the workflow requires it.

### Visible Thread Names

This adapter does not currently establish an executor-applied visible-thread
naming capability. Therefore Claude-targeted `FRESH THREAD`, `SAME THREAD`,
and `CHILD TASK` prompts resolve the shared
`[resolved thread-name section when applicable]` placeholder to nothing. Do
not ask Claude to rename itself or report a naming limitation. This is the
Playbook's current adapter mapping, not a claim about every present or future
Anthropic product surface.

Requested configuration and effective runtime configuration are distinct.
Claude Code can intentionally switch `opusplan` from Opus in plan mode to Sonnet
in execution, and can use configured fallback chains for unavailable or
overloaded models; Fable/Opus safety-classifier fallback is also documented.
For governed work, record the requested model/effort and the effective values
when the runtime exposes them, plus any substitution event. `/status` exposes
the current Claude Code model, and Claude Code shows a transcript notice when a
documented switch occurs. On the Claude API, server-side fallback responses
identify the serving model and expose fallback blocks and attempt iterations.
Other providers and error paths need not expose the same evidence or perform a
server-side fallback. If effective identity is unavailable, record that
limitation rather than treating the request as proof. Requalify, escalate, or
stop only when the effective result violates a required capability or exact-model
reviewer qualification; a runtime event is not automatically fatal.

If a lower-capability SAME THREAD reaches unresolved ambiguity, an architecture
or authority decision, conflicting authoritative evidence, repeated residual
correctness findings, an unexplained invariant, a new trust boundary, or a
decision-relevant uncertainty, prefer a bounded stronger child or explicit
fresh-thread transition over mutating the parent silently. If a stronger parent
reaches deterministic follow-up, delegate the bounded check to Haiku or another
qualified mechanism where worthwhile instead of downgrading the parent solely
for cost.

Reviewer independence is separate from model, thinking/effort, and thread
routing. A qualified separate Claude invocation can supply the selected external
review only when it meets the reviewer contract. A child spawned by the party
under review is not externally independent, regardless of its model, vendor,
effort, or isolated context; an internally spawned Codex review remains Codex
review. Mechanical external verification and Codex
mechanical fallback must be labeled as their actual mechanism and never
retroactively stand in for substantive external review. CAK-106 is observational
workflow evidence only: substantive authority/process findings justified deeper
review, while later evidence-precision, environment-limited verification, and
mechanical follow-up were candidates for a bounded qualified mechanism. It does
not establish savings, quality parity, or cross-vendor equivalence.

### Prompt Operator Metadata

When an operator prepares a Claude prompt, use one complete metadata block:

```text
Operator metadata (do not include in prompt)
Thread routing: <FRESH THREAD | SAME THREAD | CHILD TASK>
Recommended model: <FRESH THREAD/CHILD TASK: haiku | sonnet | opus | fable; SAME THREAD: Preserve requested thread model and observe effective runtime model>
Recommended thinking/effort: <FRESH THREAD/CHILD TASK: supported executor setting; SAME THREAD: Preserve requested thread setting and observe effective runtime setting>

Reason:
<one concise task-specific selection or continuity justification>
```

This metadata is operator guidance, not task authority. Do not recommend a
model, effort, or child configuration that the current Claude surface cannot
support. Interpret FRESH/SAME routing before prompt delivery: do not tell the
downstream Claude task to change or preserve parent configuration when that
surface does not expose the control. The executable task body must be complete
without metadata and may authorize child dispatch only where that Claude
surface supports it. Keep task-required requested/effective runtime evidence in
the executable body when it is a validation or qualification requirement.

## Reasoning And Model Configuration

When a material prompt uses the product-neutral reasoning class in
[`prompt-contracts.md`](../prompt-contracts.md) (`light`, `medium`, `high`), the
Claude representation is a supported thinking/effort setting plus model
selection chosen for the bounded task. Concrete model names and thinking/effort
settings are adapter configuration and attempt-receipt metadata, not the meaning
of the class.
Preserve whether the class and each capability are mandatory or advisory; if the
available Claude surface cannot meet a mandatory requirement without weakening a
guarantee, fail closed rather than silently downgrade. A model change alone does
not justify a prompt rewrite; preserve existing behavior first, then make
surgical changes tied to an observed failure.

## Local GitHub And Environment Preflight

`scripts/codex-preflight` checks local GitHub SSH auth, `gh` auth, and repository
reachability — executor-neutral environment readiness. When Claude drives
repository automation or worker fan-out, run it first and stop on a non-zero
exit:

```text
cd /Users/keith/src/ctrl-alt-keith/ai-workflow-playbook
./scripts/codex-preflight
```

## Delivery And Stop Conditions

Follow the PR readiness, validation, and delivery rules in
[`repo-readiness.md`](../repo-readiness.md) and repo-local `AGENTS.md`. On
completion, report the PR link when one was opened or updated, files changed,
validation results, and known blockers or residual risks.

Pause and ask for human input when the repository, branch, or worktree context
appears wrong, the scope is ambiguous or has shifted, required source state
cannot be retrieved, more than one valid path depends on human judgment, or the
next step is merge, release, tag, destructive, externally visible, or
permissions-sensitive.

## References

Behavioral claims above are grounded in official Anthropic documentation,
including [memory](https://docs.claude.com/en/docs/claude-code/memory),
[permissions](https://code.claude.com/docs/en/permissions),
[the tools reference](https://code.claude.com/docs/en/tools-reference),
[subagents](https://docs.claude.com/en/docs/claude-code/sub-agents), and
[worktrees](https://code.claude.com/docs/en/worktrees). Model-routing claims
above are additionally derived from Anthropic's official [Claude Code model
configuration](https://code.claude.com/docs/en/model-config), [model-selection
guide](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model),
[models overview](https://platform.claude.com/docs/en/about-claude/models/overview),
[thinking guide](https://platform.claude.com/docs/en/build-with-claude/thinking),
and [fallback guide](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback),
checked 2026-08-10.
