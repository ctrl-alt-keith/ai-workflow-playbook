from dataclasses import replace
from contextlib import closing
import importlib
import json
import multiprocessing
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from v2_retain.admin import Admin
from v2_retain.local import LocalReader, LocalWriter, initialize_destination
from v2_retain.model import Blocked, MAX_BYTES, Object, Observation, Operation, Target, digest
from v2_retain.operation import run
from v2_retain.reconcile import reconcile, show
from v2_retain.store import Store, Identity


def crash_run(path, identity, destination, op_id, seam):
    store = Store(path, identity)
    with store.session() as c:
        op, _ = store.load(c, op_id)
    writer = LocalWriter(destination, op.target, op.actor)
    def die():
        os.kill(os.getpid(), signal.SIGKILL)
    if seam in {"before_latch", "after_latch"}:
        original = store.admit
        def admit(*args):
            if seam == "before_latch":
                die()
            original(*args)
            die()
        store.admit = admit
    else:
        original = writer.submit
        def submit(*args):
            if seam == "during_call":
                die()
            result = original(*args)
            die()
            return result
        writer.submit = submit
    run(store, op_id, writer, op.actor)


def competing_run(path, identity, destination, op_id):
    store = Store(path, identity)
    with store.session() as c:
        op, _ = store.load(c, op_id)
    writer = LocalWriter(destination, op.target, op.actor)
    original = writer.submit
    def submit(*args):
        with open(str(destination) + ".calls", "ab") as f:
            f.write(b"1")
            f.flush()
            os.fsync(f.fileno())
        return original(*args)
    writer.submit = submit
    run(store, op_id, writer, op.actor)


class OperationTests(unittest.TestCase):
    def setUp(self):
        # Repository-owned fixture state, never a pilot/production store.
        root = Path(".v2-test-state")
        root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).absolute()
        self.store = Store.initialize(self.root / "state.db", "operator")
        self.destination = self.root / "destination.db"
        initialize_destination(self.destination)
        self.admin = Admin(self.store, "operator")

    def prepare(self, data=b"hello\n", name="o1", **changes):
        target = Target("local-account", "local-namespace", "parent", "/pilot/" + name)
        writer = LocalWriter(self.destination, target, "executor")
        now = time.time()
        op = Operation(name, "operator", "source:exact", "contract:C1", digest(b"C1"), "executor",
                       target, "grant:" + name, now - 60, now + 3600,
                       "retention:pilot-review", "visibility:local", digest(data), len(data), writer.qualification.fingerprint)
        op = replace(op, **changes)
        self.store.prepare(op, data, "operator")
        self.admin.grant(op.op_id, "human instruction fixture")
        return op, writer

    def objects(self):
        with closing(sqlite3.connect(self.destination)) as c:
            return c.execute("SELECT id,revision,operation,data FROM object").fetchall()

    def test_healthy_exact_text_binary_empty_and_distinct_equal_operations(self):
        for n, data in enumerate((b"hello\n", b"\x00\xff\r\n", b"", b"hello\n")):
            op, writer = self.prepare(data, "o" + str(n))
            self.assertEqual(run(self.store, op.op_id, writer, "executor")["status"], "retained_verified")
            self.assertFalse(show(self.store, op.op_id)["fresh_observation"])
            self.assertTrue(reconcile(self.store, op.op_id, writer.reader())["fresh_observation"])
            self.assertEqual(self.objects()[-1][3], data)
        self.assertEqual(len({r[0] for r in self.objects()}), 4)

    def test_pinned_input_and_no_latch_or_binding_mutation(self):
        op, writer = self.prepare()
        for table in ("operation", "grant_record"):
            with self.store.session() as c:
                with self.assertRaises(sqlite3.IntegrityError):
                    c.execute(f"DELETE FROM {table}")
        run(self.store, op.op_id, writer, "executor")
        with self.store.session() as c:
            for sql in ("DELETE FROM dispatch", "UPDATE dispatch SET attempt='replacement'", "DELETE FROM observation"):
                with self.assertRaises(sqlite3.IntegrityError):
                    c.execute(sql)
        self.assertEqual(run(self.store, op.op_id, writer, "executor")["status"], "retained_verified")
        self.assertEqual(len(self.objects()), 1)
        with self.assertRaises(Blocked):
            self.store.prepare(replace(op, op_id="other"), b"hello\n", "operator")

    def test_wrong_owner_actor_expiry_revoke_target_and_route_change(self):
        op, writer = self.prepare()
        with self.assertRaises(Blocked):
            Admin(self.store, "executor")
        with self.assertRaises(Blocked):
            self.store.prepare(replace(op, op_id="other"), b"hello\n", "other-owner")
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "wrong-actor")
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor", clock=lambda: op.expires_at)
        changed = LocalWriter(self.destination, replace(op.target, parent="wrong"), "executor")
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, changed, "executor")
        writer.qualification = replace(writer.qualification, build="changed")
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor")
        writer = LocalWriter(self.destination, op.target, "executor")
        self.admin.revoke(op.grant_ref, "explicit revocation")
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor")
        with self.assertRaises(Blocked):
            self.admin.grant(op.op_id, "cannot extend original grant")
        self.assertEqual(self.objects(), [])

    def test_required_accepted_decision_blocks_admission(self):
        op, writer = self.prepare(decision_owner="owner", decision_property="retain")
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor", require_accepted_decision=True)
        self.assertEqual(self.objects(), [])
        self.admin.decision(op.op_id, candidate=op.input_hash, property="retain", contract_ref=op.contract_ref,
                            contract_hash=op.contract_hash, owner="owner", verdict="accepted",
                            expires=op.expires_at + 10, provenance="fixture")
        self.assertEqual(run(self.store, op.op_id, writer, "executor", require_accepted_decision=True)["status"], "retained_verified")

    def test_final_gate_rechecks_expiry_and_keeps_latch(self):
        op, writer = self.prepare()
        ticks = iter([op.not_before + 1, op.not_before + 2, op.expires_at])
        self.assertEqual(run(self.store, op.op_id, writer, "executor", clock=lambda: next(ticks))["status"], "hold")
        self.assertEqual(self.objects(), [])
        self.assertTrue(show(self.store, op.op_id)["may_have_submitted"])
        run(self.store, op.op_id, writer, "executor")
        self.assertEqual(self.objects(), [])

    def test_crash_seams_fresh_process_and_competing_invocations(self):
        ctx = multiprocessing.get_context("spawn")
        for seam in ("before_latch", "after_latch", "during_call", "after_effect"):
            with self.subTest(seam=seam):
                op, writer = self.prepare(name=seam)
                p = ctx.Process(target=crash_run, args=(self.store.path, self.store.identity, self.destination, op.op_id, seam))
                p.start()
                p.join(15)
                self.assertEqual(p.exitcode, -signal.SIGKILL)
                state = show(self.store, op.op_id)
                self.assertEqual(state["may_have_submitted"], seam != "before_latch")
                result = run(self.store, op.op_id, writer, "executor")
                self.assertEqual(result["status"], "retained_verified" if seam in {"before_latch", "after_effect"} else "hold")
        op, writer = self.prepare(name="race")
        ps = [ctx.Process(target=competing_run, args=(self.store.path, self.store.identity, self.destination, op.op_id)) for _ in range(2)]
        for p in ps:
            p.start()
        for p in ps:
            p.join(15)
            self.assertEqual(p.exitcode, 0)
        self.assertEqual(len([r for r in self.objects() if r[2] == op.op_id]), 1)
        self.assertEqual(Path(str(self.destination) + ".calls").read_bytes(), b"1")
        with self.store.session() as c:
            self.assertEqual(c.execute("SELECT count(*) FROM dispatch WHERE op_id=?", (op.op_id,)).fetchone()[0], 1)

    def test_unknown_duplicate_conflict_and_unrelated_equal_object(self):
        op, writer = self.prepare()
        with patch.object(writer, "submit", side_effect=TimeoutError):
            self.assertEqual(run(self.store, op.op_id, writer, "executor")["status"], "hold")
        class EmptyReader:
            def observe(self, op, known=()):
                return Observation((), True, "empty does not establish absence")
        self.assertEqual(reconcile(self.store, op.op_id, EmptyReader())["status"], "hold")
        class DuplicateReader:
            def observe(self, op, known=()):
                return Observation(tuple(Object(id, "r1", op.target, 6, b"hello\n", True) for id in ("a", "b")), True, "local fixture")
        result = reconcile(self.store, op.op_id, DuplicateReader())
        self.assertEqual(result["status"], "conflict")
        self.assertEqual(len(json.loads(result["observation"]["evidence"])["objects"]), 2)
        self.assertEqual(reconcile(self.store, op.op_id, EmptyReader())["status"], "conflict")
        op2, writer2 = self.prepare(name="collision")
        writer2.submit(replace(op2, op_id="external"), b"hello\n")
        self.assertEqual(run(self.store, op2.op_id, writer2, "executor")["status"], "conflict")
        self.assertFalse(show(self.store, op2.op_id)["may_have_submitted"])

    def test_corruption_truncation_and_version_drift_remain_present(self):
        for n, broken in enumerate((b"Hello\n", b"hello", b"")):
            op, writer = self.prepare(name="corrupt" + str(n), text_utf8=True, final_lf=True)
            run(self.store, op.op_id, writer, "executor")
            with closing(sqlite3.connect(self.destination)) as c, c:
                c.execute("UPDATE object SET data=?,revision='changed' WHERE operation=?", (broken, op.op_id))
            result = reconcile(self.store, op.op_id, writer.reader())
            self.assertEqual(result["status"], "conflict")
            self.assertEqual(json.loads(result["observation"]["evidence"])["objects"][0]["verification"], "fail")

    def test_store_identity_missing_corrupt_schema_and_lock_replacement(self):
        op, writer = self.prepare()
        wrong = Store(self.store.path, replace(self.store.identity, store_id="other"))
        with self.assertRaises(Blocked):
            run(wrong, op.op_id, writer, "executor")
        with self.assertRaises(Blocked):
            run(Store(self.root / "missing.db", self.store.identity), op.op_id, writer, "executor")
        self.assertFalse((self.root / "missing.db").exists())
        self.store.lock_path.rename(self.root / "old.lock")
        self.store.lock_path.touch(mode=0o600)
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor")
        self.store.lock_path.unlink()
        (self.root / "old.lock").rename(self.store.lock_path)
        with closing(sqlite3.connect(self.store.path)) as c, c:
            c.execute("DROP TRIGGER dispatch_delete")
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor")
        self.assertEqual(self.objects(), [])

    def test_latch_store_failure_and_result_report_failure(self):
        op, writer = self.prepare()
        with patch.object(self.store, "admit", side_effect=sqlite3.OperationalError("full")):
            with self.assertRaises(Blocked):
                run(self.store, op.op_id, writer, "executor")
        self.assertEqual(self.objects(), [])
        with patch.object(self.store, "append", side_effect=sqlite3.OperationalError("full")):
            result = run(self.store, op.op_id, writer, "executor")
        self.assertTrue(result["reporting_gap"])
        self.assertEqual(len(self.objects()), 1)
        self.assertEqual(reconcile(self.store, op.op_id, writer.reader())["status"], "retained_verified")
        self.assertEqual(len(self.objects()), 1)

    def test_contract_c0_c1_and_property_owner_decision_separation(self):
        op, writer = self.prepare(decision_owner="human", decision_property="use")
        decision = dict(candidate=op.input_hash, property="use", contract_ref="contract:C0", contract_hash=digest(b"C0"), owner="human", verdict="accepted", expires=time.time() + 600, provenance="fixture human decision")
        self.admin.decision(op.op_id, **decision)
        self.assertEqual(run(self.store, op.op_id, writer, "executor")["decision"], "pending")
        decision.update(contract_ref=op.contract_ref, contract_hash=op.contract_hash, owner="wrong")
        self.admin.decision(op.op_id, **decision)
        self.assertEqual(show(self.store, op.op_id)["decision"], "pending")
        decision.update(owner="human", property="unrelated")
        self.admin.decision(op.op_id, **decision)
        self.assertEqual(show(self.store, op.op_id)["decision"], "pending")
        decision.update(property="use")
        self.admin.decision(op.op_id, **decision)
        self.assertEqual(show(self.store, op.op_id)["decision"], "accepted")
        decision.update(verdict="rejected")
        self.admin.decision(op.op_id, **decision)
        self.assertEqual(show(self.store, op.op_id)["decision"], "conflict")

    def test_reconcile_reader_only_and_cli_fresh_context(self):
        op, writer = self.prepare()
        reader = writer.reader()
        self.assertFalse(hasattr(reader, "submit"))
        module = importlib.import_module("v2_retain.reconcile")
        self.assertNotIn("run", vars(module))
        with patch.object(LocalWriter, "submit", side_effect=AssertionError("reconcile cannot write")):
            self.assertEqual(reconcile(self.store, op.op_id, reader)["status"], "prepared")
        identity = self.root / "identity.json"
        identity.write_text(self.store.identity.json())
        result = subprocess.run([sys.executable, "-m", "v2_retain", "--store", str(self.store.path), "--identity", str(identity), "run", op.op_id, "--destination", str(self.destination), "--actor", "executor"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "retained_verified")

    def test_resource_format_and_recovery_only(self):
        with self.assertRaises(Blocked):
            self.prepare(b"\xff", text_utf8=True)
        with self.assertRaises(Blocked):
            self.prepare(b"no newline", final_lf=True)
        with self.assertRaises(Blocked):
            self.prepare(b"x" * (MAX_BYTES + 1))
        op, writer = self.prepare()
        recovery = Store(self.store.path, replace(self.store.identity, mode="recovery-only"))
        with self.assertRaises(Blocked):
            run(recovery, op.op_id, writer, "executor")
        self.assertEqual(reconcile(recovery, op.op_id, writer.reader())["status"], "prepared")

    def test_accepted_revocation_serializes_behind_admitted_call(self):
        op, writer = self.prepare()
        entered, release, requested, revoked = (threading.Event() for _ in range(4))
        original = writer.submit
        errors = []
        def submit(*args):
            entered.set()
            if not release.wait(5):
                raise RuntimeError("fixture release missing")
            return original(*args)
        writer.submit = submit
        def invoke():
            try:
                run(self.store, op.op_id, writer, "executor")
            except Exception as exc:
                errors.append(exc)
        def revoke():
            requested.set()
            try:
                self.admin.revoke(op.grant_ref, "human revoke during call")
                revoked.set()
            except Exception as exc:
                errors.append(exc)
        a, b = threading.Thread(target=invoke), threading.Thread(target=revoke)
        a.start()
        self.assertTrue(entered.wait(5))
        b.start()
        try:
            self.assertTrue(requested.wait(5))
            self.assertFalse(revoked.wait(0.05))
            with closing(sqlite3.connect(self.store.path)) as c:
                self.assertEqual(c.execute("SELECT count(*) FROM revocation").fetchone()[0], 0)
        finally:
            release.set()
            a.join(5)
            b.join(5)
        self.assertFalse(a.is_alive() or b.is_alive())
        self.assertEqual(errors, [])
        self.assertTrue(revoked.is_set())
        self.assertEqual(len(self.objects()), 1)

    def test_revocation_accepted_after_preflight_wins_admission(self):
        op, writer = self.prepare()
        reader = writer.reader()
        admin = self.admin
        class RevokeAfterRead:
            def observe(self, op, known=()):
                result = reader.observe(op, known)
                admin.revoke(op.grant_ref, "human revoke after preflight")
                return result
        with patch.object(writer, "reader", return_value=RevokeAfterRead()):
            with self.assertRaises(Blocked):
                run(self.store, op.op_id, writer, "executor")
        self.assertFalse(show(self.store, op.op_id)["may_have_submitted"])
        self.assertEqual(self.objects(), [])

    def test_uncertain_commit_and_final_actor_change_never_submit(self):
        for name in ("commit", "actor"):
            op, writer = self.prepare(name=name)
            original = self.store.admit
            def admit(*args):
                original(*args)
                if name == "commit":
                    raise sqlite3.OperationalError("commit acknowledgement lost")
                writer.actor = "changed"
            with patch.object(self.store, "admit", side_effect=admit):
                if name == "commit":
                    with self.assertRaises(Blocked):
                        run(self.store, op.op_id, writer, "executor")
                else:
                    self.assertEqual(run(self.store, op.op_id, writer, "executor")["status"], "hold")
            self.assertTrue(show(self.store, op.op_id)["may_have_submitted"])
        self.assertEqual(self.objects(), [])

    def test_same_bytes_version_drift_and_changed_read_route_stay_held(self):
        op, writer = self.prepare()
        run(self.store, op.op_id, writer, "executor")
        with closing(sqlite3.connect(self.destination)) as c, c:
            c.execute("UPDATE object SET revision='changed'")
        for _ in range(2):
            self.assertEqual(reconcile(self.store, op.op_id, writer.reader())["status"], "hold")
        other = self.root / "other.db"
        initialize_destination(other)
        result = reconcile(self.store, op.op_id, LocalReader(other, op.target, op.actor))
        self.assertEqual(result["status"], "hold")
        self.assertIn("unavailable", json.loads(result["observation"]["evidence"])["error"])

    def test_actual_database_corruption_fails_closed(self):
        op, writer = self.prepare()
        with open(self.store.path, "r+b") as f:
            f.write(b"not a sqlite database")
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor")
        self.assertEqual(self.objects(), [])

    def test_cli_prepare_and_operator_grant_revoke(self):
        from v2_retain.__main__ import main
        from v2_retain.admin import main as admin_main
        from contextlib import redirect_stdout
        import io
        old, writer = self.prepare(name="seed")
        target = replace(old.target, path="/pilot/cli")
        writer = LocalWriter(self.destination, target, old.actor)
        op = replace(old, op_id="cli", target=target, grant_ref="cli-grant", route_hash=writer.qualification.fingerprint)
        identity, spec, input_file = (self.root / n for n in ("identity.json", "spec.json", "input.bin"))
        identity.write_text(self.store.identity.json())
        spec.write_text(op.json())
        input_file.write_bytes(b"hello\n")
        base = ["--store", str(self.store.path), "--identity", str(identity)]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(base + ["prepare", "--spec", str(spec), "--input", str(input_file), "--owner", "operator"]), 0)
            self.assertEqual(admin_main(base + ["--owner", "operator", "grant", "cli", "--provenance", "explicit synthetic grant"]), 0)
            self.assertEqual(admin_main(base + ["--owner", "operator", "revoke", "cli-grant", "--provenance", "explicit revoke"]), 0)
            self.assertEqual(main(base + ["run", "cli", "--destination", str(self.destination), "--actor", "executor"]), 2)
