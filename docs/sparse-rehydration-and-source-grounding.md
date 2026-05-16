# Sparse Rehydration And Source Grounding

## Purpose

This note records architectural rationale from sparse-context rehydration work:
the system became easier to reconstruct, inspect, and trust after prompt mass,
hidden state, and duplicated policy were reduced.

It is explanatory ecosystem philosophy, not a new startup dependency. The
executable workflow rules already live in the relevant playbook documents:

- source retrieval and evidence ordering:
  [`source-first-retrieval.md`](source-first-retrieval.md)
- repository execution, validation, worktree, and PR behavior:
  [`repo-readiness.md`](repo-readiness.md)
- Codex-specific execution deltas:
  [`tool-adapters/codex.md`](tool-adapters/codex.md)
- orchestration and worker-lane boundaries:
  [`orchestration-and-parallelism.md`](orchestration-and-parallelism.md)
- reusable prompt envelopes:
  [`prompts.md`](prompts.md)
- ecosystem repository roles:
  [`ai-workflow-ecosystem.md`](ai-workflow-ecosystem.md)

Do not promote this page into a shadow canon or second doctrine layer. Use it
to understand why the existing architecture works.

## Layer Boundaries

The playbook benefits from keeping four kinds of material separate:

- Operational policy defines what an agent must do during repository work.
  It belongs in the canonical playbook rule that owns the behavior, a tool
  adapter, or the repo-local `AGENTS.md` execution layer.
- Architectural rationale explains why the structure is shaped this way. It
  may guide future edits, but it should not create hidden requirements.
- Staging material explores unsettled ideas before promotion. It is not
  canonical unless a durable rule is explicitly moved into the playbook.
- Canonical workflow doctrine is reusable, source-grounded guidance that has
  earned promotion and belongs in a stable playbook document.

This page is architectural rationale. It should reinforce authority boundaries,
not blur them.

## What Sparse Rehydration Showed

Sparse rehydration worked because the system did not need a full conversational
memory image to behave coherently. It needed a compact routing entry point, a
small set of canonical sources, and enough topology to find the right source
before acting.

Reducing hidden state increased reconstructability. A later agent could rebuild
the working context from repository structure, current files, PR surfaces,
validation output, and cited docs rather than depending on an uninspectable
memory blob.

Reducing duplicated doctrine improved legibility. When rules were repeated in
prompts, adapters, local notes, and staging material, small wording differences
created semantic drift. Once authority returned to fewer source documents,
disagreements became easier to detect and review.

Reducing prompt mass improved source inspection behavior. Large onboarding
prompts encouraged continuity-first reasoning: the agent could sound informed
without reopening the current source. Sparse routing made missing retrieval
more visible, because the next step had to be found in the repo, PR, issue,
adapter, or validation path.

The central lesson is not that context is bad. The lesson is that hidden,
duplicated, and unreviewable context is a weak substrate for operational trust.

## Topology Can Substitute For Memory

A well-shaped repository ecosystem carries semantic authority in its topology.
The system can answer "what governs this?" by following structure:

- shared reusable workflow guidance belongs in the playbook
- executor deltas belong in tool adapters
- repo-specific execution details belong in repo-local `AGENTS.md`
- mechanical policy and drift checks belong in enforcement
- unsettled exploration belongs in incubation
- retained knowledge belongs in reviewed knowledge repositories

That topology does some of the work giant prompts often try to do. Instead of
placing every rule in every prompt, the startup path only needs to route the
agent to the controlling source. The authority lives in files, repository
boundaries, and PR history, not in conversational recall.

This is why sparse canonical routing can outperform giant onboarding prompts:
it improves the odds that an agent will inspect the current source of
authority instead of replaying a remembered copy.

## Source-First Operation

Conversational continuity behaves like an eventually consistent cache. It can
be useful for intent, tone, and navigation, but it may lag behind current
repository state, PR review, CI, branch history, provider behavior, or promoted
playbook guidance.

[`source-first-retrieval.md`](source-first-retrieval.md) treats summaries and
memory as leads, not proof. That reduces hallucinated continuity: the agent
cannot safely claim the branch is ready, the PR is clean, the issue is solved,
or the policy says something unless the controlling source has been inspected.

A polished completion report is still a summary. When a live PR, issue,
branch, check run, or file is referenced, inspect that source before relying on
the reported state. Coherent operational narratives are especially easy to
mistake for evidence because they already match the expected workflow shape.

This model also makes recovery clearer. When continuity outruns source
inspection, the repair is not more explanation. The repair is to retrieve the
authoritative source, mark unsupported assumptions, and continue from verified
state.

## Prompt Shape

Prompts should be executable routing envelopes, not policy blobs. A good prompt
names the repository, goal, scope, source evidence, validation path, stop
conditions, and expected deliverable. It should route the agent to canonical
rules rather than restating those rules in a second language.

This keeps prompts small enough to review and specific enough to execute. It
also limits drift: when a workflow rule changes, the canonical document changes
once, and prompts keep pointing at it.

The reusable templates in [`prompts.md`](prompts.md) follow that shape. The
Codex-specific worker-envelope constraints in
[`tool-adapters/codex.md`](tool-adapters/codex.md) and the lane model in
[`orchestration-and-parallelism.md`](orchestration-and-parallelism.md) are the
operational owners for executor behavior.

## PRs As Evidence Packets

Pull requests work as trust checkpoints because they compress evidence into a
reviewable package: changed files, rationale, validation output, discussion,
and merge history. They turn model-assisted work into something a later reader
can inspect without needing the original conversation.

That is review compression. The PR does not need to contain every intermediate
thought. It needs enough source-grounded evidence for a reviewer to evaluate
scope, correctness, authority boundaries, validation, and residual risk.

This is why `repo-readiness.md` keeps PRs small, scoped, and validated. The PR
surface is not ceremony; it is the durable trust boundary between execution and
retained change.

## Reliability Scar Tissue

Many of these properties came from reliability and distributed-systems
instincts, not from traditional prompt-engineering ideology:

- explicit authority boundaries prevent split-brain policy
- source-first reads avoid stale-cache decisions
- bounded autonomy limits blast radius
- small PRs create observable checkpoints
- canonical validation gives one local readiness signal
- worker envelopes make distributed execution debuggable
- idempotent routing beats hidden session state
- semantic deduplication reduces drift under change

Mature distributed systems do not scale by trusting every node to remember the
whole world. They scale by making authority explicit, constraining writes,
checking current state before action, and creating logs, checkpoints, and
rollback surfaces.

The same instincts apply here. A trustworthy AI workflow does not require a
giant prompt, hidden memory, or broad autonomy. It needs a small set of
inspectable sources, clear ownership, bounded execution rights, and reviewable
evidence.

## Semantic Compression

Trustworthy AI-assisted work may scale through semantic compression and
authority clarity instead of larger prompts. Compression does not mean losing
important context. It means replacing repeated prose with durable references,
reviewable topology, and source-grounded retrieval.

Useful compression looks like:

- a minimal startup route instead of a full policy transcript
- a repository role boundary instead of repeated ownership prose
- a worker envelope instead of inherited hidden context
- a PR packet instead of a conversation replay
- a canonical doc link instead of copied doctrine

The architecture improved after removing context because the remaining context
had clearer authority. Less prompt mass made the system easier to inspect. Less
duplicated policy made it easier to change safely. Less hidden state made it
easier to reconstruct the workflow from sources.

## Placement Guidance

Keep startup routing intentionally minimal. Do not add this page to the
mandatory read path in `docs/start-here.md`.

Use this page when changing architecture, explaining the ecosystem direction,
or evaluating whether a proposed workflow abstraction improves source-grounded
execution. For actual execution rules, follow the document that owns the
behavior.
