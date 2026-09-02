# ChatGPT Adapter

This adapter projects the Playbook onto repository-scoped ChatGPT use. Chat
and Work are nested task-shape or capability modes under that one ChatGPT
adapter, not separate durable executor identities or adapters. It begins after
repository work has been activated; ordinary conceptual Chat remains outside
repository startup. Shared operating rules remain owned by
[`start-here.md`](../start-here.md) and [`core-model.md`](../core-model.md).

Current [OpenAI Help Center guidance](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex)
places Chat and Work under ChatGPT and identifies Codex as a distinct view with
history separate from ChatGPT history. [ChatGPT Work guidance](https://learn.chatgpt.com/docs/get-started-with-work)
describes Work as delegated work to ChatGPT and an alternative to Codex for
non-coding tasks. The Playbook uses that documented persistence boundary for
adapter selection.

## Repository-bootstrap boundary

Project instructions are bootstrap and routing input, not a second copy of the
Playbook. After the CAK-108 project bootstrap has routed repository work to the
current [`start-here.md`](../start-here.md), apply this adapter with the
repository floor and the task-activated guidance.

Use the one copy-ready
[`global bootstrap router`](../../distributions/global-bootstrap/bootstrap-router.md)
for both hosted ChatGPT destinations: account custom instructions and CAK
project instructions. Treat them as separately installed and manually verified
surfaces, not one ambiguous configuration. The router applies the shared
[`global bootstrap persistence`](../start-here.md#global-bootstrap-persistence)
timing invariant across repositories. Do not reinterpret the router as a
per-turn retrieval requirement.

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

### Interactive control-plane projection

Chat is the normal interactive control plane for human-led clarification,
scoping, authority decisions, decomposition, steering, review, and disposition.
Work is the preferred ChatGPT surface for a bounded general-purpose multi-step
outcome or non-repository deliverable. Codex is the preferred distinct
repository-oriented executor when completion materially depends on repository
locality, terminal commands, tests, Git, worktrees, commits, pull requests, or
code review. Hard reasoning may remain in Chat while the task is still
interactive; difficulty, model tier, or reasoning setting does not select Work
or Codex.

This is a default task-shape projection, not a claim that Chat is canonical,
universally authoritative, or required to mediate every workflow. Chat and
Work remain nested surfaces under one ChatGPT adapter. Use the shared routing,
surface-transition, thin-envelope, and target-shaping rules in
[`prompts.md`](../prompts.md#task-shape-surface-selection-and-thin-handoffs).

When a handoff points to an exact package through a connected app, treat access
as runtime evidence. Inspect or attempt retrieval of the named manifest or
sealed-package identity before claiming it is accessible, and verify the exact
identity before relying on its payload. Listing a folder or reaching a mutable
package root proves neither exact-package access nor current authority. If the
identity cannot be accessed, resolved, or verified, fail closed or return an
explicit non-authorizing partial result without reconstructing it from Chat or
Work memory.

#### Work-shaped handoff

Project the shared thin-envelope semantics for a delegated general-purpose
outcome by emphasizing permitted connected sources and tools, output form,
quality checks, and the return-to-Chat boundary:

```text
Target: Work — bounded general-purpose outcome
Outcome: [source-backed non-repository deliverable]
Governed payload: [exact manifest or sealed-package identity]
Human direction and authority: [bounded declaration, owning reference, prohibitions]
Refresh: [mutable sources to retrieve from their owners]
Tools and locality: [permitted connected sources and execution location]
Validation and output: [quality checks and deliverable form]
Return boundary: [return to Chat for review or stop condition]
```

#### Codex-shaped handoff

Project the shared thin-envelope semantics for repository execution by adding
exact repository locality, terminal and Git tools, canonical validation,
delivery, and the stop-before-merge boundary:

```text
Target: Codex — repository execution
Outcome: [bounded repository change or review]
Repository and locality: [repository, worktree, branch, relevant surface]
Governed payload: [exact manifest or sealed-package identity]
Human direction and authority: [bounded declaration, owning reference, prohibitions]
Refresh: [repository, GitHub, planning, and provider facts to re-read]
Tools: [terminal, tests, Git, worktrees, commits, PR, or code review as applicable]
Validation and delivery: [canonical command, outputs, commit/push/PR expectation]
Stop boundary: [including no merge or other prohibited transition]
```

These shapes project the shared owner in
[`prompts.md`](../prompts.md#task-shape-surface-selection-and-thin-handoffs);
they do not redefine its package, authority, source-refresh, or failure
semantics.

#### Examples

1. **Difficult architecture discussion remains in Chat.** The human and Chat
   are still comparing authority boundaries and tradeoffs. No bounded
   deliverable or execution contract exists, so difficulty does not trigger a
   move to Work or Codex.
2. **Source-backed report moves from Chat to Work.** Chat establishes the
   question and authority boundary, then sends the Work-shaped envelope with
   an exact manifest identity, current source-refresh instructions, output
   checks, and return-to-Chat boundary. The complete recoverable package is not
   pasted into conversation.
3. **Repository implementation moves from Chat to Codex.** Chat establishes a
   bounded repository outcome, then sends the Codex-shaped envelope with the
   exact sealed-package identity, repository and worktree expectations,
   terminal and Git tools, canonical validation, PR delivery, and a
   stop-before-merge boundary.
4. **Discussion becomes delegated execution.** A task begins in Chat as an
   open-ended product discussion. It stays there until the human selects a
   bounded comparison report with accepted sources and review criteria; only
   then does it move to Work.
5. **Worker result returns to Chat.** Work returns the report identity,
   validation evidence, limitations, and output—not new authority. Chat is
   again the interactive surface for human review, interpretation,
   disposition, or next-step selection.
6. **Package reference fails closed.** A target receives only a mutable folder,
   or the named manifest is inaccessible, stale, digest-mismatched, or
   ambiguous. It stops the affected work or reports a non-authorizing partial
   result without rebuilding the missing payload from conversation memory.

## Connected apps, approvals, and consequential actions

An installed or authenticated app, available action, or product approval
setting describes capability or permission behavior; it does not expand the
human-authorized task. Keep consequential writes within the authorized scope
and re-observe their result before reporting the intended effect. The shared
authority, decision-boundary, and re-observation rules remain in
[`core-model.md`](../core-model.md), while connector availability is governed
by [`start-here.md`](../start-here.md#connector-availability-is-runtime-evidence).

For routine connected-app create or write operations, invoke only the write
and the minimum verification required by the owning evidence contract. Do not
invoke preview, thumbnail, open-in-provider, or share-link actions merely to
confirm success. Preview remains appropriate when the operator explicitly
requests visual inspection, rendered correctness requires it, or a narrower
owning workflow requires it. If the client renders a card from the write action
itself, classify that as client-enforced UI, avoid redundant preview calls or
model narration, and report the limitation when material rather than claiming
the card was suppressed. Current
[OpenAI Apps guidance](https://help.openai.com/en/articles/11487775-connectors-in)
documents rich in-chat app experiences and write confirmations, but does not
establish a universal per-action client-rendering suppression control.

### Recipient-Capability Prompt Presentation

Apply the complete shared
[`prompt delivery decision model`](../prompts.md#prompt-delivery-decision-model),
with the transport rules in
[`cross-executor prompt presentation`](../prompts.md#cross-executor-prompt-presentation).
Record the human operator or viewer and the executable prompt's execution
recipient as independent stage outputs before inspecting capability. The fact
that the operator asks to receive, view, or be given a handoff is evidence
about the operator-facing surface; it does not replace a resolved Codex,
Claude, Work, or other machine execution recipient with the human viewer.
Representative framing such as `prompt me`, `show me the Codex handoff`, and
`give me the prompt` remains upstream semantic evidence rather than a
transport selector or downstream renderer input.

Build stage 5 qualification only from the shared model's closed current-route
evidence record: the observed current runtime route, its route class and exact
identity, and the current owning route-qualification contract. Keep a
delegated task's target capability, acceptance criteria, desired future state,
implementation intent, prompt body, and explanatory rationale outside that
record. The fact that the delegated work is meant to strengthen or repair the
same capability does not make the route carrying that work unqualified. Do not
convert such task-target evidence into `route-disqualified` or `unresolved`;
only the current owning contract's classification of a current-route
observation may produce route disqualification.

For a machine execution recipient with qualified Dropbox retrieval and a
permitted destination, the model selects `file-backed` presentation. This
includes `qualified-with-known-limitation`: retain and report the diagnostic,
but do not reinterpret it as route disqualification. Use the authorized file
route, present the card produced by the write when available, and immediately
provide the target-shaped handoff. A separate preview or open action remains
optional under the connected-app rules above. Do not wait for prompt approval
or require the operator to open a preview; connector confirmation authorizes
only its file operation. File-card and preview behavior is product-dependent
runtime evidence, so recheck the relevant action.

For a human execution recipient, or a machine execution recipient whose
inspected capability state permits inline fallback, the model selects `inline`
presentation and the existing
[two-block inline renderer](#prompt-presentation). If access is unknown,
inspect or attempt it before resolving the route. Material prompts also apply
the durable profile below; routine prompts do not inherit it from transport.

Owner retrieval and output conformance remain separate checks. Only when the
frozen stage 5 record identifies a selected qualified Dropbox or file route
and the owning contract classifies a new failure against that same route class
and exact destination identity, with its reason, as `route-disqualified` before
a qualified prompt handoff is
complete may ChatGPT apply the canonical decision model's bounded capability
re-evaluation rule. A known non-disqualifying limitation is retained as
diagnostic evidence and does not activate re-entry. Sequence the owned failure
classification, the single downstream-only re-evaluation, and then the
terminal mapping from the resulting stage 5 state. Record there that bounded
re-evaluation was consumed. A newly qualified and permitted file route remains
file-backed only when its exact identity differs from the failed route; retain
the old failure as prior evidence, not as a disqualification of the new route.
Reasserting the same failed identity cannot force another file-backed attempt.
When no new file route qualifies and the owning contract
permits inline fallback, preserve the two-block complete-prompt shape and
report the disqualification reason outside the copyable blocks. If the
re-evaluated route also fails, stop blocked with that new reason rather than
re-entering or relabeling the failure as unresolved. Consume only the current
stage 5 record; a superseded pre-re-evaluation record cannot restart the bound.
When the governing exact-byte or durable contract prohibits that fallback,
preserve the target-shaped handoff with an explicit blocked state and stop. Do
not degrade the required prompt or handoff into unconstrained status prose
merely because one downstream prerequisite failed.

### Dropbox Preview And Minimal Executor Handoff

When optional operator preview is selected, complete the pre-link object-ID,
path, containment, and revision-when-exposed checks defined in the issue-owned
capture profile below. Then call Dropbox `file_preview` with `file_paths`
containing the exact `file_id` returned by the write. Use the exact returned
namespace path only when no file ID is available; never strip its namespace
prefix. Present the tool-produced widget before the final `download_link`
call.

The preview call and connector metadata are not a visibly rendered preview.
Do not substitute `open_in_dropbox_url`, copy or share links, thumbnail URLs,
or metadata for the widget, and claim visible rendering only when the operator
actually sees it. Preview remains optional and does not gate the handoff.

Keep the complete prompt in Dropbox. Outside the optional widget, emit only the
normal concise operator metadata and one compact retrieval, verification, and
execution bootstrap shown below; do not summarize or reproduce the prompt.

Thread routing: [FRESH THREAD | SAME THREAD | CHILD TASK]

Recommended model: [model]

Recommended reasoning level: [level]

Reason:
[one concise task-specific explanation]

```text
Download: [fresh single-use raw-download URL]
Dropbox ID: [exact returned file ID]
Expected bytes: [byte count]
Expected SHA-256: [digest]
Execute: Download once, verify the exact identity, byte count, and SHA-256, then execute the complete prompt file.
Stop: Fail closed on retrieval, identity, size, or SHA-256 mismatch. Do not reconstruct the prompt from chat or compare ordinary SHA-256 directly with Dropbox content_hash.
```

### Issue-Owned Durable Prompt Capture And Handoff

Apply the shared
[`issue-owned durable rendered-prompt handoff profile`](../prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile)
when ChatGPT prepares an exact prompt for another executor. For Dropbox's
qualified provider-checksum route, compute `content_hash` from the frozen
rendered bytes using Dropbox's documented algorithm. The concrete provider,
account, namespace, issue-path grammar, visibility, privacy, and retention
rules remain with the project or storage owner. Use its absent-create,
no-overwrite, and no-autorename semantics; a destination collision fails
closed.

After the write, complete the pre-link checks by re-observing and matching the
created object's non-empty file ID and path, its containment beneath the exact
issue destination, and its provider revision when exposed. When revision is
not exposed, record that unavailability explicitly; never fabricate it.
Perform zero controller verification content downloads in that qualified
attempt. Extracted text alone is not exact-byte readback. Defer authoritative
stored size and `content_hash` evidence to the final link response. Optionally
preview the file, then call
`download_link` exactly once. Require its returned file ID, path, stored size,
and `content_hash` to match the created object; require a non-empty returned URL,
keep `content_hash` distinct from ordinary whole-file SHA-256, and leave the URL
unconsumed for the executor. Do not report `PRESERVED` until that comparison
succeeds. Missing or mismatched evidence uses the shared fail-closed raw-readback
fallback.

## Workspace Agents

Workspace Agents are a ChatGPT execution surface, not a second adapter.

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

### Prompt presentation

Consume the frozen stage outputs from the shared
[prompt delivery decision model](../prompts.md#prompt-delivery-decision-model).
ChatGPT must not reclassify the produced artifact, replace the execution
recipient with the operator or viewer, or reconsider transport from request
wording or diagnostic limitations during rendering. The final application
executes the selected file-backed, inline, lightweight, or blocked action from
that record; it cannot select another renderer. Before any complete-prompt
renderer or delivery application is eligible, ChatGPT must materially realize
the complete current stage-5-through-7 state as one frozen decision record and
pass that record as the only delivery-decision input. Loose route,
qualification, presentation, or renderer fields; task prose; diagnostics;
rationale; and conversational context are not application inputs. Missing,
incomplete, stale, mismatched, or superseded records select no complete-prompt
renderer and fail closed. This explicit state boundary need not be displayed,
persisted, or implemented as a second workflow engine. Keep genuinely conceptual
fragments and incomplete snippets lightweight through the model's
`lightweight` renderer.

Do not begin either inline block unless `presentation-selection` produced
`inline` and `renderer-selection` produced `canonical-inline-two-block`.
`file-backed` uses only the thin-handoff renderer, and `blocked` uses no
complete-prompt renderer. When the model legitimately selects inline
presentation for a complete, copy-ready prompt or downstream handoff, present
the shared operator-metadata block followed immediately by the complete
executable block as consecutive copyable code blocks, with no intervening
prose. The shared canonical renderer controls the entire response surface:
emit no assistant-authored material before, between, or after the two blocks.
Do not add a copy instruction, navigation breadcrumb, Markdown separator,
prose label, or line-continuation escaping artifact. Keep the executable block
complete without metadata so the operator can copy only that block. This rule
applies only after the shared model has selected inline presentation; it does
not change classification, recipient, capability, Dropbox-backed routing, or
the treatment of quoted prompts, source excerpts, incomplete fragments, and
conceptual discussion. ChatGPT-targeted prompts resolve the
shared naming placeholder to nothing. This adapter does not ask ChatGPT to
rename itself or report a naming limitation. A downstream visible name may be
selected only when the downstream target executor adapter explicitly supports
executor-applied naming.

Bounded route re-evaluation must complete stages 5 through 7 again, freeze one
new current record, and supersede the prior record before application resumes.
Neither application nor bounded re-entry may consume the stale or superseded
record. A `file-backed` record therefore cannot reach the inline renderer, while
a legitimate `inline` record still reaches the canonical two-block surface.

Do not nest Markdown code fences inside the executable block; represent any
embedded example with indentation or plain text. Optimize this client rendering
for reliable copy/paste without changing the shared prompt meaning in
[`prompts.md`](../prompts.md).

## Generated artifacts

Creating a ChatGPT artifact in Chat or Work does not make it current
authoritative state or grant publication, sharing, overwrite, or adoption
authority. Apply the derived-artifact and consequential-action boundaries in
[`core-model.md`](../core-model.md) and the material-artifact contract in
[`prompt-contracts.md`](../prompt-contracts.md) when activated.

## Scheduled and unattended execution

Scheduled or unattended ChatGPT execution must project the current automation,
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
artifact as a whole before resuming. This is a ChatGPT projection of
[`source-first-retrieval.md`](../source-first-retrieval.md) and, for prompts,
[`prompts.md`](../prompts.md); it is not symptom-by-symptom repair from
conversation memory.

## Evidence and provider-reference boundary

This adapter defines Playbook behavior, not a provider guarantee about how
ChatGPT context, memory, permissions, or Work execution operates. The current
sources above establish only their documented selector, mode, and history
behavior; other client details remain runtime evidence. Re-check provider
behavior through authoritative current evidence when a task depends on it.
