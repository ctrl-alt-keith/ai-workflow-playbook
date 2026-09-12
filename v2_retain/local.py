"""Owned local destination for synthetic development inputs, not Dropbox proof."""

from dataclasses import asdict
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import uuid

from .model import Blocked, Object, Observation, Qualification, Target, digest, encode


def initialize_destination(path):
    path = Path(path).absolute()
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    with closing(sqlite3.connect(path)) as c, c:
        c.executescript("CREATE TABLE object (id TEXT PRIMARY KEY, revision TEXT, target TEXT UNIQUE, operation TEXT, data BLOB);")


def qualification(path, target, actor):
    path = Path(path).absolute()
    s = path.stat()
    return Qualification("owned-local", "1", digest(encode([str(path), s.st_dev, s.st_ino, actor]).encode()), target,
                         "repository-local-acceptance", "2026-09-12", "local")


class LocalReader:
    __slots__ = ("path", "target", "actor")

    def __init__(self, path, target, actor):
        self.path, self.target, self.actor = Path(path).absolute(), target, actor

    def observe(self, op, known=()):
        qualification(self.path, self.target, self.actor).require_local(op)
        if op.target != self.target or op.actor != self.actor:
            raise Blocked("read owner/target mismatch")
        with closing(sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True)) as c:
            rows = c.execute("SELECT id,revision,target,operation,data FROM object WHERE target=?", (encode(asdict(op.target)),)).fetchall()
        objects = tuple(Object(r[0], r[1], op.target, len(r[4]), r[4], r[3] == op.op_id and (not known or (r[0], r[1]) in known)) for r in rows)
        drift = bool(known) and any((o.object_id, o.revision) not in known for o in objects)
        return Observation(objects, True, "owned local target; operation column correlation", "version drift" if drift else "")


class LocalWriter:
    def __init__(self, path, target, actor):
        self.path, self.target, self.actor = Path(path).absolute(), target, actor
        s = self.path.stat()
        self.identity = (s.st_dev, s.st_ino)
        self.qualification = qualification(self.path, target, actor)

    def reader(self):
        return LocalReader(self.path, self.target, self.actor)

    def check_binding(self, op, actor):
        s = self.path.stat()
        if op.actor != actor or actor != self.actor or op.target != self.target or (s.st_dev, s.st_ino) != self.identity:
            raise Blocked("destination or actor binding changed")

    def submit(self, op, data):
        object_id, revision = str(uuid.uuid4()), str(uuid.uuid4())
        with closing(sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True)) as c, c:
            c.execute("PRAGMA synchronous=EXTRA")
            c.execute("INSERT INTO object VALUES (?,?,?,?,?)", (object_id, revision, encode(asdict(op.target)), op.op_id, data))
        return object_id, revision
