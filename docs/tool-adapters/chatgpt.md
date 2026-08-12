# ChatGPT/Work Adapter

This adapter projects the Playbook onto repository-scoped ChatGPT and Work
use. It begins after repository work has been activated; ordinary conceptual
Chat remains outside repository startup. Shared operating rules remain owned
by [`start-here.md`](../start-here.md) and
[`core-model.md`](../core-model.md).

## Repository-bootstrap boundary

Project instructions are bootstrap and routing input, not a second copy of the
Playbook. After the CAK-108 project bootstrap has routed repository work to the
current [`start-here.md`](../start-here.md), apply this adapter with the
repository floor and the task-activated guidance.

## Project and conversation context

Project instructions, project or uploaded files, conversation history, memory,
and prior hydration can help route or continue work, but do not establish the
current source boundary. Generated artifacts and Work state are derived
outputs; connected-app availability is runtime capability evidence; a
connector result is evidence only for its observed operation. Classify and use
each surface through [`core-model.md`](../core-model.md#authority-follows-the-question),
[`source-first-retrieval.md`](../source-first-retrieval.md), and, for material
prompts, [`prompt-contracts.md`](../prompt-contracts.md).

## Persistent-context activation

Repository mode may continue across Chat and Work turns. For an ordinary
repository follow-up whose task shape remains sufficient, reuse still-current
verified sources. If the task materially changes interaction mode, artifact,
workflow, source need, execution locality, or authority boundary, re-run the
current activation route before responding, planning, drafting, or acting.
Retrieve newly activated owners without replaying unchanged doctrine or
hydrating unrelated documents. This is the persistent-context projection of
the [activation-sufficiency invariant](../start-here.md#required-repository-invariants);
[`repo-readiness.md`](../repo-readiness.md) owns interaction-mode selection.

## Chat, Work, and execution locality

Chat and Work are task-shape and capability surfaces under this one adapter,
not separate authority contracts. A transition between them preserves
repository mode unless the task's source or boundary needs change. When Work
moves between local and cloud execution, revalidate the required sources,
working location, tools, credentials, acting identity, and mutation surface
that materially changed. Use [`repo-readiness.md`](../repo-readiness.md) for
repository execution posture and
[`maintenance-automations.md`](../maintenance-automations.md) when locality or
unattended-work guidance is activated.

## Connected apps, approvals, and consequential actions

An installed or authenticated app, available action, or product approval
setting describes capability or permission behavior; it does not expand the
human-authorized task. Keep consequential writes within the authorized scope
and re-observe their result before reporting the intended effect. The shared
authority, decision-boundary, and re-observation rules remain in
[`core-model.md`](../core-model.md), while connector availability is governed
by [`start-here.md`](../start-here.md#connector-availability-is-runtime-evidence).

## Workspace Agents

Workspace Agents are a ChatGPT/Work execution surface, not a second adapter.

### Trigger initiation and durable run authority

API/event and scheduled Workspace Agent runs may begin without an interactive
user turn. A published agent or channel, API token, trigger payload, schedule
instructions, prior conversation or memory, and run status are capability,
input, continuity, or execution evidence; they do not create approval or widen
task authority. Trigger data is event/run input and evidence, not automatically
authoritative source state for another system. Each run must resolve its
durable bounded authority envelope and current required sources. If a required
source, identity, connection, or authority is missing, stale, conflicting, or
mismatched, fail closed or return an explicit non-authorizing partial or
blocked result. Use [`core-model.md`](../core-model.md),
[`source-first-retrieval.md`](../source-first-retrieval.md), and
[`maintenance-automations.md`](../maintenance-automations.md) for the shared
authority, retrieval, and recurring-execution rules. Workspace Agents are
hosted execution when the required facts, connections, identities, and outputs
are actually provisioned there.

### Acting connection identity

Workspace Agents can use end-user connections or agent-owned/shared
connections. Keep the invoker/end user, API caller/token principal, Workspace
Agent/configuration, and downstream connected-system acting account distinct.
Tie reads, writes, source scope, attribution, and re-observation to the actual
connection identity; do not attribute an agent-owned connection action to its
invoker. Connection permissions expose or constrain capability, but do not
widen human task authority. Stop when the expected acting identity does not
match the available connection rather than silently substituting one.

### Draft, publication, and channels

Draft/Preview is candidate or test state, not proof of a published operational
agent. Publication, sharing/channel enablement, or equivalent activation is a
material operational transition requiring applicable explicit authority and
re-observation of the resulting provider state. It can make a selected
configuration callable, but does not make sources current, grant arbitrary
downstream authority, convert capability into approval, or make generated
outputs canonical. If a schedule, trigger, or channel change materially alters
future initiation, audience, source scope, identity, instructions, or possible
effects, preserve that material-transition boundary without assuming universal
republish or version mechanics. Run logs/status, memory, conversation keys,
generated artifacts, and prior results remain continuity, history, or evidence
surfaces; a completed run does not replace post-write re-observation of the
connected-system object.

## Prompt and downstream-context projection

When the task becomes prompt authoring, activate the current prompt and
orchestration owners rather than reproducing their doctrine here. Project or
controller context does not prove a downstream prompt has the same sources or
evidence. Use [`prompts.md`](../prompts.md),
[`prompt-contracts.md`](../prompt-contracts.md), and
[`orchestration-and-parallelism.md`](../orchestration-and-parallelism.md) for
the applicable prompt and downstream-context contract.

## Generated artifacts

Creating a ChatGPT or Work artifact does not make it current authoritative
state or grant publication, sharing, overwrite, or adoption authority. Apply
the derived-artifact and consequential-action boundaries in
[`core-model.md`](../core-model.md) and the material-artifact contract in
[`prompt-contracts.md`](../prompt-contracts.md) when activated.

## Scheduled and unattended execution

Scheduled or unattended ChatGPT/Work must project the current automation,
source, and locality rules for each run. A standalone run cannot assume an
originating conversation; an in-chat run may use conversation as context but
not as proof of current canonical or provider state. Do not depend on an
interactive approval or unavailable local state. The governing owner is
[`maintenance-automations.md`](../maintenance-automations.md), with current
retrieval in [`source-first-retrieval.md`](../source-first-retrieval.md).

## Recovery after activation drift

If persistent context proves under-hydrated, stop continuity-based drafting or
action and re-enter current canonical routing. Retrieve the missing activated
owners, revalidate mutable sources, and replace or correct the affected
artifact as a whole before resuming. This is a ChatGPT/Work projection of
[`source-first-retrieval.md`](../source-first-retrieval.md) and, for prompts,
[`prompts.md`](../prompts.md); it is not symptom-by-symptom repair from
conversation memory.

## Evidence and provider-reference boundary

This adapter defines Playbook behavior, not a provider guarantee about how
ChatGPT context, memory, permissions, or Work execution operates. Re-check
provider behavior through authoritative current evidence when a task depends
on it; keep observed runtime behavior separate from that evidence.
