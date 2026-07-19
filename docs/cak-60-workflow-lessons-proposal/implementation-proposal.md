# CAK-60 Workflow Lessons Synthesis Proposal

Status: initial independent review findings resolved; focused re-review
**ACCEPT**; ready for proposal-only delivery; no repository implementation
authorized

Date: 2026-07-18 America/Los_Angeles

## 1. Decision requested

Approve a coordinated, proposal-first change across two repositories with a
strict ownership split:

- `ai-workflow-playbook` will own reusable operating semantics;
- `ai-workflow-playbook/docs/tool-adapters/codex.md` will own Codex-specific
  invocation and progress-rendering mechanics; and
- `ai-workflow-incubator` will own bounded observations, emergence history,
  limitations, counterexamples, and open questions from the CAK-53 through
  CAK-66 lineage.

The recommended content split is **75% Playbook / 25% Incubator** by semantic
weight. This is not a file-size target. Four existing Playbook files would be
amended, while one existing Incubator case study would receive a bounded
follow-up. No new normative chapter or parallel Incubator essay is proposed.

This proposal authorizes no doctrine or case-study implementation. After
independent review and explicit finding disposition, the frozen proposal
package will be delivered through two linked proposal-only draft pull requests,
one per repository. Human approval must bind to both exact proposal commits
before implementation may continue on those same branches and pull requests.

## 2. Interaction mode, evidence boundary, and source gate

The current run is implementation mode only for proposal, review, disposition,
validation, commit, push, and draft-PR delivery. It is not implementation mode
for the proposed Playbook or Incubator content changes.

The proposal is grounded in live Linear retrieval, connector-first GitHub
inspection, read-only `gh` verification, current fetched `origin/main` refs,
and repository-native source artifacts. Conversation history and the task text
were used only to identify sources and candidate lessons.

Verified repository baselines at drafting time:

| Repository | Verified `origin/main` | Visibility | Merge methods |
| --- | --- | --- | --- |
| `ctrl-alt-keith/ai-workflow-playbook` | `df7ae9ceb6379e35fbda7a0b4b94c763b9071316` | public | squash only |
| `ctrl-alt-keith/ai-workflow-incubator` | `93a7f688bb96a4f1ddf694ee81eb85ceb19acb6d` | private | squash only |
| `ctrl-alt-keith/knowledge-vault` | `1f8591b0dfff49b337d96a111d72808579d5baa6` | private | squash only |

The Knowledge Vault is inspected as historical and implementation evidence;
it is not a mutation target in this proposal.

The GitHub, local-ref, and Linear facts in sections 2 through 4 were verified
by Codex through the connected GitHub surface, read-only `gh`, local repository
inspection, and the connected Linear surface. The initial Claude reviewer had
local read access only: it could not execute `gh`, could not access Linear, and
could not independently compute the proposal digest. Those gaps are preserved
in the review record and will be closed by Codex verification plus a focused
read-only Claude GitHub verification pass before freeze. No source claim should
be attributed to an actor that did not verify it.

## 3. Current Linear authority and source lineage

Live Linear state was retrieved directly on 2026-07-18 America/Los_Angeles.

| Issue | Current state | Role in this proposal |
| --- | --- | --- |
| CAK-59 | source retrospective | Frozen observation, maturity, disposition, and target record, including reviewed rows 1-57 and 59-62; row 58 is intentionally unused. |
| CAK-60 | Backlog | Cross-repository implementation coordinator and current synthesis lineage. |
| CAK-61 | Done | Playbook doctrine implementation. |
| CAK-62 | Done | Workflow-operational reference implementation and primary emergence chronology. |
| CAK-63 | Done | Prompt-contract semantics, adapter boundary, and bounded K1 implementation. |
| CAK-64 | Done | Bounded Incubator disposition and CAK-63 follow-up. |
| CAK-65 | Done | Durable implementation-record closeout and post-merge reconciliation precedent. |
| CAK-66 | Done | CAK-62 non-canonical Incubator case study. |

CAK-59's seven current comments were retrieved directly. The relevant frozen
source records are:

- rows 1-8: `1d6b71e0-c3f3-48ec-97a1-9b399ad9a0f9`;
- rows 9-19: `1e4ea570-0707-4030-b393-7f238301110b`;
- rows 20-30: `ae43163b-a538-4932-8ffd-760a85340b17`;
- rows 31-40: `7538af1d-529c-4488-858d-62ec6235e160`;
- rows 41-51: `e3a49d8a-c770-4619-af72-ed19f5667e96`;
- audit additions 52-57 and 59-62: `d04cc6d3-cedb-494a-90c8-97bc33a82bea`; and
- freeze-before-implementation guidance:
  `faa2cfa6-c8c1-4a71-a88c-857a4c95f8c1`.

The candidate lessons most directly extend CAK-59 rows 5, 9-17, 20, 21, 24,
29, 39, 41-51, 54, 57, 59, 61, and 62. Rows 18, 19, and 30 remain open
questions and must not be silently answered by this synthesis.

## 4. Merged GitHub and repository-native evidence

All source PRs below were inspected directly and are currently merged. Because
the repositories allow squash only, the resulting integrated identity is the
squash commit, not a merge commit created by a merge-commit strategy.

| Track | Pull request | Reviewed head | Resulting integrated identity | Material evidence |
| --- | --- | --- | --- | --- |
| CAK-61 | Playbook #289 | `9b50fa0843cc25646f137dff24feb838d742e63e` | `b087e1250f7b4d2eb60d8f4b6cda0319da8e1375` | Exact approval identity, phase boundaries, review packets, same-PR allowance, evidence lifecycle, durable receipts. |
| CAK-62 | Knowledge Vault #74 | `a220606757f3fc96a859a772c20e69d62152b01a` | `16b17a61fca719c79a7d05928cb2d0e384f808e0` | Proposal, human approval artifact, serial batch authorizations, compact review, same-PR boundary, preparation, reconciliation. |
| CAK-63 architecture | Knowledge Vault #75 | `b3c154ee8e51f8a1c40b9c0f876fd77ebde1b824` | `d6f5f26f0db3f320489599c88f503558c4082925` | Proposal, independent review, complete disposition, and ADR. |
| CAK-63 semantics | Playbook #290 | `dafed7f8a614eb76ee4e8a85886c5b3266edb26c` | `df7ae9ceb6379e35fbda7a0b4b94c763b9071316` | Shared prompt-contract semantics, capability mapping, live authority, Codex adapter. |
| CAK-63 K1 | Knowledge Vault #76 | `17d87d0cd4bef6427c5a88d6bddcc67f1d5cf430` | `850828587950cc7171e68e63137e47642beaa42a` | Bounded implementation, review-found gaps after passing tests, exact receipt and reasoning-class fixes. |
| CAK-66 | Incubator #99 | `848c991bab14f0b3556cffe565aa69f6867a66c9` | `b05cc5f3848467a0a5cbd216a0fdfd93bb874051` | Non-canonical CAK-62 emergence chronology and limitations. |
| CAK-64 | Incubator #101 | `f5fae60b7d540e896abfbd5f9ceb5bd89dfedd8f` | `93a7f688bb96a4f1ddf694ee81eb85ceb19acb6d` | Proposal-only PR, direct Claude review, explicit disposition, focused re-review, same-lineage follow-up. |
| CAK-65 | Knowledge Vault #77 | `d5825965416cbba4649169148f7858eb5a22146f` | `1f8591b0dfff49b337d96a111d72808579d5baa6` | Proposal-first delivery, repository-native review, exact row closeout, actual merge identity, post-merge Linear reconciliation. |

The principal repository-native review artifacts inspected were:

- CAK-62 proposal and human approval record;
- CAK-63 proposal, independent Claude review, finding disposition, and ADR;
- CAK-64 proposal, original review, disposition, final review, and focused
  delivery-workflow re-review;
- CAK-65 proposal, Claude architecture review, and disposition; and
- the CAK-62 Incubator case study with its CAK-63 postscript.

## 5. Current Playbook doctrine inventory

The Playbook already owns most primitives. The proposal must amend existing
owners instead of introducing a parallel lifecycle manual.

| Existing owner | Current adequate doctrine | Gap this proposal would address |
| --- | --- | --- |
| `docs/feature-lifecycle.md` | Semantic phase boundaries; exact reviewed identity; narrow same-PR implementation/approval allowance; durable stage receipts; retrospective freeze; PR/Linear coordination. | No bounded proposal-first lifecycle or explicit proposal-only PR applicability rule; no explicit record of implementation head versus resulting integrated identity; post-merge reconciliation is present but incomplete. |
| `docs/review-packet.md` | Decision-first review surface; approval identity and validity; doctrine provenance; direct PR inspection; post-merge planning-status note. | No first-class finding-disposition contract; no explicit reviewer capability/source-verification ledger; no conditional second-review decision framed around continued applicability. |
| `docs/external-ai-reviewer.md` | Provider-agnostic targeted external review and stop-on-missing-evidence behavior. | Current wording assumes lightweight, optional, non-blocking PR review after implementation. It does not cover independent artifact review before a high-risk or explicitly governed implementation, direct invocation, actor/source capability boundaries, preserved output, or disposition. |
| `docs/tool-adapters/codex.md` | Source-first behavior, explicit phase boundaries, capability mapping for material prompts, worktree rules, autonomous lane, delivery receipts. | No Codex-specific direct reviewer invocation pattern and no concise workflow-state progress-rendering guidance. |
| `docs/alignment-checkpoints.md` | Pause on phase changes and new branch/PR rules. | Adequate; amend only if implementation reveals a missing cross-link. No planned edit. |
| `docs/repo-readiness.md` | Interaction modes, PR isolation, draft-PR conditions, GitHub/planning-system ownership, canonical validation. | Adequate. Avoid duplicating proposal-first or post-merge language here. No planned edit. |
| `docs/core-model.md` | Authority/capability distinction and protocol phases. | Adequate. No planned edit. |
| `docs/evidence-lifecycle.md` | Evidence freeze, semantic accounting, validation boundary. | Adequate. No planned edit. |
| `docs/prompt-contracts.md` | Product-neutral capability declarations, fresh/replay identity, live authority. | Useful analogy, but this task should not turn independent reviewers into prompt-contract consumers or copy prompt semantics. No planned edit. |

## 6. Current Incubator case-study inventory

| Existing material | Coverage | Consequence |
| --- | --- | --- |
| `experiments/2026-07-17-cak-62-emergent-workflow-architecture.md` | Proposal chronology, independent review, finding resolution, exact identity, serial authorization, same-PR approval, layered evidence/authority model, human-effort shift, limitations, and the CAK-63 postscript merged by CAK-64 PR #101. | Primary edit owner. Extend with a bounded CAK-60/61-66 same-lineage delivery follow-up instead of creating a second case study. The file already owns sequential post-experiment follow-up for this lineage. |
| `experiments/2026-07-18-cak-64-proposal/` | Source inventory, duplicate analysis, same-lineage claim calibration, direct reviewer capability gap, finding dispositions, focused re-review. | Evidence and precedent. Do not restate the package as a new framework. |
| `experiments/2026-07-10-evidence-driven-multi-agent-convergence.md` | Human-leverage shift and evidence-driven contract revision. | Avoid duplicating the generalized human-leverage claim. |
| `workflow-patterns/operational-friction-as-evidence.md` | Friction as experiment input and observe/clarify/retest loop. | Avoid a second general friction theory. |
| `workflow-patterns/role-based-autonomous-engineering-stewardship.md` | Speculative feedback-loop and role-boundary material. | Do not use as proof; leave its evidence gaps intact. |
| `architecture/solo-operator-operational-architecture-2026-05-14.md` | Review compression, bounded execution, reconciliation, and promotion constraints. | Avoid another architectural overview. |

## 7. Lesson-by-lesson ownership and publication decision

| Candidate lesson | Playbook | Codex adapter | Incubator | Omit / calibration |
| --- | --- | --- | --- | --- |
| Proposal-first delivery | Add a **conditional recommended lifecycle** for material, ambiguous, cross-repo, policy-sensitive, or high-risk work. | Render the current phase and closed/open transition criteria. | Record that CAK-62 through CAK-65 used the pattern and uncertainty concentrated before implementation. | Do not make it universal or require it for small mechanical changes. |
| Proposal-only PR as approval artifact | Recommend when a durable collaborative approval surface is proportionate; preserve exact proposal commit, continue bounded implementation on the same branch/PR, and require distinct final merge authorization. | State how Codex stops after proposal delivery and resumes only from exact approval. | Record proposal PRs as the observed topology, including corrections on the same proposal PR. | Do not prescribe it for trivial changes or repos whose local policy requires a different topology. |
| Direct independent reviewer invocation | Define a provider-neutral **independent review adapter**: exact artifact identity, reviewer identity, declared capabilities, read-only access, source retrieval, independent verification, preserved output, and evidence authority. | Prefer Codex directly invoking the reviewer against exact artifacts; Claude may be an example, not the semantic requirement. | Record the shift from conversational/copy-paste transport toward direct artifact invocation and the remaining access gaps. | Do not make Claude transport universal. |
| Reviewer capability boundaries | Require explicit material gaps, authorized follow-up verification, actor-to-source attribution, and no unsupported verification claim. | Record available tools/access and route inaccessible authority back to Codex or another authorized tool. | Preserve CAK-64/65 cases where Claude lacked Linear or GitHub in one review pass. | Do not treat reviewers as oracles or capability declarations as authority. |
| Finding disposition | Require every substantive finding to be accepted, accepted with modification, reasoned declined, superseded, or verified externally, connected to the frozen artifact. | Summarize counts, unresolved findings, and exact next boundary. | Record that dispositions preserved assurance and auditability across the lineage. | Do not require a taxonomy for trivial nit-only reviews. |
| Conditional second review | Govern with: **Is the original review still applicable to the frozen proposal?** Define no re-review, focused re-review, and fresh/full-review outcomes. | Render the selected review outcome and rationale. | Record CAK-64's focused delivery-workflow re-review and CAK-63's full architecture rework as contrasting cases. | Do not use “the file changed” as the sole criterion. |
| Phase boundaries and transition criteria | Add proposal/review/disposition/freeze/approval prerequisites to the existing lifecycle without making worktrees semantic requirements. | Treat worktree creation as an execution signal governed by repo policy, not universal doctrine. | Record that worktree creation was an observed phase-transition signal in this lineage. | Rows 18/19 remain open; no optimal gate count is claimed. |
| Workflow-native progress reporting | Define observable, evidence-based status fields by cross-linking stage receipts and review packets. | Add concise Codex rendering guidance: current phase, satisfied prerequisites, findings/dispositions, capability gaps, exact artifacts, preserved invariants, unmet criteria, next permitted action. | Record the observed shift from model-activity narration to governed workflow state. | Do not require verbose narration or private reasoning disclosure. |
| Merge identity abstraction | Record approval against pre-merge implementation head and completion against the actual integrated identity produced by allowed merge method. | Report both identities after direct verification. | Record that all source repos were squash-only and that merge-commit assumptions failed in CAK-65. | Do not assume merge commits or mandate a merge method. |
| Post-merge live-authority follow-up | Require separate, revalidated reconciliation when an external authority tracks completion: retrieve live state, record integrated identity, update/backlink if needed, verify final state. | Use direct tool retrieval and avoid replaying a transition already performed automatically. | Record CAK-65 as one same-lineage instance and note automation/permission limitations. | Do not make Linear mandatory or let external systems override GitHub repository state. |
| Implementation became more mechanical after freeze | None as doctrine beyond bounded implementation against approved scope. | None beyond scope-check reporting. | Publish as a bounded observation with counterexamples: later review still found receipt-binding and reasoning-class gaps. | Do not claim freeze eliminates implementation judgment. |
| Disposition can carry assurance otherwise sought through repeated review | Add only the applicability-based re-review decision rule. | None beyond reporting the decision. | Preserve as a hypothesis/observation from this lineage. | Do not claim equivalence between disposition and independent re-review. |

## 8. Duplicate analysis and smallest adequate change

The candidate lessons overlap heavily with existing doctrine. The smallest
adequate change is an amendment set, not a new lifecycle chapter.

1. `feature-lifecycle.md` is the existing lifecycle, phase-boundary, same-PR,
   merge, and external-coordination owner.
2. `review-packet.md` is the existing exact-identity, human decision,
   approval-validity, and doctrine-provenance owner.
3. `external-ai-reviewer.md` is the existing provider-neutral reviewer-mode and
   invocation owner, but its current lightweight-only framing must be revised
   conditionally. `review-packet.md` remains the single owner of finding
   disposition and re-review applicability.
4. `tool-adapters/codex.md` is the existing Codex-specific behavior owner.
5. The CAK-62 case study is already the Incubator lineage owner and was updated
   by merged CAK-64 PR #101 at integrated identity
   `93a7f688bb96a4f1ddf694ee81eb85ceb19acb6d`. The retained CAK-64 package README
   preserves its proposal-only historical state and is not current hosted
   status. A second case-study file would split a follow-up sequence that the
   existing case study already owns. The added section must remain explicitly
   a same-lineage postscript and must not revise the original CAK-62 chronology
   or broaden the file into a general workflow manual.

No update is proposed to `core-model.md`, `evidence-lifecycle.md`,
`repo-readiness.md`, `alignment-checkpoints.md`, `prompt-contracts.md`, or
Incubator architecture/workflow-pattern files unless implementation reveals a
broken link or unavoidable owner gap. Such a discovery would reopen the
approved scope and require renewed review before editing.

## 9. Proposed Playbook files and exact semantic changes

### `docs/feature-lifecycle.md`

- Add a conditional proposal-first lifecycle near Design / Branch and PR Rules.
- Define applicability by risk, ambiguity, cross-repo ownership, policy impact,
  irreversible consequences, and review cost; explicitly exempt small,
  mechanical, low-risk changes.
- Define transition criteria from source-first discovery through proposal,
  independent review when selected or required, finding disposition, frozen
  exact proposal identity, human approval, bounded implementation, canonical
  validation, final human review, explicit merge authorization, and post-merge
  reconciliation.
- Define proposal-only draft PR continuation on the same branch/PR as a
  recommended bounded pattern, not a universal topology.
- Distinguish approved implementation head from the actual resulting integrated
  identity after merge.
- Extend issue/planning coordination with live post-merge reconciliation,
  backlinking, and verification of automatic status transitions.

### `docs/review-packet.md`

- Add a first-class finding-disposition surface linked to exact reviewed and
  frozen identities.
- Add reviewer identity, material capability gaps, and actor/source
  verification attribution when independent review affects a decision.
- Add the applicability-based conditional re-review rule and the three outcomes:
  no re-review, focused re-review, or fresh proposal/full review.
- Keep approval ownership human and do not turn review or disposition into
  execution authority.
- Own the disposition taxonomy and re-review applicability semantics here;
  other review guidance must cross-link rather than restate them.

### `docs/external-ai-reviewer.md`

- Explicitly revise the current blanket “advisory only, optional, never
  blocking” invariant into two proportional modes. This is a semantic policy
  change, not a wording-only clarification: lightweight targeted review remains
  optional and non-blocking, while governed independent artifact review may be
  a transition prerequisite when the human/task explicitly requires it or the
  selected high-risk workflow contract makes it proportional.
- Reconcile residual “advisory only,” “never blocking,” and “never required”
  language so it applies only to the lightweight mode; do not imply that a
  reviewer verdict itself grants authority.
- Define the two modes: lightweight targeted PR sanity check and governed
  independent artifact review for material work when explicitly selected by
  the human/task or when proportional risk justifies it.
- Define independent review semantics: exact artifact, reviewer identity,
  capability declaration, read-only access, source retrieval, independent
  verification, output preservation, evidence limits, and stop behavior.
- Cross-link to `review-packet.md` for the disposition contract and conditional
  second-review decision; do not duplicate those semantics here.
- Retain provider neutrality and proportionality; keep small mechanical changes
  out of the governed mode.
- Update reusable prompts to request capability gaps, source attribution,
  severity, exact anchors, and an explicit verdict without inviting redesign.

### `docs/tool-adapters/codex.md`

- Add a Codex-specific independent reviewer invocation section.
- Prefer direct invocation against exact repository artifacts and read-only
  source access over human copy/paste transport when available.
- Treat Claude as an example reviewer implementation; preserve the shared
  independent-review semantics across providers.
- Require Codex to independently close declared access gaps using an authorized
  connector/tool and record which actor verified which source.
- Add workflow-native progress-rendering guidance focused on observable state,
  evidence, invariants, unmet transition criteria, and exact next action.
- Explicitly exclude private chain-of-thought narration.

No new Playbook file is proposed.

## 10. Proposed Incubator file and empirical content

Update only:

`experiments/2026-07-17-cak-62-emergent-workflow-architecture.md`

Add a bounded `Postscript: CAK-60 same-lineage delivery follow-up` after the
existing CAK-63 postscript and before the conclusion. This location is selected
because the file already owns the CAK-62 experiment chronology and its merged
CAK-63 follow-up; the new section reports how that same proposal/review/freeze/
delivery lineage continued through CAK-61 to CAK-66. A standalone note would
repeat the CAK-62 setup, CAK-63 counterexample, source record, limitations, and
same-lineage caveat. The postscript must remain bounded, linkable, and visibly
separate from the original experiment; if implementation cannot preserve those
limits cleanly, the scope must return for review rather than silently becoming
a new essay. It will:

1. name the CAK-61 through CAK-66 same-lineage source set and exact merged
   identities;
2. describe the observed lifecycle from source-first discovery through
   post-merge reconciliation;
3. describe proposal PRs as the observed collaboration topology, not doctrine;
4. record the shift from copy/paste review transport to direct artifact
   invocation and the reviewer capability gaps that remained;
5. record that explicit disposition and focused re-review preserved review
   traceability in CAK-64/65;
6. record uncertainty concentration before freeze and more bounded
   implementation afterward, while noting CAK-63 review still found substantive
   implementation gaps after tests passed;
7. record worktree creation as an observed phase-transition signal, not a
   semantic requirement;
8. record the shift toward workflow-state progress reports;
9. record squash-only merge identity and post-merge Linear reconciliation as
   observed constraints; and
10. preserve benefits, limitations, counterexamples, and open questions,
    including rows 18, 19, and 30 and the lack of independent replication.

No new Incubator essay, taxonomy, checklist, workflow manual, or architecture
overview is proposed. `experiments/README.md` does not require an implementation
edit because it already indexes the case study accurately.

## 11. Semantic contract versus adapter capability split

Shared Playbook semantics:

- applicability and proportionality;
- exact artifact and actor identity;
- independent-review meaning;
- capability-gap declaration;
- source-verification attribution;
- finding disposition;
- re-review applicability;
- phase transition criteria;
- approval and merge identity;
- external-state reconciliation.

Codex adapter mechanics:

- direct reviewer invocation;
- tool/access declaration;
- Claude-specific command examples only if useful during implementation;
- independent closing of inaccessible-source gaps;
- concise progress rendering; and
- Codex stop/resume behavior at closed phase boundaries.

Incubator observations:

- how these surfaces emerged in this lineage;
- which artifacts and transports were actually used;
- observed benefits and friction;
- counterexamples and late-discovered defects;
- limitations, uncertainty, and open questions.

No Claude-specific transport is a shared semantic requirement. No Codex tool
name belongs in core doctrine. Reviewer capability is not reviewer authority.

## 12. Claim-calibration boundaries

The implementation must preserve these limits:

- CAK-53 through CAK-66 is one project lineage, not independent replication.
- Proposal-first delivery is recommended conditionally, not proven universally
  optimal.
- Proposal PRs reduced context reconstruction in this lineage; no controlled
  review-cost experiment establishes a universal effect size.
- Implementation became more bounded after freeze, but CAK-63 demonstrates that
  semantic review remained necessary after deterministic tests passed.
- Explicit disposition can preserve review applicability; it is not equivalent
  to another independent review.
- Direct reviewer invocation improves artifact identity and transport
  traceability when access is available; it does not guarantee reviewer
  independence, correctness, or complete authority access.
- Worktree creation was an observed signal and remains repository policy or
  implementation detail, not universal workflow doctrine.
- GitHub repository state and external planning state remain separately owned.
- The actual integrated identity depends on the allowed merge method.
- Rows 18, 19, and 30 remain open; this synthesis chooses no gate count and no
  canonical workflow-state representation.

## 13. Exact omissions and rationale

- No universal twelve-step lifecycle: the lifecycle is conditional and may be
  collapsed for low-risk work while preserving required semantic boundaries.
- No mandatory proposal PR for trivial changes: ceremony must be proportional
  to risk and ambiguity.
- No mandatory external reviewer for every change: governed review is selected
  by task authority or proportional risk; lightweight review remains optional.
- No Claude-only doctrine: reviewer semantics are provider-neutral.
- No reviewer-as-oracle language: capability and source limits remain explicit.
- No mandatory second review after every edit: applicability controls.
- No mandatory worktree doctrine beyond repo-local policy.
- No verbose progress template or chain-of-thought disclosure.
- No merge-commit assumption or prescribed merge method.
- No Linear-specific core requirement: Linear is one external planning authority
  example.
- No new Playbook chapter, Incubator manual, taxonomy, schema, validator, or
  enforcement mechanism.
- No changes to CAK-59 frozen rows or to completed CAK-61 through CAK-66
  historical artifacts outside the existing Incubator case-study owner.

## 14. Independent review plan and reviewer capability contract

Codex will invoke Claude directly against the exact proposal file and the
authoritative local source graph with read-only `Read` and read-only `gh`
commands. The reviewer brief will ask Claude to assess:

- doctrine versus observation ownership;
- duplication and smallest adequate change;
- overclaiming and same-lineage calibration;
- phase-boundary correctness;
- reviewer-independence and capability semantics;
- finding disposition and second-review criteria;
- adapter leakage into shared doctrine;
- applicability to small versus high-risk work; and
- the proposed two-PR delivery topology.

Claude must declare its reviewer identity, tools, accessible sources, and
material capability gaps. Linear is expected to be inaccessible to Claude and
must be recorded as a gap rather than inferred as verified. Codex has already
retrieved Linear directly and will re-verify every Linear-dependent correction
before freeze.

The independent review output will be preserved verbatim enough for audit.
Every substantive finding will receive one of:

- accepted;
- accepted with modification;
- reasoned decline;
- superseded; or
- verified externally.

After corrections, Codex will decide:

- no re-review when the original review remains applicable and changes only
  improve traceability, provenance, accounting, validation wording, or
  already-decided clarity;
- focused re-review when scope, ownership, claims, authority, acceptance
  criteria, omissions, review criteria, or delivery topology changes
  materially but the proposal remains recognizably the same; or
- fresh proposal and full review when the corrected artifact is no longer
  meaningfully the same proposal.

The recorded governing question is: **Is the original review still applicable
to the frozen proposal?**

Review execution result: the initial Claude review returned **ACCEPT WITH
CHANGES** with seven findings. All seven were explicitly dispositioned. A
focused pass was required because the initial Claude environment could not run
GitHub or digest checks. After a pass-specific environment failure, the
identical focused review ran with narrow read-only access, matched all eight
GitHub receipts and the corrected proposal digest, confirmed every finding
resolution, found no new defect, and returned **ACCEPT**. Linear remained an
explicit Claude capability gap and was verified by Codex through the connected
authority.

## 15. Proposal delivery topology

Two linked proposal-only draft PRs are required because each repository is an
independent unit of change and implementation will later occur in both.

### Playbook proposal PR

- Dedicated branch/worktree created only after review and disposition.
- Proposal package placed temporarily under
  `docs/cak-60-workflow-lessons-proposal/`.
- Contains only the frozen coordinated proposal, Claude review, and disposition.
- After human approval, implementation would continue on the same branch/PR.
- Before final merge, the branch-only project-specific proposal package must be
  removed from the Playbook tip while remaining in branch/PR history. The
  Playbook owns reusable guidance and does not retain project-specific proposal
  records; changing this removal outcome would be a scope change requiring a
  renewed proposal decision.

### Incubator proposal PR

- Dedicated branch/worktree created only after review and disposition.
- Proposal package placed under
  `experiments/2026-07-18-cak-60-workflow-lessons-proposal/`.
- Contains only the frozen coordinated proposal, Claude review, and disposition.
- After human approval, the bounded case-study update would continue on the
  same branch/PR.
- The proposal package is expected to remain as repository-native experimental
  provenance because that repository owns same-lineage observations and review
  history.

Both proposal copies must have identical proposal bytes and review/disposition
meaning. Human approval must name both exact repository commit identities. One
approval does not silently authorize the other repository.

## 16. Canonical validation plan

For `ai-workflow-playbook`:

1. Run `make check` from the dedicated proposal worktree.
2. Run `git diff --check origin/main...HEAD` as whitespace/conflict-marker
   sanity only.
3. Verify exactly three proposal-package files differ from `origin/main`.
4. Inspect final status, branch, and remote head.

For `ai-workflow-incubator`:

1. Verify the remote remains private.
2. Run `make check` from the dedicated proposal worktree.
3. Run `git diff --check origin/main...HEAD` as whitespace/conflict-marker
   sanity only.
4. Verify exactly three proposal-package files differ from `origin/main`.
5. Inspect final status, branch, and remote head.

Validation establishes repository conformance and proposal-package scope. It
does not approve the proposal's semantics.

## 17. Exact approval and implementation sequence

1. Complete source-first discovery and duplicate inventory. **Done.**
2. Draft this coordinated proposal in workspace scratch. **Current phase.**
3. Invoke Claude directly against the exact proposal and source graph.
4. Preserve the review and explicitly disposition every substantive finding.
5. Independently verify any Linear claim Claude cannot access.
6. Decide and perform no, focused, or full re-review using continued
   applicability as the criterion.
7. Freeze proposal, review, and disposition bytes.
8. Create one dedicated worktree and branch per repository.
9. Commit only the proposal/review/disposition package in each repository.
10. Run each canonical validation path and exact changed-file check.
11. Push both branches and open linked proposal-only draft PRs.
12. Record both exact proposal commit identities and stop.
13. Human reviews and explicitly approves, rejects, or requests changes to both
    exact proposal commits.
14. Only after exact approval, implement the four Playbook amendments and one
    Incubator case-study update on the same respective branches and PRs.
15. Run canonical validation, verify scope against the approved proposal, and
    stop for final human review.
16. Human separately authorizes each merge against the exact reviewed
    implementation head.
17. After each merge, retrieve the actual integrated identity and current live
    external issue state; add durable backlinks/update status only if needed;
    verify final state.

## 18. Acceptance criteria for this proposal-only run

- Source traceability covers CAK-59 through CAK-66 and all merged source PRs.
- Existing Playbook and Incubator owners are inventoried and duplicate analysis
  justifies every planned edit and omission.
- Every candidate lesson has an explicit Playbook, Codex adapter, Incubator, or
  omit decision.
- Claude independently reviews the exact proposal with declared capabilities
  and read-only source access.
- Every substantive finding is explicitly dispositioned.
- The re-review decision and rationale are recorded.
- Both repositories pass canonical validation with proposal-only diffs.
- Two linked draft PRs identify exact proposal commits and request human
  approval of those commits.
- No Playbook doctrine or Incubator case-study implementation begins.

## 19. Exact next permitted action

Freeze this proposal with its review and disposition, deliver identical package
meaning through one dedicated proposal-only draft PR per repository, run each
canonical validation path, record both exact proposal commit identities, and
stop for human approval. Do not begin Playbook doctrine or Incubator case-study
implementation.
