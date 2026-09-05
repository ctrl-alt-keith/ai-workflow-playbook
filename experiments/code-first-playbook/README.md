# CAK-233 code-first shadow pilot

The CAK-233 persona previews remain experimental evidence only. The one
[Recovery section](recovery/README.md) now has a separate semantic-authored
ownership contract in `AGENTS.md`; all surrounding Playbook prose retains its
existing owners. No executor, router or automation consumes the persona
outputs. Permission is never evaluated and completion grants no authority.

## Authorization and bounds

Keith approved proposal v1 and its exact temporary AGENTS exception in
[CAK-233](https://linear.app/ctrl-alt-keith/issue/CAK-233)
decision comment `15e7f730-9b92-4218-b744-00e1967cc060`.
Approval recorded/activated: **2026-09-05T04:47:28Z** (first controller clock
observation after the explicit instruction; message timestamp not exposed).
Expiry: **2026-10-05T04:47:28Z**, or earlier human pilot disposition.
Expiry stops development and expansion; no automatic deletion or adoption.

Approved proposal: `id:FHKdoRfTdTUAAAAAAAAJvw`, SHA-256
`ae6752ddb17d74c91da38025577c8313bb90e1d0e146e9db89cffc19cb40ade1`.
Accepted architecture: `id:FHKdoRfTdTUAAAAAAAAJuQ`, SHA-256
`baa9cf60bfb537ea5b376e6b326ed8013c9f48e146037e802bf500f35e24f829`.

Exactly six units: startup-floor, conditional-activation, mode-persistence,
retrieval-triggers, claim-verification and retrieval-recovery (all prefixed
`pb.`). No decomposition is currently admitted by this implementation.
Interaction-mode and action-latch remain external source boundaries.
Only AI, Operator/SRE and Support views; at most two evaluation edit rounds.

## Use

From the owning repository worktree, run `make code-first-setup`, then
`make check` and `make code-first-source-check`.
Use `make code-first-render`, `make code-first-diff` and
`make code-first-rehearse` for explicit review artifacts.
Checks do not install dependencies or repair generated files.
The pilot virtual environment and build tree are ignored repository-owned state,
not durable evidence. Nothing is installed as a service or shared package.

Browse [generated/index.md](generated/index.md), [language.md](language.md),
the two semantic-owner modules, and the coverage/provenance maps.
An engineering renderer is unavailable; engineers inspect source and both human
views. A topic overview is never a complete execution contract.

## Removal

Preserve exact pilot/evaluation/review evidence under CAK-233 first.
If unmerged, leave main untouched and return branch/PR disposition to the human.
For a separately authorized removal PR, first preserve the operational Recovery
source, compiler dependencies, checks and setup identified in `AGENTS.md`, or
complete a separately authorized reverse ownership transition. The predecessor's
blanket directory/Make/CI removal recipe is no longer applicable. Preserve unrelated
edits and history. Verify no removed imports/consumers remain, run the then-current
`make check`, and stop for human merge authority. Only remove this experiment's
ignored dependency/build state after containment and evidence checks.
