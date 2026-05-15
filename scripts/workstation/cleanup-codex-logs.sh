#!/usr/bin/env bash
set -euo pipefail

readonly DEFAULT_DB="${HOME}/.codex/logs_2.sqlite"
readonly DEFAULT_BACKUP_DIR="${HOME}/.codex/log-backups"
readonly EXPECTED_LOGS_SIGNATURE='id:INTEGER:0:1
ts:INTEGER:1:0
ts_nanos:INTEGER:1:0
level:TEXT:1:0
target:TEXT:1:0
feedback_log_body:TEXT:0:0
module_path:TEXT:0:0
file:TEXT:0:0
line:INTEGER:0:0
thread_id:TEXT:0:0
process_uuid:TEXT:0:0
estimated_bytes:INTEGER:1:0'

apply=0
db_path="${CODEX_LOG_DB:-$DEFAULT_DB}"
backup_dir="${CODEX_LOG_BACKUP_DIR:-$DEFAULT_BACKUP_DIR}"

usage() {
  cat <<'EOF'
Usage: cleanup-codex-logs.sh [--apply] [--db PATH]

Safely inspect or clean ~/.codex/logs_2.sqlite.

Default mode is dry-run inspection only. Pass --apply to back up the database,
refuse to continue if Codex-related processes are active, delete rows from the
verified logs table, and run SQLite maintenance.

Options:
  --apply       Mutate the database after process and schema safety checks.
  --dry-run     Inspect only. This is the default.
  --db PATH     Inspect or clean a specific logs_2.sqlite path.
  --help        Show this help text.
EOF
}

fail() {
  printf 'cleanup-codex-logs: %s\n' "$*" >&2
  exit 1
}

require_sqlite3() {
  if ! command -v sqlite3 >/dev/null 2>&1; then
    fail "sqlite3 is not installed or is not on PATH."
  fi
}

sql_quote() {
  local value=${1//\'/\'\'}
  printf "'%s'" "$value"
}

sqlite_ro() {
  sqlite3 -batch -bail -readonly "$db_path" "$1"
}

sqlite_rw() {
  sqlite3 -batch -bail "$db_path" "$1"
}

print_sizes() {
  local label=$1
  local found=0

  printf '%s sizes for %s*:\n' "$label" "$db_path"
  for path in "$db_path"*; do
    if [[ ! -e "$path" ]]; then
      continue
    fi
    found=1
    local bytes
    bytes=$(wc -c <"$path" | tr -d '[:space:]')
    printf '  %s  %s bytes\n' "$path" "$bytes"
  done

  if [[ "$found" -eq 0 ]]; then
    printf '  no matching files found\n'
  fi
}

list_codex_processes() {
  ps -axo pid=,comm=,args= | awk -v self="$$" '
    {
      pid = $1
      line = $0
      lower = tolower(line)
      if (pid == self) {
        next
      }
      if (lower !~ /codex/) {
        next
      }
      if (lower ~ /cleanup-codex-logs[.]sh/) {
        next
      }
      print line
    }
  '
}

require_codex_stopped() {
  local active
  if ! active=$(list_codex_processes); then
    fail "could not inspect active processes; refusing --apply."
  fi
  if [[ -n "$active" ]]; then
    printf 'Codex-related processes appear to be active:\n%s\n' "$active" >&2
    fail "stop Codex fully before running --apply."
  fi
}

require_db() {
  if [[ ! -e "$db_path" ]]; then
    printf 'No Codex log database found at %s. Nothing to do.\n' "$db_path"
    exit 0
  fi
  if [[ ! -f "$db_path" ]]; then
    fail "$db_path exists but is not a regular file."
  fi
}

logs_signature() {
  sqlite_ro "
    SELECT group_concat(signature, char(10))
    FROM (
      SELECT name || ':' || type || ':' || \"notnull\" || ':' || pk AS signature
      FROM pragma_table_info('logs')
      ORDER BY cid
    );
  "
}

require_expected_schema() {
  local logs_table_count
  logs_table_count=$(sqlite_ro "
    SELECT COUNT(*)
    FROM sqlite_schema
    WHERE type = 'table' AND name = 'logs';
  ")

  if [[ "$logs_table_count" != "1" ]]; then
    fail "expected one table named logs, found $logs_table_count."
  fi

  local actual_signature
  actual_signature=$(logs_signature)
  if [[ "$actual_signature" != "$EXPECTED_LOGS_SIGNATURE" ]]; then
    printf 'Unexpected logs table schema.\n\nExpected:\n%s\n\nActual:\n%s\n' \
      "$EXPECTED_LOGS_SIGNATURE" "$actual_signature" >&2
    fail "schema inspection failed; refusing to delete rows."
  fi
}

print_inspection() {
  local row_count
  row_count=$(sqlite_ro "SELECT COUNT(*) FROM logs;")

  local estimated_bytes
  estimated_bytes=$(sqlite_ro "SELECT COALESCE(SUM(estimated_bytes), 0) FROM logs;")

  printf 'Mode: %s\n' "$([[ "$apply" -eq 1 ]] && printf 'apply' || printf 'dry-run')"
  printf 'Database: %s\n' "$db_path"
  printf 'Schema: verified logs table\n'
  printf 'Log rows: %s\n' "$row_count"
  printf 'Estimated logged bytes: %s\n' "$estimated_bytes"

  if [[ "$apply" -eq 0 ]]; then
    local active
    if ! active=$(list_codex_processes 2>/dev/null); then
      printf 'Apply safety: could not inspect active processes; apply mode would refuse.\n'
    elif [[ -n "$active" ]]; then
      printf 'Apply safety: would refuse because Codex-related processes appear active.\n'
    else
      printf 'Apply safety: no Codex-related processes detected by this script.\n'
    fi
  fi
}

backup_database() {
  mkdir -p "$backup_dir"

  local timestamp
  timestamp=$(date '+%Y%m%d-%H%M%S')

  local backup_path="${backup_dir}/logs_2.sqlite.${timestamp}.bak"
  local backup_sql
  backup_sql=$(sql_quote "$backup_path")

  sqlite_rw "VACUUM main INTO $backup_sql;"
  printf 'Backup: %s\n' "$backup_path"
}

apply_cleanup() {
  backup_database
  sqlite_rw "
    PRAGMA wal_checkpoint(TRUNCATE);
    DELETE FROM logs;
    VACUUM;
    PRAGMA optimize;
  "
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --apply)
      apply=1
      shift
      ;;
    --dry-run)
      apply=0
      shift
      ;;
    --db)
      if [[ "$#" -lt 2 ]]; then
        fail "--db requires a path."
      fi
      db_path=$2
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

require_sqlite3
require_db

if [[ "$apply" -eq 1 ]]; then
  require_codex_stopped
fi

print_sizes "Before"
require_expected_schema
print_inspection

if [[ "$apply" -eq 0 ]]; then
  printf 'Dry-run only. Re-run with --apply after Codex is fully stopped to clean logs.\n'
  exit 0
fi

apply_cleanup
print_sizes "After"
printf 'Codex log cleanup completed.\n'
