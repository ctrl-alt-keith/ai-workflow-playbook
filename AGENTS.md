# AGENTS.md

This repository uses the shared playbook in `docs/` as the canonical source for
general workflow rules. This file is the thin repo-local execution layer.
Repo-local rules take precedence only for repo-specific behavior.

## Startup And Interaction Mode

- Start with `docs/start-here.md` before repository or software work.
- Before acting, select the interaction mode from `docs/repo-readiness.md`:
  implementation, review/audit, or orchestration/prompt-authoring.
- Implementation agents make explicit repo changes and carry them through
  validation, commit, push, and PR delivery.
- Review/audit agents inspect and report findings without mutating the repo.
- Orchestration/prompt-authoring agents produce complete, self-contained
  handoffs or prompts unless explicitly asked to implement.

## Repo Scope

- This repo contains reusable AI workflow and playbook guidance.
- It does not contain implementation code or project-specific automation.

## File Placement

- Put core reusable guidance in `docs/`.
- Put tool-specific guidance in `docs/tool-adapters/`.
- Do not add project-specific logic or implementation examples.

## Local Execution

- Run commands from this repository working directory by default.
- For implementation changes, use one repository, one branch, one dedicated
  repo-local worktree under `.worktrees/`, and one pull request per change; see
  `docs/repo-readiness.md#pr-readiness`.
- Keep repository-owned working state repo-local and tool-owned working state
  under its tool's contract. Use attempt-local disposable scratch only for
  private mechanics that have no required post-attempt role; see
  `docs/repo-readiness.md#repo-local-workflow-state`.
- Follow the command-form preflight rule in `docs/repo-readiness.md`: use direct
  `git ...`, `gh ...`, `make ...`, `python ...`, repo-local scripts, and tool
  commands for ordinary repository operations.
- For standard `git` and `gh` work, preserve direct CLI execution at both the
  command-selection and execution-tool layers; disable implicit shell or
  login-shell behavior where the environment supports that.
- Before using `zsh`, `bash`, `sh`, `zsh -lc`, `bash -lc`, `sh -c`, aliases, or
  equivalent wrapper shells, confirm shell semantics are genuinely required;
  otherwise rewrite the operation into direct argv form.

## Validation

- Use `make check` as the canonical local validation entrypoint.
- Run `make check` before opening or updating a PR.
- `make check` runs Markdown lint and scanner unit tests.
- Treat direct validation tool calls as implementation details of the Makefile
  target.
- `make authoritative-source-check` runs advisory authoritative-source scanning;
  it is separate from `make check` and non-blocking unless a caller configures
  that workflow to be stricter.
- CI is the enforcement layer for required remote checks and for checks that
  local tooling cannot run.

## Branches

- Follow the branch naming guidance in `docs/feature-lifecycle.md`.
- For playbook documentation work, use concise descriptive branch names such as
  `docs/<short-name>` or `chore/<short-name>`.

## Pull Requests

- Target `main`.
- Include a clear summary and rationale.
- Include validation notes.
- Add `Closes #[issue number]` when applicable.

## Playbook Reference

- Start here: `docs/start-here.md`
- This playbook builds on the engineering baseline defined in
  `docs/engineering-baseline.md`.
- Codex runs must apply `docs/tool-adapters/codex.md` as part of startup.
- Claude runs must apply `docs/tool-adapters/claude.md` as part of startup.
- For general workflow rules, refer to the playbook documents instead of
  duplicating them here. Use `docs/core-model.md`,
  `docs/feature-lifecycle.md`, `docs/alignment-checkpoints.md`, and
  `docs/review-packet.md` as reference material for deeper workflow details.

### CAK-233 temporary code-first pilot exception

Notwithstanding Repo Scope and File Placement above, the human-approved CAK-233 implementation proposal v1 permits experimental semantic source, Python compiler/validator/diff/rendering and simulation code, focused fixtures/tests, and generated previews only under `experiments/code-first-playbook/`.

Outside that directory, this exception permits only this section, the focused `code-first-*` Makefile targets and their `make check` integration, and the pilot dependency-setup step in the existing `.github/workflows/markdownlint.yml`. Existing validation remains in place.

Scope is `pb.startup-floor`, `pb.conditional-activation`, `pb.mode-persistence`, `pb.retrieval-triggers`, `pb.claim-verification`, and `pb.retrieval-recovery`. At most twelve rule records may represent documented dependency decomposition within these six units. Interaction-mode and action-latch remain external canonical boundaries unless a new human scope decision explicitly includes them. Permit only AI, Operator/SRE and Support projections, two evaluation edit rounds, and simulation-only authority rehearsal.

Existing Playbook prose remains operationally canonical. All experimental sources, generated previews, diagnostics and simulations are evidence only. No live executor, startup/router, automation or production documentation consumes or adopts them. No policy change, authority inversion, generated-doc adoption, global rollout or Playbook–Enforcement runtime/import dependency is authorized.

`make check` includes the experiment's deterministic tests and committed-preview regeneration check. The separate `make code-first-source-check` verifies current external prose bindings for pilot evaluation/readiness claims; Recovery's generated body uses the permanent section contract below. It does not make unrelated prose edits depend on snapshot reapproval. Missing required tooling blocks the checks that need it and must be reported, not silently skipped.

This exception activates only under the explicit human decision approving the exact CAK-233 proposal and this exception. It expires at the earlier of the human's pilot disposition or 30 calendar days after that approval. At expiry, stop further development and expansion pending human disposition. Expiry does not delete evidence, adopt outputs, extract implementation, or grant removal/merge authority. A fresh explicit human decision is required for extension or removal. All other repository rules remain in force.

### Recovery generated-section ownership

The narrower CAK-235 ownership model supersedes the pilot's prose-canonical and
no-generated-doc-adoption restrictions **only for the Recovery body** at
`docs/source-first-retrieval.md#recovery`. Its sole authored normative body is
`action.retrieval-recovery/does`, owned by `pb.retrieval-recovery`, in
`experiments/code-first-playbook/semantics/source-retrieval.yaml`. The semantic
`source.retrieval` identity still names the surrounding document owner; the
section-specific author/reader mapping lives in `recovery/contract.json`.
All surrounding retrieval, precedence, verification, failure, authority and
executor rules retain their existing owners.

Only the marked Recovery body is generated; the rest of its reader document
remains hand-maintained. Authors edit the semantic action and explicitly run
`make code-first-recovery-render`. `make check` detects stale or hand-edited
Recovery output and provenance without repairing them. Review meaningful
changes through the shared semantic diff and generated prose diff; the focused
outgoing-envelope guard does not replace incoming-edge corpus review.

The existing semantic modules (including `semantics/startup.yaml`),
`provenance/sources.json`, restricted parser/model/validator, diff,
provenance helpers, Recovery section renderer/contract, focused tests,
requirements and Make/CI integration may support this one operational section
at their existing locations. This permanent, section-specific placement
permission avoids duplicating the compiler; it permits no other generated
section, new semantic-language construct, persona adoption, runtime controller
or cross-repository dependency.

CAK-233's remaining infrastructure and persona previews stay experimental and
retain the predecessor's original expiry and disposition boundary. That expiry
does not revoke Recovery ownership or stop its necessary generation and
validation. Pilot removal must preserve Recovery's named dependencies, or
follow a separately authorized reverse ownership transition; it cannot delete
them under the old blanket removal recipe. This carve-out does not renew or
widen the pilot. Implementation and validation do not grant doctrine promotion
or merge authority; those decisions apply to the exact reviewed transition.
