# ChatGPT Adapter

This adapter applies to repository-scoped ChatGPT. Chat and Work are modes
under one adapter; Codex is a distinct executor. Ordinary conceptual Chat does
not activate repository startup. Shared rules remain owned by
[`start-here.md`](../start-here.md) and [`core-model.md`](../core-model.md).

Provider behavior was rechecked against official OpenAI documentation on
2026-09-21; provider sources belong in reviewed PR evidence, not this
agent-read adapter.

## Bootstrap and continuity

- Project instructions are routing input, not a second Playbook. Apply this
  adapter after they route repository work to `start-here.md` and its required
  repository floor.
- Install the global bootstrap router separately in account custom instructions
  and CAK project instructions; manually verify each surface. Do not treat it
  as a per-turn retrieval rule.
- Project/uploaded files, conversation, memory, prior hydration, generated
  artifacts, and Work state are context or derived evidence, not current source
  authority. Connected-app availability is runtime capability evidence; a
  connector result proves only its observed operation. Apply the canonical
  authority and source-first owners before relying on them.
- Repository mode can continue across Chat and Work. Before treating a strongly
  unrelated instruction as a task change, apply active bounded-task continuity.
  Re-run activation and retrieve only newly required owners when the interaction
  mode, artifact, workflow, source need, execution locality, or authority
  boundary materially changes.

## Chat-to-Work projection

Chat is interactive; Work is an execution surface for bounded general-purpose
outcomes. A Chat-to-Work transition preserves repository mode unless a required
source or boundary changes. Revalidate any materially changed source, working
location, tools, credentials, acting identity, or mutation surface. Consequential
Work results return to Chat for review and disposition unless another owner
places that authority elsewhere.

Apply the shared interactive-to-execution consent boundary to Chat-to-Work.
Authorizing the task and identifying a Work capability/locality are separate
from transition consent. Do not instantiate or transition to Work unless the
operator explicitly requests it or accepts an offered transition; absent
consent, retain an eligible Chat-local or separately authorized executor route,
or offer Work and stop. Authoring or presenting a Codex prompt does not select
Work.

For Work handoffs, use the canonical prompt owner and name the bounded outcome,
permitted sources/tools, output checks, and return boundary. Codex handoffs
also require repository locality, validation, PR delivery, and stop-before-
merge. Verify a governed package's identity before relying on it.

## Connected apps and consequential actions

An installed/authenticated app, available action, or approval setting is
capability or permission evidence, not task authority. Keep writes in scope and
re-observe their result. For a routine connected-app write, perform only that
write and the owning contract's minimum verification. Do not call preview,
thumbnail, provider-open, or share-link actions just to confirm success.
Visual inspection is eligible only when requested, required for rendered
correctness, or required by a narrower owner. Treat any client-rendered card as
client-enforced UI; do not claim it was suppressed.

Treat the effective permission setting and exact action contract as runtime
evidence. A general permission does not waive a more specific action
requirement, workspace/provider restriction, or safety protection.

### Prompt transport

Use the canonical prompt-delivery decision model and preserve its terminal
failure reason. For a qualifying machine recipient with a permitted Airtable
route, apply the canonical Airtable handoff before selecting presentation; do
not add file-preview, download-link, or attempt-local retrieval steps. For a
human execution recipient, use the inline two-block presentation. If machine
recipient Airtable capability is unknown, inspect or attempt it before routing.
Routine prompts do not inherit the material-prompt profile merely from
transport.

For Airtable production and consumption, resolve the permitted base, table, and
field IDs through current actions and use the returned record ID with the exact
`recordIds` constraint. Apply the canonical handoff's verification, correction,
and transport rules, plus the issue-owned durable-capture profile; do not add
any record or transport beyond what those owners require.

When an inline prompt is selected, emit the shared operator metadata and the
complete executable prompt as consecutive fenced blocks with no assistant prose
before, between, or after them. Keep the executable block independently usable;
resolve the ChatGPT thread-name placeholder to nothing.

## Workspace Agents

Workspace Agents are a ChatGPT execution surface, not another adapter. For an
API, event, or scheduled run, publication/channel state, token, trigger,
conversation, memory, and run status are capability, input, continuity, or
execution evidence—not approval or current authority. Resolve a durable bounded
authority envelope and current required sources for every run. Fail closed, or
return an explicit non-authorizing partial/blocked result, when a required
source, identity, connection, or authority is missing, stale, conflicting, or
mismatched.

Keep the invoker/end user, API caller/token principal, agent/configuration, and
connected-system acting account distinct. Tie reads, writes, scope, attribution,
and re-observation to the actual connection identity; do not silently substitute
or misattribute an agent-owned connection.

Draft/Preview is candidate or test state, not proof of a published agent.
Publication, sharing/channel enablement, or equivalent activation requires
applicable explicit authority and re-observation. A schedule, trigger, or
channel change that alters future initiation, audience, source scope, identity,
instructions, or effects is material. Completion logs, memory, conversation
keys, generated artifacts, and prior results remain continuity/history/evidence;
they do not make a source current or replace post-write re-observation.

## Recovery and unattended work

Prompt authoring, generated artifacts, scheduled/unattended work, and recovery
use their canonical owners. A generated artifact does not grant publication,
sharing, overwrite, adoption, or current authority. Each unattended run must
apply current automation, source, and locality rules; a conversation can supply
context but not canonical state or an interactive approval.

If persistent context is under-hydrated, stop continuity-based drafting/action,
re-enter canonical routing, retrieve the missing owners, revalidate mutable
sources, and replace or correct the affected artifact as a whole before
resuming. This adapter specifies Playbook behavior, not a provider guarantee;
re-check provider behavior through current official evidence when it matters.
