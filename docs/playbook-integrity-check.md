# Playbook Integrity Check

The integrity check is a lightweight periodic review to keep this repository a playbook instead of a dumping ground.

Use this check to review new capture docs such as [`new-repo-bootstrap.md`](new-repo-bootstrap.md) before the repository accumulates one-off material.

## Goal

Confirm that the repository still contains reusable guidance rather than drifting into notes, implementation, or tool sprawl.

Notes repositories may be useful staging layers for high-signal material, but
promoted guidance should converge here so the playbook remains the canonical
source.

## When To Run It

Run the check when:

- a new workflow family is proposed
- several docs were added in a short period
- a capture step produces more material than expected
- the repo starts feeling harder to navigate or easier to misuse
- a periodic maintenance pass is due

## Notes Cleanup and Alignment

Use the notes cleanup lifecycle after promotion work has already landed in the
playbook:

1. notes
2. audit
3. remove or trim
4. re-audit
5. converge

In this lifecycle, the playbook remains canonical and notes remain a staging
layer. Use the [`Notes vs Playbook Alignment Audit`](prompts.md#notes-vs-playbook-alignment-audit)
prompt in [`prompts.md`](prompts.md) for the cleanup pass, then rerun it after
changes to confirm convergence.

## What To Look For

Look for:

- scope drift toward project-specific implementation
- duplicated guidance that should be merged
- notebook behavior such as raw notes, scratch thinking, or incomplete fragments
- weak guidance that describes ideas without telling people how to act
- tool-specific material leaking into core docs instead of adapter docs
- filesystem-based audits or prompts that do not define dataset boundaries and
  therefore invite traversal outside the intended project root or working
  directory

## Review Questions

Ask:

1. Is this content reusable across multiple projects?
2. Is it proven or necessary to explain the core model?
3. Is it specific enough to guide action?
4. Does it belong here, or in another repo?

If the answer is weak on multiple questions, the content probably does not belong in this repository in its current form.
