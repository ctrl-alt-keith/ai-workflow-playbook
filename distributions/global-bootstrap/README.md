# Global Bootstrap Distribution

## Purpose

This distribution projects the Playbook's repository startup entry point onto
provider-global instruction surfaces. Installing the applicable projection
once gives every repository the same thin router without copying shared
doctrine into every repo-local instruction file.

The canonical timing rule remains in
[`docs/start-here.md`](../../docs/start-here.md#global-bootstrap-persistence):

> Before the first project action, and again only when the task/repository
> materially changes.

The router persists after successful bootstrap. A new conversational turn,
follow-up message, reasoning step, or tool call does not independently trigger
another retrieval.

## Canonical Router

[`bootstrap-router.md`](bootstrap-router.md) is the one copy-ready router body.
Do not maintain provider-specific copies of its text.

The router projects the core model's active bounded-task continuity guard
before its material-change bootstrap trigger without copying that guard's
behavior or cases into the distribution.

The final hard precondition in that body is scoped by the first-action or
material-change trigger. It permits the retrieval needed to obtain and apply
`start-here.md`, but blocks all response, task reasoning, and unrelated tool
invocation while that trigger is active. Retrieval or read failure stops the
task rather than allowing execution from memory. The precondition is not a
standing per-turn block after successful bootstrap.

## Immediate Codex Desktop Repair

The immediate Codex desktop repair has exactly one app-level destination:

- **Codex user-global instructions:** place it in `~/.codex/AGENTS.md` between
  the managed markers described below.

That repair does not require a Codex project setting, conversation or memory
setting, repository-local `AGENTS.md`, or Claude router change. None of the
broader provider surfaces below affects Codex desktop behavior.

## Broader Provider Rollout

The broader CAK-187 rollout projects the same canonical body to these separate
provider surfaces:

- **Claude Code user-global instructions:** place it in
  `~/.claude/CLAUDE.md` between the same managed markers.
- **Claude account instructions:** Anthropic currently documents
  **Instructions for Claude** as an account-wide setting reached from the
  account initials and **Settings**. Install and verify the body there when
  Claude conversations may start CAK repository work; do not classify this
  account surface as Chat-only.
- **Claude runtime account preferences:** when a current session exposes one
  or more `user_preferences` blocks, audit them as a separate observed
  instruction transport until their owning hosted setting and precedence are
  established. Remove or reconcile stale CAK directives such as unconditional
  "before answering" wording; do not assume an edit to another visible field
  changed these injected blocks. When the owner cannot be established, record
  unresolved provenance and continue treating the stale directive as active;
  do not claim that it was repaired.
- **Claude Cowork global instructions:** Anthropic currently documents
  **Settings > Cowork**, then **Global instructions**, for standing Cowork
  instructions. Verify that destination in the current account and product
  build before installation. If the route is not exposed, record the observed
  capability gap instead of substituting account instructions or installing a
  duplicate in another field.
- **ChatGPT account custom instructions:** install and verify the body through
  the hosted Personalization surface.
- **ChatGPT CAK project instructions:** install and verify the body through the
  hosted project-instructions surface.

The two ChatGPT destinations are distinct hosted configuration surfaces even
when they intentionally use the same reviewed router body. Record and verify
them separately; do not collapse them into one ambiguous "project/custom"
surface. They are manual hosted projections, not prerequisites for the
immediate Codex desktop repair.

Claude account instructions, runtime account preferences, and Cowork global
instructions are independently audited hosted transports. They are not read or
changed by this distribution or its local-file validator. Reconcile older
unconditional wording such as "always fetch before answering" to the canonical
timing and fail-closed retrieval semantics; do not claim local validator
coverage for any hosted surface. Use Claude project or Cowork folder
instructions for project-specific context, never as another copy of the global
router. When no verified global transport covers a run, record the gap and use
an explicit qualified current-source route for that run; do not fill the gap by
duplicating the router in a project or folder field.

Anthropic documents
[**Instructions for Claude**](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)
as account-wide for conversations and
[Cowork Global instructions](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)
as applying to every Cowork session, but does not publish their combined
precedence, their relationship to runtime `user_preferences` blocks, or
deduplication behavior. Verify them separately and do not infer that account
instructions alone cover Cowork. If a runtime presents the same canonical
router through more than one transport, treat the copies as one idempotent
bootstrap trigger under the persistence rule, not as separate doctrine or a
reason to retrieve once per copy.

Use these markers around the exact router body in the Codex and Claude local
files:

```text
<!-- ai-workflow-playbook:global-bootstrap:start -->
[exact contents of bootstrap-router.md]
<!-- ai-workflow-playbook:global-bootstrap:end -->
```

The read-only validator compares only the marked body after normalizing outer
newlines, permitting unrelated personal instructions before or after it.
Preserve the markers when installing or updating the router.

## Read-Only Validation

Run:

```text
make check-local-bootstrap
```

The default check requires the immediate Codex destination. When the Claude
user-global file exists, the check validates it too; an absent Claude file is
reported as a skipped broader-rollout surface rather than failing the Codex
repair. Use `--require-claude` when validating a completed broader local
rollout.

To require both default user-global locations for a completed local rollout,
run:

```text
python3 scripts/check_global_bootstrap.py --require-claude
```

For every selected local file, the check extracts the managed body and compares
the normalized body with [`bootstrap-router.md`](bootstrap-router.md). It does
not create, edit, or replace local files. Missing required files, missing or
duplicate markers, and content drift fail with a remediation path.

Use explicit paths when validating staged or fixture files:

```text
python3 scripts/check_global_bootstrap.py \
  --codex-file /path/to/AGENTS.md \
  --claude-file /path/to/CLAUDE.md \
  --require-claude
```

Claude account instructions, observed runtime account preferences, Claude
Cowork global instructions, ChatGPT account instructions, and ChatGPT CAK
project instructions are each validated by direct comparison during manual
installation or runtime audit because the providers do not expose those hosted
surfaces as local files. That is a capability gap, not equivalent to the local
byte check: record the surface, observed owner or unresolved provenance,
canonical router commit, and verification time in the owning rollout issue so
later drift checks have an explicit baseline.

## Local Reconciliation

After the canonical router changes, reconcile an existing marked local file
from [`bootstrap-router.md`](bootstrap-router.md), never from a copied body in
an issue, PR, or chat. The operator path is explicit:

```text
check -> plan -> review -> apply -> verified pass
```

```text
make check-local-bootstrap
make plan-local-bootstrap
make apply-local-bootstrap
make check-local-bootstrap
```

`check-local-bootstrap` remains read-only. `plan-local-bootstrap` is also
read-only: it reports already-current surfaces and renders the exact unified
diff for each managed body that needs replacement. Review that diff before
running the distinct, explicit `apply-local-bootstrap` command.

Apply accepts only a single existing marker pair in a regular UTF-8 file and
atomically replaces only the managed body, preserving unrelated prefix and
suffix content. It prepares the replacement from an observed file, then
immediately before replacement re-reads and compares the content, mode, and
file identity; an observed change fails closed. It verifies the result against
the canonical router. Missing, duplicate, malformed, or changed unsafe state
fails closed. It never creates a marker pair or performs broader provider-home
management.

This is a final pre-replacement snapshot check, not a cross-process lock or a
filesystem compare-and-swap primitive. An uncooperative writer that changes a
file after that final comparison and before the atomic path replacement cannot
be distinguished by this workflow; the command does not claim to prevent that
last filesystem scheduling race.

By default, plan and apply cover the Codex local file and the Claude local file
when it is installed. To inspect or reconcile one existing provider surface,
use the same canonical command with an explicit selector:

```text
python3 scripts/check_global_bootstrap.py --mode plan --provider codex
python3 scripts/check_global_bootstrap.py --mode apply --provider claude
```

First-time installation is deliberately separate from reconciliation. Add and
review a marker pair around the canonical body through the installation process
before these commands can manage the file. Local reconciliation is an explicit
post-merge action; this repository change does not silently mutate either
user-global file.

## Installation Boundary

The templates and reconciliation helper are repository deliverables. Updating
live provider-global files remains a separate local action: review the plan,
explicitly apply the marked-block substitution, and run the read-only check.
Do not edit repo-local `AGENTS.md` or `CLAUDE.md` files merely to install this
global router.
