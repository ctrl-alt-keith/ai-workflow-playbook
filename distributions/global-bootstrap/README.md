# Global Bootstrap Distribution

## Purpose

This is a consumable, non-authoritative distribution under
[`distributions/`](../README.md). It provides the one copy-ready router for
project startup without copying shared doctrine into repository-local
instructions. Canonical startup timing and continuity remain in
[`docs/start-here.md`](../../docs/start-here.md#global-bootstrap-persistence)
and [`docs/core-model.md`](../../docs/core-model.md).

Provider-specific installation, runtime interpretation, and hosted-surface
validation belong in the matching [tool adapter](../../docs/tool-adapters/).
This shared surface does not establish a provider destination or runtime
coverage.

## Canonical Router

[`bootstrap-router.md`](bootstrap-router.md) is the one copy-ready router body.
Do not maintain provider-specific copies or change it to encode provider
behavior. Its first-action and material-change trigger, retrieval failure
boundary, and post-bootstrap persistence are owned by the canonical sources
linked above.

Use these managed markers around the exact router body where a supported local
reconciliation surface applies:

```text
<!-- ai-workflow-playbook:global-bootstrap:start -->
[exact contents of bootstrap-router.md]
<!-- ai-workflow-playbook:global-bootstrap:end -->
```

The local validator compares only the marked body after normalizing outer
newlines, permitting unrelated content before or after it. Preserve the
markers when reconciling a managed body.

## Read-Only Validation

Run:

```text
make check-local-bootstrap
```

For every selected local file, the check extracts the managed body and compares
the normalized body with [`bootstrap-router.md`](bootstrap-router.md). It does
not create, edit, or replace local files. Missing required files, missing or
duplicate markers, and content drift fail with a remediation path.

Use explicit paths or selectors when validating a staged or fixture file. See
the supported options with:

```text
python3 scripts/check_global_bootstrap.py --help
```

## Local Reconciliation

After the canonical router changes, reconcile an existing marked local file
from [`bootstrap-router.md`](bootstrap-router.md), never from a copied body in
an issue, PR, or chat. The operator path is explicit:

```text
check -> plan -> review -> apply -> verified pass
```

```text
make check-local-bootstrap
make plan-local-bootstrap
make apply-local-bootstrap
make check-local-bootstrap
```

`check-local-bootstrap` remains read-only. `plan-local-bootstrap` is also
read-only: it reports already-current surfaces and renders the exact unified
diff for each managed body that needs replacement. Review that diff before
running the distinct, explicit `apply-local-bootstrap` command.

Apply accepts only a single existing marker pair in a regular UTF-8 file and
atomically replaces only the managed body, preserving unrelated prefix and
suffix content. It prepares the replacement from an observed file, then
immediately before replacement re-reads and compares the content, mode, and
file identity; an observed change fails closed. It verifies the result against
the canonical router. Missing, duplicate, malformed, or changed unsafe state
fails closed. It never creates a marker pair or performs broader provider-home
management.

This is a final pre-replacement snapshot check, not a cross-process lock or a
filesystem compare-and-swap primitive. An uncooperative writer that changes a
file after that final comparison and before the atomic path replacement cannot
be distinguished by this workflow; the command does not claim to prevent that
last filesystem scheduling race.

First-time installation is deliberately separate from reconciliation. Add and
review a marker pair around the canonical body through the installation process
before these commands can manage the file. Local reconciliation is an explicit
post-merge action; this repository change does not silently mutate local files.

## Installation Boundary

The router and reconciliation helper are repository deliverables. Updating
live instruction surfaces remains a separate local action: review the plan,
explicitly apply the marked-block substitution, and run the read-only check.
Do not edit repo-local instruction files merely to install this router.

## Unified Local Projection Workflow

Use the top-level commands to inspect every currently qualified
Playbook-managed local projection:

```text
make check-local
make plan-local
make apply-local
```

`check-local` reports current, drifted, skipped, or blocked state. `plan-local`
is read-only and prints the exact next action; no output needs to be parsed or
copied. If apply is interrupted, rerun the same command. Finish with
`make check-local`.

The aggregate updates only Playbook-owned local projections and blocks
unrecognized or unsafe state. It does not install or validate hosted provider
surfaces; follow the matching adapter for those boundaries.
