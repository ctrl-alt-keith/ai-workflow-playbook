"""Provider read-only reconciliation. This module has no writer or admin import."""

from dataclasses import asdict
import json
import time
from typing import Protocol

from .model import Blocked, Observation, digest


class Reader(Protocol):
    def observe(self, op, known=()) -> Observation: ...


def inspect(op, expected, observation):
    objects = []
    for obj in observation.objects:
        matches = (obj.target == op.target and obj.size == len(obj.data) == len(expected)
                   and obj.data == expected and bool(obj.object_id) and bool(obj.revision))
        objects.append({"id": obj.object_id, "revision": obj.revision,
                        "target": asdict(obj.target), "size": obj.size,
                        "read_size": len(obj.data), "sha256": digest(obj.data),
                        "verification": "pass" if matches else "fail",
                        "correlated": obj.correlated})
    # Every returned identity remains visible, including same-ID revision drift.
    conflict = len(objects) > 1 or any(o["verification"] == "fail" for o in objects)
    verified = (len(objects) == 1 and not conflict and objects[0]["correlated"]
                and observation.complete and not observation.error)
    return {"kind": "observation", "objects": objects, "scope": observation.scope,
            "complete": observation.complete, "error": observation.error,
            "effect": "conflict" if conflict else "present" if objects else "unknown",
            "verified": verified, "expected_sha256": op.input_hash,
            "expected_size": op.size}


def known_objects(c, op_id):
    known = []
    for row in c.execute("SELECT evidence FROM observation WHERE op_id=? ORDER BY id", (op_id,)):
        evidence = json.loads(row[0])
        for obj in evidence.get("objects", []):
            if evidence.get("kind") != "acknowledgement" and not obj.get("correlated", False):
                continue
            pair = (obj["id"], obj["revision"])
            if pair not in known:
                known.append(pair)
    return tuple(known)


def project(store, c, op_id, *, fresh=False, gap=""):
    op, _ = store.load(c, op_id)
    dispatched = c.execute("SELECT * FROM dispatch WHERE op_id=?", (op_id,)).fetchone()
    rows = c.execute("SELECT id,at,evidence FROM observation WHERE op_id=? ORDER BY id", (op_id,)).fetchall()
    records = [json.loads(row["evidence"]) for row in rows]
    latest = records[-1] if records else {}
    conflict = any(r.get("effect") in {"conflict", "collision"} for r in records)
    verified = latest.get("verified", False) and not conflict and not gap
    status = "conflict" if conflict else "retained_verified" if verified else "hold" if dispatched else "prepared"
    return {"operation": op_id, "effect_id": op.effect_id,
            "attempt": dispatched["attempt"] if dispatched else None,
            "status": status, "may_have_submitted": bool(dispatched),
            "observation": dict(rows[-1]) if rows else None,
            "decision": store.decisions(c, op, time.time()),
            "fresh_observation": fresh, "reporting_gap": gap,
            "admission_boundary": "local-synchronous-call",
            "claim_ceiling": "local-test-only",
            "next_action": "review" if verified else "inspect/disposition" if conflict else "reconcile/disposition" if dispatched else "run under current grant"}


def observe_and_record(store, c, op, data, reader, attempt):
    try:
        observation = reader.observe(op, known_objects(c, op.op_id))
    except Exception:
        # Do not persist exception strings that may contain credentials or links.
        observation = Observation(error="read unavailable")
    evidence = inspect(op, data, observation)
    if observation.objects and not c.execute("SELECT 1 FROM dispatch WHERE op_id=?", (op.op_id,)).fetchone():
        evidence.update(effect="collision", verified=False)
    store.append(c, op.op_id, attempt, evidence)
    return project(store, c, op.op_id, fresh=True)


def reconcile(store, op_id, reader: Reader):
    with store.session() as c:
        op, data = store.load(c, op_id)
        attempt = store.attempt(c, op_id, "reconcile")
        return observe_and_record(store, c, op, data, reader, attempt)


def show(store, op_id):
    with store.session() as c:
        return project(store, c, op_id)
