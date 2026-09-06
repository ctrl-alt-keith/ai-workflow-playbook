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
- In a fresh implementation worktree, run `make code-first-setup` before the
  first `make check` to establish the isolated Recovery semantic tooling.
  This is an explicit startup step; `make check` remains non-mutating and
  fails closed if the tooling is unavailable.
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

### CAK-233 legacy preview retirement

CAK-238 retires CAK-233's experimental AI, Operator/SRE and Support preview
pipeline, its preview-only provenance rebinding, and its mock transition
rehearsal. They have no operational reader or distinct continuing failure
boundary. The shared semantic source, parser, validator, diff, source binding,
provenance helper and focused Recovery checks remain only because the Recovery
contract below actively depends on them.

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

The retired previews' expiry and historical evidence do not revoke Recovery
ownership or stop its necessary generation and validation. This carve-out does
not widen generated ownership beyond Recovery. Implementation and validation
do not grant doctrine promotion or merge authority; those decisions apply to
the exact reviewed transition.
