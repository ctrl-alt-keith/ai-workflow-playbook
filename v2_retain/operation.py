"""The only operation submit path; holds exclusion through synchronous call."""

import time

from .model import Blocked, MAX_OBSERVATIONS
from .reconcile import inspect, observe_and_record, project


def run(store, op_id, writer, actor, *, clock=time.time):
    # Material remote reads precede the admission exclusion, so a revocation
    # accepted while preflight is running wins the subsequent admission race.
    with store.session() as c:
        op, data = store.load(c, op_id)
        reader = writer.reader()
        if c.execute("SELECT 1 FROM dispatch WHERE op_id=?", (op_id,)).fetchone():
            attempt = store.attempt(c, op_id, "run")
            return observe_and_record(store, c, op, data, reader, attempt)
    writer.qualification.require_local(op)
    writer.check_binding(op, actor)
    try:
        preflight = reader.observe(op)
    except Exception as exc:
        raise Blocked("pre-submit observation unavailable") from exc
    with store.session() as c:
        op, data = store.load(c, op_id)
        attempt = store.attempt(c, op_id, "run")
        if c.execute("SELECT 1 FROM dispatch WHERE op_id=?", (op_id,)).fetchone():
            return observe_and_record(store, c, op, data, reader, attempt)
        if project(store, c, op_id)["status"] == "conflict":
            raise Blocked("prior conflict requires disposition")
        if c.execute("SELECT count(*) FROM observation WHERE op_id=?", (op_id,)).fetchone()[0] > MAX_OBSERVATIONS - 3:
            raise Blocked("insufficient observation capacity before admission")
        writer.qualification.require_local(op)
        writer.check_binding(op, actor)
        if preflight.objects:
            evidence = inspect(op, data, preflight)
            evidence.update(effect="collision", verified=False)
            store.append(c, op_id, attempt, evidence)
            return project(store, c, op_id, fresh=True)
        if not preflight.complete or preflight.error:
            raise Blocked("pre-submit target lookup incomplete")
        store.grant_valid(c, op, actor, clock())
        store.check_files()
        store.admit(c, op, attempt, clock(), {"grant": op.grant_ref, "grant_revision": "original",
                    "expires_at": op.expires_at, "actor": actor,
                    "route": writer.qualification.fingerprint,
                    "preflight_scope": preflight.scope, "boundary": "local-synchronous-call"})
        # No transferable permit, queue, retry, or callback between this final
        # check and the single synchronous call. Any refusal leaves the latch.
        try:
            store.check_files()
            writer.qualification.require_local(op)
            writer.check_binding(op, actor)
            store.grant_valid(c, op, actor, clock())
        except Blocked:
            store.append(c, op_id, attempt, {"kind": "not_sent", "reason": "final admission refused"})
            return project(store, c, op_id)
        try:
            acknowledged = writer.submit(op, data)
        except Exception:
            # A timeout/error is possible submission, never retry permission.
            try:
                store.append(c, op_id, attempt, {"kind": "possible", "reason": "submission response unavailable"})
                return project(store, c, op_id)
            except Exception:
                return {"operation": op_id, "status": "hold", "may_have_submitted": True, "reporting_gap": "post-submission store failure"}
        try:
            store.append(c, op_id, attempt, {"kind": "acknowledgement", "objects": [{"id": acknowledged[0], "revision": acknowledged[1]}]})
            return observe_and_record(store, c, op, data, reader, attempt)
        except Exception:
            return {"operation": op_id, "status": "hold", "may_have_submitted": True, "reporting_gap": "post-submission observation/report failure"}
