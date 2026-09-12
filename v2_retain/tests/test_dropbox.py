from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import requests
import dropbox
from requests.adapters import HTTPAdapter

from v2_retain.dropbox_adapter import BoundedHTTPAdapter, Config, DropboxWriter, strict_create
from v2_retain.model import Blocked, digest
from v2_retain.operation import run
from v2_retain.qualify_live import _counted
from v2_retain.reconcile import reconcile
import test_operation as local_tests

ACCOUNT = "dbid:" + "a" * 35


class FixtureServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self):
        super().__init__(("127.0.0.1", 0), Handler)
        self.requests = []
        self.objects = {}
        self.upload_status = 200
        self.download_truncate = False
        self.account = ACCOUNT
        self.parent = "id:parent"
        self.target_as_folder = False
        self.target_lookup_error = False
        self.download_versions = {}
        self.download_path_override = None

    @property
    def origin(self):
        return "http://127.0.0.1:" + str(self.server_port)


def metadata(path, data):
    return {".tag": "file", "name": path.rsplit("/", 1)[-1], "id": "id:fixture-file", "rev": "0123456789abcdef",
            "path_lower": path, "path_display": path, "size": len(data), "is_downloadable": True,
            "client_modified": "2026-09-12T00:00:00Z", "server_modified": "2026-09-12T00:00:00Z"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, status, obj, headers=None):
        body = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        self.server.requests.append((self.path, dict(self.headers), body))
        if self.path.endswith("users/get_current_account"):
            return self.respond(200, {"account_id": self.server.account, "name": {"given_name": "Test", "surname": "User", "familiar_name": "Test", "display_name": "Test User", "abbreviated_name": "TU"}, "email": "fixture@example.invalid", "email_verified": True, "disabled": False, "locale": "en", "referral_link": "https://example.invalid", "is_paired": False, "account_type": {".tag": "basic"}, "root_info": {".tag": "user", "root_namespace_id": "123", "home_namespace_id": "123"}})
        if self.path.endswith("files/list_folder"):
            return self.respond(200, {"entries": [], "cursor": "fixture-cursor", "has_more": False})
        if self.path.endswith("files/get_metadata"):
            path = json.loads(body)["path"]
            if path == "/pilot":
                return self.respond(200, {".tag": "folder", "name": "pilot", "id": self.server.parent, "path_lower": "/pilot", "path_display": "/pilot"})
            if path in self.server.objects:
                if self.server.target_lookup_error:
                    return self.respond(409, {"error_summary": "path/not_file/", "error": {".tag": "path", "path": {".tag": "not_file"}}})
                if self.server.target_as_folder:
                    return self.respond(200, {".tag": "folder", "name": path.rsplit("/", 1)[-1], "id": "id:folder", "path_lower": path, "path_display": path})
                return self.respond(200, metadata(path, self.server.objects[path]))
            return self.respond(409, {"error_summary": "path/not_found/", "error": {".tag": "path", "path": {".tag": "not_found"}}})
        if self.path.endswith("files/upload"):
            status = self.server.upload_status
            if status == "timeout":
                time.sleep(0.15)
                return self.respond(500, {})
            if status in (301, 302, 307, 308):
                return self.respond(status, {}, {"Location": self.server.origin + "/replayed"})
            if status == 401:
                return self.respond(401, {"error": {".tag": "expired_access_token"}})
            if status == 429:
                return self.respond(429, {"error": {".tag": "too_many_requests"}, "error_summary": "too_many_requests/"}, {"Retry-After": "0"})
            if status != 200:
                return self.respond(status, {})
            path = json.loads(self.headers["Dropbox-API-Arg"])["path"]
            if path in self.server.objects:
                return self.respond(409, {"error_summary": "path/conflict/file/", "error": {".tag": "path", "reason": {".tag": "conflict", "conflict": {".tag": "file"}}, "upload_session_id": "fixture"}})
            self.server.objects[path] = body
            return self.respond(200, metadata(path, body))
        if self.path.endswith("files/download"):
            self.server.download_argument = json.loads(self.headers["Dropbox-API-Arg"])
            path, data = next(iter(self.server.objects.items()))
            rev = self.server.download_argument["path"].removeprefix("rev:")
            if rev in self.server.download_versions:
                data = self.server.download_versions[rev]
            meta = metadata(self.server.download_path_override or path, data)
            if rev in self.server.download_versions:
                meta["rev"] = rev
            return self.respond(200, data[:-1] if self.server.download_truncate else data, {"dropbox-api-result": json.dumps(meta)})
        return self.respond(400, {})


class DropboxTests(unittest.TestCase):
    prepare_local = local_tests.OperationTests.prepare

    def setUp(self):
        local_tests.OperationTests.setUp(self)
        self.server = FixtureServer()
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        def close():
            self.server.shutdown()
            self.thread.join()
            self.server.server_close()
        self.addCleanup(close)

    def prepare(self, name="sdk", timeout=1):
        original, _ = self.prepare_local(name="seed" + name)
        target = replace(original.target, account=ACCOUNT, namespace="123", parent="id:parent", path="/pilot/" + name)
        config = Config(target.account, target.namespace, target.parent, "/pilot", "executor", "synthetic-fixture", timeout)
        writer = DropboxWriter(config, target, fixture_origin=self.server.origin)
        self.addCleanup(writer.close)
        op = replace(original, op_id=name, grant_ref="grant:" + name, target=target, route_hash=writer.qualification.fingerprint)
        self.store.prepare(op, b"hello\n", "operator")
        self.admin.grant(name, "synthetic local transport authorization")
        return op, writer

    def test_effective_sdk_strict_create_namespace_and_exact_revision_readback(self):
        op, writer = self.prepare()
        result = run(self.store, op.op_id, writer, "executor")
        self.assertEqual(result["status"], "retained_verified", result)
        requests = self.server.requests
        upload = [r for r in requests if r[0].endswith("files/upload")]
        self.assertEqual(len(upload), 1)
        arg = json.loads(upload[0][1]["Dropbox-API-Arg"])
        self.assertEqual(arg["mode"], {".tag": "add"})
        self.assertIs(arg["autorename"], False)
        self.assertIs(arg["strict_conflict"], True)
        self.assertEqual(upload[0][2], b"hello\n")
        self.assertEqual(json.loads(upload[0][1]["Dropbox-API-Path-Root"]), {".tag": "namespace_id", "namespace_id": "123"})
        self.assertEqual(self.server.download_argument["path"], "rev:0123456789abcdef")
        self.assertFalse(hasattr(writer.reader(), "submit"))
        with self.assertRaises(Blocked):
            writer._read_client.files_upload(b"forbidden", op.target.path)
        reconcile(self.store, op.op_id, writer.reader())
        self.assertEqual(len([r for r in requests if r[0].endswith("files/upload")]), 1)

    def test_sdk_and_http_layers_never_replay_error_redirect_or_expired_token(self):
        for status in (500, 429, 401, 301, 302, 307, 308, "timeout"):
            with self.subTest(status=status):
                op, writer = self.prepare(name="error" + str(status), timeout=0.03)
                self.server.upload_status = status
                start = len(self.server.requests)
                result = run(self.store, op.op_id, writer, "executor")
                emitted = self.server.requests[start:]
                self.assertEqual(result["status"], "hold", result)
                self.assertEqual(len([r for r in emitted if r[0].endswith("files/upload")]), 1)
                self.assertFalse(any("replayed" in r[0] or "oauth" in r[0] for r in emitted))
                with patch.object(writer, "submit", side_effect=AssertionError("no second submission")):
                    self.assertEqual(run(self.store, op.op_id, writer, "executor")["status"], "hold")

    def test_sdk_config_drift_identity_and_unqualified_live_route(self):
        op, writer = self.prepare()
        writer._client._max_retries_on_error = 1
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor")
        writer._client._max_retries_on_error = 0
        transport = writer._client._session.get_adapter("https://content.dropboxapi.com")
        transport.fixture_origin = "http://127.0.0.1:1"
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor")
        transport.fixture_origin = self.server.origin
        self.server.account = "dbid:" + "b" * 35
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor")
        self.server.account = ACCOUNT
        self.server.parent = "id:wrong"
        with self.assertRaises(Blocked):
            run(self.store, op.op_id, writer, "executor")
        live = DropboxWriter(writer.config, op.target)
        self.addCleanup(live.close)
        with self.assertRaises(Blocked):
            live.submit(op, b"hello\n")
        with self.assertRaises(Blocked):
            live._client.files_upload(b"x", op.target.path)
        self.assertFalse(any(r[0].endswith("files/upload") for r in self.server.requests))

    def test_effective_download_truncation_and_correlation_hold(self):
        op, writer = self.prepare()
        self.server.download_truncate = True
        self.assertEqual(run(self.store, op.op_id, writer, "executor")["status"], "conflict")
        # Matching content without an acknowledged identity is not causal proof.
        observation = writer.reader().observe(op, ())
        self.assertFalse(observation.objects[0].correlated)

    def test_local_collision_fixture_does_not_qualify_provider_collision(self):
        op, writer = self.prepare()
        writer.submit(op, b"hello\n")
        for data in (b"hello\n", b"different"):
            with self.assertRaises(dropbox.exceptions.ApiError):
                strict_create(writer._client, op.target.path, data)
        self.assertEqual(self.server.objects[op.target.path], b"hello\n")
        self.assertEqual(writer.qualification.collision_response_ref, "unqualified")

    def test_reader_mismatch_unavailable_folder_and_multiple_versions(self):
        op, writer = self.prepare()
        writer.submit(op, b"hello\n")
        reader = writer.reader()
        self.server.download_path_override = "/pilot/elsewhere"
        self.assertEqual(reader.observe(op).error, "returned identity/containment mismatch")
        self.server.download_path_override = None
        self.server.target_lookup_error = True
        self.assertEqual(reader.observe(op).error, "metadata unavailable")
        self.server.target_lookup_error = False
        self.server.target_as_folder = True
        self.assertEqual(reader.observe(op).error, "target is not a file")
        self.server.target_as_folder = False
        self.server.download_versions["abcdef0123456789"] = b"older bytes"
        observed = reader.observe(op, (("id:fixture-file", "abcdef0123456789"),))
        self.assertEqual(len(observed.objects), 2)
        self.assertEqual([o.revision for o in observed.objects], ["abcdef0123456789", "0123456789abcdef"])
        self.assertTrue(observed.complete)

    def test_explicit_live_profile_uses_resolved_token_and_implicit_app_root_on_loopback(self):
        original, _ = self.prepare_local(name="seedliveprofile")
        target = replace(original.target, account=ACCOUNT, namespace="123", parent="id:parent", path="/pilot/liveprofile")
        config = Config(target.account, target.namespace, target.parent, "/pilot", "executor",
                        "symbolic-op-reference", profile="live-qualification", root_namespace="123",
                        home_namespace="123", head="a" * 40)
        with self.assertRaises(Blocked):
            DropboxWriter(config, target)
        with self.assertRaises(Blocked):
            DropboxWriter(config, target, access_token="op://unresolved")
        with self.assertRaises(Blocked):
            DropboxWriter(replace(config, profile="local"), target, access_token="ambient-token")

        def fixture_send(adapter, request, **kwargs):
            self.assertEqual(request.url.split(":", 1)[0], "https")
            self.assertIn(request.url.split("/", 3)[2], {"api.dropboxapi.com", "content.dropboxapi.com"})
            request.url = self.server.origin + "/" + request.url.split("/", 3)[3]
            return HTTPAdapter.send(adapter, request, **kwargs)

        with patch.dict("os.environ", {"DROPBOX_ACCESS_TOKEN": "resolved-fixture-token"}), \
             patch.object(BoundedHTTPAdapter, "send", fixture_send):
            writer = DropboxWriter(config, target, access_token="resolved-fixture-token")
            self.addCleanup(writer.close)
            counter_dir = tempfile.TemporaryDirectory()
            self.addCleanup(counter_dir.cleanup)
            count_path = Path(counter_dir.name) / "requests.jsonl"
            count_path.touch()
            _counted(writer, count_path)
            live_op = replace(original, op_id="liveprofile-op", grant_ref="grant:liveprofile-op",
                              target=target, route_hash=writer.qualification.fingerprint)
            self.store.prepare(live_op, b"hello\n", "operator")
            self.admin.grant(live_op.op_id, "explicit fixture-only live profile test")
            result = run(self.store, live_op.op_id, writer, "executor")
            self.assertEqual(result["status"], "retained_verified")
            upload = [r for r in self.server.requests if r[0].endswith("files/upload")]
            self.assertEqual(len(upload), 1)
            self.assertEqual(len(count_path.read_text().splitlines()), 1)
            self.assertNotIn("Dropbox-API-Path-Root", upload[0][1])
            self.assertTrue(any(r[0].endswith("files/list_folder") for r in self.server.requests))
            self.assertEqual(result["claim_ceiling"], "bounded-live-qualification-only")

    def test_unacknowledged_matching_bytes_never_become_causal_evidence(self):
        op, writer = self.prepare()
        submit = writer.submit
        def lose_ack(*args):
            submit(*args)
            raise TimeoutError("lost acknowledgement")
        with patch.object(writer, "submit", side_effect=lose_ack):
            self.assertEqual(run(self.store, op.op_id, writer, "executor")["status"], "hold")
        for _ in range(3):
            result = reconcile(self.store, op.op_id, writer.reader())
            self.assertEqual(result["status"], "hold")
            evidence = json.loads(result["observation"]["evidence"])
            self.assertEqual(evidence["objects"][0]["verification"], "pass")
            self.assertFalse(evidence["objects"][0]["correlated"])
        self.assertEqual(len([r for r in self.server.requests if r[0].endswith("files/upload")]), 1)
