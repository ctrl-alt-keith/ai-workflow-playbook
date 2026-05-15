# Workstation Maintenance

This page covers manual workstation maintenance tasks that are intentionally
outside recurring automation.

## Codex Log Cleanup

`scripts/workstation/cleanup-codex-logs.sh` inspects or compacts the local
Codex SQLite log database at `~/.codex/logs_2.sqlite`.

Use this only as a manual maintenance tool. Do not run it from cron, launchd,
GitHub Actions, Codex automations, or other scheduled systems. The database is
local runtime state owned by Codex while Codex is running, so unattended cleanup
could race active writes or remove diagnostic logs before a human has decided
they are disposable.

Before applying cleanup, quit Codex fully. Apply mode refuses to continue when
Codex-related processes are detected.

Files touched in apply mode:

- `~/.codex/logs_2.sqlite`
- SQLite sidecar files matching `~/.codex/logs_2.sqlite*`, such as `-wal` and
  `-shm`, through checkpoint and vacuum maintenance
- a backup file under `~/.codex/log-backups/`

Dry-run mode is the default and only inspects the database:

```sh
scripts/workstation/cleanup-codex-logs.sh
```

Apply mode backs up the database, verifies the known `logs` table schema,
truncates the write-ahead log, deletes rows from `logs`, vacuums the database,
and runs SQLite optimization:

```sh
scripts/workstation/cleanup-codex-logs.sh --apply
```

For recovery, stop Codex, move the current database and sidecars out of the
way, copy the desired backup from `~/.codex/log-backups/` back to
`~/.codex/logs_2.sqlite`, then restart Codex. Keep the moved current files until
the restored database has been checked.
