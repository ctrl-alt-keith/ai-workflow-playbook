"""Explicit operation A, bounded observations, and a non-rearmable latch.

Trusted participating processes on one host. The externally retained identity
detects replacement, not an adversarial or in-place rollback of the same inode.
"""

from contextlib import contextmanager, closing
from dataclasses import asdict, dataclass
import fcntl
import json
import os
from pathlib import Path
import sqlite3
import stat
import time
import uuid

from .model import Blocked, MAX_OBSERVATIONS, Operation, digest, encode

TABLES = {
    "installation": "id TEXT PRIMARY KEY, store_id TEXT NOT NULL, owner TEXT NOT NULL, schema_version INTEGER NOT NULL",
    "operation": "id TEXT PRIMARY KEY, spec TEXT NOT NULL, spec_hash TEXT NOT NULL, payload BLOB NOT NULL, target TEXT UNIQUE NOT NULL",
    "grant_record": "id TEXT PRIMARY KEY, op_id TEXT NOT NULL REFERENCES operation(id), spec_hash TEXT NOT NULL, owner TEXT NOT NULL, provenance TEXT NOT NULL",
    "revocation": "grant_id TEXT PRIMARY KEY REFERENCES grant_record(id), provenance TEXT NOT NULL, at REAL NOT NULL",
    "dispatch": "op_id TEXT PRIMARY KEY REFERENCES operation(id), attempt TEXT NOT NULL, admitted_at REAL NOT NULL, evidence TEXT NOT NULL",
    "attempt": "id TEXT PRIMARY KEY, op_id TEXT NOT NULL REFERENCES operation(id), kind TEXT NOT NULL, at REAL NOT NULL",
    "observation": "id INTEGER PRIMARY KEY, op_id TEXT NOT NULL REFERENCES operation(id), attempt TEXT NOT NULL REFERENCES attempt(id), at REAL NOT NULL, evidence TEXT NOT NULL",
    "decision": "id TEXT PRIMARY KEY, op_id TEXT NOT NULL REFERENCES operation(id), candidate TEXT NOT NULL, property TEXT NOT NULL, contract_ref TEXT NOT NULL, contract_hash TEXT NOT NULL, owner TEXT NOT NULL, verdict TEXT NOT NULL, expires REAL NOT NULL, provenance TEXT NOT NULL",
}


def schema():
    commands = []
    for name, columns in TABLES.items():
        commands.append(f"CREATE TABLE {name} ({columns});")
        for action in ("UPDATE", "DELETE"):
            commands.append(f"CREATE TRIGGER {name}_{action.lower()} BEFORE {action} ON {name} BEGIN SELECT RAISE(ABORT, 'immutable record'); END;")
    return "\n".join(commands)


def schema_identity(c):
    return [(r[0], r[1]) for r in c.execute("SELECT name, sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name")]


def expected_schema():
    with closing(sqlite3.connect(":memory:")) as c:
        c.executescript(schema())
        return schema_identity(c)


EXPECTED_SCHEMA = expected_schema()


def file_identity(path):
    s = Path(path).lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_uid != os.getuid() or stat.S_IMODE(s.st_mode) != 0o600 or s.st_nlink != 1:
        raise Blocked("store/lock must be private, owned regular files")
    return (s.st_dev, s.st_ino)


@dataclass(frozen=True)
class Identity:
    installation_id: str
    store_id: str
    owner: str
    database: tuple[int, int]
    lock: tuple[int, int]
    mode: str = "active"

    def json(self):
        return encode(asdict(self))

    @classmethod
    def parse(cls, value):
        v = json.loads(value)
        v["database"], v["lock"] = tuple(v["database"]), tuple(v["lock"])
        return cls(**v)


class Store:
    def __init__(self, path, identity):
        self.path = Path(path).absolute()
        self.lock_path = Path(str(self.path) + ".lock")
        self.identity = identity

    @classmethod
    def initialize(cls, path, owner):
        """Operator-only explicit initialization; never invoked by execution."""
        p = Path(path).absolute()
        if not owner or not p.parent.is_dir() or p.parent.resolve() != p.parent:
            raise Blocked("explicit owner and real parent directory required")
        # Partial initialization is a blocker; no overwrite or repair fallback.
        for f in (p, Path(str(p) + ".lock")):
            fd = os.open(f, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            os.fsync(fd)
            os.close(fd)
        installation_id, store_id = str(uuid.uuid4()), str(uuid.uuid4())
        with closing(sqlite3.connect(p)) as c, c:
            c.execute("PRAGMA journal_mode=DELETE")
            c.execute("PRAGMA synchronous=EXTRA")
            c.executescript(schema())
            c.execute("INSERT INTO installation VALUES (?,?,?,1)", (installation_id, store_id, owner))
        parent_fd = os.open(p.parent, os.O_RDONLY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
        identity = Identity(installation_id, store_id, owner, file_identity(p), file_identity(str(p) + ".lock"))
        return cls(p, identity)

    def check_files(self):
        if self.path.parent.resolve() != self.path.parent:
            raise Blocked("store parent changed")
        if file_identity(self.path) != self.identity.database or file_identity(self.lock_path) != self.identity.lock:
            raise Blocked("installation file identity changed; recovery-only")

    @contextmanager
    def session(self):
        fd, c = None, None
        try:
            self.check_files()
            fd = os.open(self.lock_path, os.O_RDWR | os.O_NOFOLLOW)
            if (os.fstat(fd).st_dev, os.fstat(fd).st_ino) != self.identity.lock:
                raise Blocked("lock identity changed")
            fcntl.flock(fd, fcntl.LOCK_EX)
            self.check_files()
            c = sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True, isolation_level=None)
            c.row_factory = sqlite3.Row
            c.execute("PRAGMA foreign_keys=ON")
            c.execute("PRAGMA synchronous=EXTRA")
            if c.execute("PRAGMA journal_mode").fetchone()[0] != "delete":
                raise Blocked("unsupported journal configuration")
            if c.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or c.execute("PRAGMA foreign_key_check").fetchone():
                raise Blocked("store corruption")
            if schema_identity(c) != EXPECTED_SCHEMA:
                raise Blocked("unsupported or corrupt schema")
            rows = c.execute("SELECT * FROM installation").fetchall()
            expected = (self.identity.installation_id, self.identity.store_id, self.identity.owner, 1)
            if len(rows) != 1 or tuple(rows[0]) != expected:
                raise Blocked("installation/store/owner mismatch")
            yield c
        except (OSError, sqlite3.Error, ValueError, TypeError, KeyError) as exc:
            raise Blocked("store unavailable or corrupt") from exc
        finally:
            if c is not None:
                c.close()
            if fd is not None:
                os.close(fd)

    def prepare(self, op, data, owner):
        op.validate(data)
        if owner != op.owner or owner != self.identity.owner:
            raise Blocked("wrong source/operation owner")
        with self.session() as c:
            if self.identity.mode != "active":
                raise Blocked("recovery-only installation")
            c.execute("BEGIN IMMEDIATE")
            c.execute("INSERT INTO operation VALUES (?,?,?,?,?)", (op.op_id, op.json(), digest(op.json().encode()), data, encode(asdict(op.target))))
            c.execute("COMMIT")

    def load(self, c, op_id):
        row = c.execute("SELECT * FROM operation WHERE id=?", (op_id,)).fetchone()
        if row is None or digest(row["spec"].encode()) != row["spec_hash"]:
            raise Blocked("operation missing or corrupt")
        op = Operation.parse(row["spec"])
        op.validate(row["payload"])
        if op.op_id != op_id or row["target"] != encode(asdict(op.target)) or op.owner != self.identity.owner:
            raise Blocked("operation binding mismatch")
        return op, row["payload"]

    def attempt(self, c, op_id, kind):
        if c.execute("SELECT count(*) FROM attempt WHERE op_id=?", (op_id,)).fetchone()[0] >= MAX_OBSERVATIONS * 2:
            raise Blocked("attempt capacity exhausted; explicit disposition required")
        attempt = str(uuid.uuid4())
        c.execute("INSERT INTO attempt VALUES (?,?,?,?)", (attempt, op_id, kind, time.time()))
        return attempt

    def append(self, c, op_id, attempt, evidence):
        if c.execute("SELECT count(*) FROM observation WHERE op_id=?", (op_id,)).fetchone()[0] >= MAX_OBSERVATIONS:
            raise Blocked("observation capacity exhausted; explicit disposition required")
        raw = encode(evidence)
        if len(raw.encode()) > 65536:
            raise Blocked("observation too large")
        cur = c.execute("INSERT INTO observation(op_id,attempt,at,evidence) VALUES (?,?,?,?)", (op_id, attempt, time.time(), raw))
        return cur.lastrowid

    def admit(self, c, op, attempt, now, evidence):
        c.execute("BEGIN IMMEDIATE")
        c.execute("INSERT INTO dispatch VALUES (?,?,?,?)", (op.op_id, attempt, now, encode(evidence)))
        c.execute("COMMIT")

    def grant_valid(self, c, op, actor, now):
        if self.identity.mode != "active" or actor != op.actor or not op.not_before <= now < op.expires_at:
            raise Blocked("actor, original expiry, or installation mode refuses admission")
        grant = c.execute("SELECT * FROM grant_record WHERE id=?", (op.grant_ref,)).fetchone()
        if (grant is None or grant["op_id"] != op.op_id or grant["spec_hash"] != digest(op.json().encode())
                or grant["owner"] != self.identity.owner or not grant["provenance"]
                or c.execute("SELECT 1 FROM revocation WHERE grant_id=?", (op.grant_ref,)).fetchone()):
            raise Blocked("grant missing, revoked, or scope changed")

    def decisions(self, c, op, now):
        if not op.decision_owner:
            return "not_required"
        rows = c.execute("SELECT verdict FROM decision WHERE op_id=? AND candidate=? AND property=? AND contract_ref=? AND contract_hash=? AND owner=? AND expires>?", (op.op_id, op.input_hash, op.decision_property, op.contract_ref, op.contract_hash, op.decision_owner, now)).fetchall()
        values = {r[0] for r in rows}
        return "pending" if not values else "conflict" if len(values) > 1 else next(iter(values))
