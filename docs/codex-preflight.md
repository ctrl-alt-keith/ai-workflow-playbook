# Codex Preflight

## Purpose

`scripts/codex-preflight` is a small read-only check for stale local/session
prerequisites before Codex automation fan-out or real repository work begins.

It verifies:

- GitHub SSH authentication succeeds with `ssh -T git@github.com`
- `gh` is installed and authenticated
- the playbook repository is reachable through `git ls-remote`

When available, `ssh-add -l` is used only for diagnostic context. It is not a
readiness gate because some agent-backed flows, including 1Password SSH agent,
can authenticate to GitHub without listing identities through `ssh-add -l`.
The authoritative SSH readiness check is actual GitHub SSH authentication via
`ssh -T git@github.com`.

The script does not install tools, mutate Git state, change credentials, push,
commit, or update SSH configuration. SSH checks use batch mode and strict host
key checking so a missing `known_hosts` entry fails instead of being added by
the preflight.

## Usage

At the start of a Codex automation prompt, add a short preflight step before
delegating workers or touching repositories:

```text
Before starting repository work, run:

cd /Users/keith/src/ctrl-alt-keith/ai-workflow-playbook
./scripts/codex-preflight

If it exits non-zero, stop and report the failing check and remediation.
```

This catches common stale Monday-morning failures, such as broken GitHub SSH
authentication or an expired GitHub CLI session, while the task is still cheap
to restart.

Set `CODEX_PREFLIGHT_REPO_URL` only when checking a different GitHub repository
with the same read-only pattern.
