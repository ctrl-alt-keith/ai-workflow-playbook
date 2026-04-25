# Context Refresh Primitive

## Purpose

Rehydrate working context from a baseline brief plus verified repo state.

## When To Use

- New thread
- Lost context
- Before starting cross-repo work
- After meaningful repo drift

## Required Inputs

- Baseline brief
- Verified repo state via a local checkout, GitHub API, `gh`, or a repo-aware
  Codex workspace

## Failure Behavior

If repo state cannot be verified, use:

`unknown → repo state could not be verified`

## Notes

- Baseline briefs are not the source of truth.
- Repo state remains the source of truth.
- Context output is a snapshot or cache, not canonical state.

## Self-Contained Prompt

```text
Task:
Refresh working context for the GitHub org `ctrl-alt-keith` using `org-brief.md` as the baseline reference and current repo state as the source of truth.

Working Context:
- This is a fresh Codex thread with no prior context.
- The only provided input is `org-brief.md`.
- You must use the org brief as a baseline, not as the final authority.
- You must treat current repo state as source of truth.
- You must not rely solely on the org brief.
- Org: https://github.com/ctrl-alt-keith
- Repos to evaluate:
  - knowledge-adapters
  - ai-workflow-playbook
  - ka-destinations
- Local notes layer:
  - cross-repo-threads
  - reference only
  - not authoritative

Goal:
Produce a concise, decision-focused org context refresh that:
- identifies drift from the org brief
- reflects actual current repo state
- highlights cross-repo health
- surfaces concrete gaps and risks
- recommends the next highest-leverage moves

Required Inputs:

1. `org-brief.md` (baseline reference)
2. access to current repo state via one of:
   - local repository checkouts
   - GitHub API or `gh` CLI
   - Codex workspace with repository access

If repo state is not available or cannot be verified, Drift MUST use:
`unknown → repo state could not be verified`

Do not mark Drift as `accurate` based only on the org brief.

Scope / Constraints:
- Do not modify any repositories.
- Do not create issues or pull requests.
- Keep this staged, not playbook-canonical.
- Do not restate or summarize the org brief.
- Focus only on what changed, what matters now, and what to do next.
- Do not use external prompt context, hidden assumptions, or prior thread state.
- If repo state cannot be verified, say so explicitly using the required unknown format.
- Keep the final output within approximately 300-500 words.

Execution Steps:

1. Establish baseline
- Read `org-brief.md` first.
- Extract only the claims that need verification against repo state.

2. Verify repo state
- Check current repo state for each listed repository.
- Use repo state as source of truth for all conclusions.
- Use the org brief only to detect drift, not to fill verification gaps.

3. Apply repo-verification gate
- Before producing the final answer, explicitly verify each repo's current state from GitHub or a local repo checkout.
- Do not mark a repo as `accurate` based only on the org brief.
- For each repo:
  - If repo state was verified and matches the org brief, use:
    `accurate`
  - If repo state was verified and differs from the org brief, use:
    `changed → <one-line summary>`
  - If repo state could not be accessed or verified, use:
    `unknown → repo state could not be verified`

4. Produce Drift
For each repo, output exactly one of the verification-gated results above.

5. Produce Current State
For each repo, provide:
- purpose (1 sentence max)
- activity level: experimental / active / stable / unknown
- current focus (top 1-2 items only, or unknown if not verifiable)

6. Produce Cross-Repo Health
Assess whether the org still has a clean three-layer model:
- knowledge-adapters = ingestion
- ka-destinations = publishing
- ai-workflow-playbook = guidance

Call out only meaningful drift, overlap, or ambiguity.
Maximum 3 bullets.

7. Produce Gaps / Risks
- Maximum 5 bullets.
- Only concrete, actionable gaps or risks grounded in repo state.
- Do not include speculative risks.

8. Produce Next Moves
- Exactly 5 items.
- Each item must be small, high leverage, and directly actionable.
- Prefer moves that reduce ambiguity, unblock near-term work, or protect repo boundaries.

Validation Requirements:
- Ground all statements in verified repo state.
- Do not guess or infer missing information.
- Do not mark Drift as `accurate` unless the repo was actually verified.
- Do not convert org-brief claims into facts unless repo state verifies them.
- If something cannot be verified from repo state, you MUST use:
  `unknown → repo state could not be verified`
- If verification is partial, keep the verified portion and mark the unverifiable portion as unknown.
- If repo state cannot be verified, the repo's Drift entry MUST be:
  `unknown → repo state could not be verified`
- If repo access fails, unavailable sections must still use the required unknown format.

Output Format (strict):

# Org Context (Updated)

## Drift
- knowledge-adapters:
- ai-workflow-playbook:
- ka-destinations:

## Current State
- knowledge-adapters:
- ai-workflow-playbook:
- ka-destinations:

## Cross-Repo Health
- ...

## Gaps / Risks
- ...

## Next Moves
1.
2.
3.
4.
5.

Delivery Expectations:
- Plain text only.
- Single response only.
- No extra sections.
- No repetition of the org brief.
- Keep the writing tight and decision-focused.
- Stay within approximately 300-500 words total.

Complexity:
- medium

Model recommendation:
- default model (upgrade only if needed)

Estimated usage:
- tokens: ~6k-12k
- cost (API equivalent): low-medium
```
