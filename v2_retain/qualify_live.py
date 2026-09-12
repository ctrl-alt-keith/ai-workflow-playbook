"""One-shot, opt-in App Folder qualification on the operator's Mac.

The token is read only from the child-process environment. This module never
serializes it or includes provider exception text in output or evidence.
"""

import argparse
from datetime import datetime, timezone
import fcntl
from importlib.metadata import version
import json
import multiprocessing
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urlsplit

import dropbox

from .admin import Admin
from .dropbox_adapter import Config, DropboxWriter, ReadOnlySession, NoRefreshDropbox, read_identity, strict_create
from .model import Blocked, Operation, Target, digest, encode
from .operation import run
from .reconcile import reconcile
from .store import Identity, Store

MAX_DESTINATIONS = 8
MAX_UPLOADS = 12
MAX_OBJECT_BYTES = 1024 * 1024
FOLDER_PATTERN = re.compile(r"/cak-301-v2-qual-[a-z0-9-]{8,40}\Z")
LABEL = "op://Private/CAK v2 Dropbox Qualification/access_token"


def _head():
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    head = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise Blocked("exact build head unavailable")
    return head


def _token():
    token = os.environ.get("DROPBOX_ACCESS_TOKEN", "")
    if not token or token.startswith("op://") or token == "synthetic-local-test-token":
        raise Blocked("resolved DROPBOX_ACCESS_TOKEN required at process start")
    return token


def _versions():
    if (version("dropbox"), version("requests"), version("urllib3")) != ("12.2.1", "2.34.2", "2.7.0"):
        raise Blocked("qualification dependency drift")


def _identity_client(token):
    session = ReadOnlySession(live=True)
    return NoRefreshDropbox(oauth2_access_token=token, max_retries_on_error=0,
                            max_retries_on_rate_limit=0, timeout=10, session=session)


def _identity(client, folder):
    account = client.users_get_current_account()
    root = account.root_info
    if not account.account_id or not root or not root.root_namespace_id or not root.home_namespace_id:
        raise Blocked("acting account or namespace identity unavailable")
    # An App Folder token uses its implicit app-root. Dropbox does not provide
    # root metadata, so this checks readable scope without claiming a root ID.
    client.files_list_folder("")
    try:
        existing = client.files_get_metadata(folder)
    except dropbox.exceptions.ApiError as exc:
        if exc.error.is_path() and exc.error.get_path().is_not_found():
            existing = None
        else:
            raise Blocked("qualification folder lookup unavailable") from None
    return {"account_id": account.account_id, "display_name": account.name.display_name,
            "root_namespace_id": root.root_namespace_id,
            "home_namespace_id": root.home_namespace_id,
            "app_root": "implicit-app-folder-root", "folder_path": folder,
            "folder_state": "absent" if existing is None else "present",
            "folder_id": existing.id if isinstance(existing, dropbox.files.FolderMetadata) else ""}


def _append(path, event):
    with open(path, "a", encoding="utf-8") as f:
        f.write(encode(event) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _counted(writer, count_path, *, pause=None):
    adapter = writer._client._session.get_adapter("https://content.dropboxapi.com")
    original = adapter.send

    def send(request, **kwargs):
        if urlsplit(request.url).path == "/2/files/upload":
            args = json.loads(request.headers["Dropbox-API-Arg"])
            path = args["path"]
            body = request.body
            if (not isinstance(body, bytes) or len(body) > MAX_OBJECT_BYTES
                    or args.get("mode") != {".tag": "add"}
                    or args.get("autorename") is not False or args.get("strict_conflict") is not True
                    or not path.startswith(writer.config.parent_path + "/")):
                raise Blocked("qualification upload shape or byte cap mismatch")
            with open(count_path, "a+", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.seek(0)
                prior = [json.loads(line)["path"] for line in f if line.strip()]
                if len(prior) >= MAX_UPLOADS or (path not in prior and len(set(prior)) >= MAX_DESTINATIONS):
                    raise Blocked("qualification upload/destination cap reached")
                f.write(encode({"kind": "upload-request", "path": path,
                                "size": len(body), "sha256": digest(body),
                                "create": "strict-create-no-autorename"}) + "\n")
                f.flush()
                os.fsync(f.fileno())
                fcntl.flock(f, fcntl.LOCK_UN)
        response = original(request, **kwargs)
        if pause is not None and urlsplit(request.url).path == "/2/files/upload":
            pause.send("response-received")
            pause.recv()
        return response

    adapter.send = send


def _count(count_path):
    return sum(1 for line in count_path.read_text().splitlines() if json.loads(line)["kind"] == "upload-request")


def _operation(store, facts, folder, name, data, head, token, count_path):
    if len(data) > MAX_OBJECT_BYTES:
        raise Blocked("qualification object exceeds 1 MiB")
    target = Target(facts["account_id"], facts["home_namespace_id"], facts["folder_id"], folder + "/" + name)
    config = Config(target.account, target.namespace, target.parent, folder,
                    "qualification-executor", LABEL, profile="live-qualification",
                    root_namespace=facts["root_namespace_id"], home_namespace=facts["home_namespace_id"], head=head)
    writer = DropboxWriter(config, target, access_token=token)
    _counted(writer, count_path)
    now = time.time()
    op = Operation("qual-" + name.replace(".", "-"), "qualification-operator", "CAK-301/local-qualification",
                   "CAK-301/retain-exact", digest(b"CAK-301/retain-exact"), "qualification-executor",
                   target, "grant-" + name, now - 5, now + 1200,
                   "retain-for-operator-review", "private-app-folder", digest(data), len(data),
                   writer.qualification.fingerprint)
    store.prepare(op, data, "qualification-operator")
    Admin(store, "qualification-operator").grant(op.op_id, "Keith explicitly launched bounded live qualification")
    return op, writer


def _worker(store_path, identity_path, config, target, op_id, count_path, result_queue, pause=None):
    try:
        token = _token()
        writer = DropboxWriter(config, target, access_token=token)
        _counted(writer, count_path, pause=pause)
        store = Store(store_path, Identity.parse(Path(identity_path).read_text()))
        result_queue.put(run(store, op_id, writer, "qualification-executor")["status"])
        writer.close()
    except BaseException:
        result_queue.put("blocked")


def _execute(facts, folder, token, head, state_root):
    if facts["folder_state"] != "absent":
        raise Blocked("isolated qualification folder already exists")
    print("Read-only preflight:")
    print(encode(facts))
    print("Confirm the account and namespace fields above against your intended Dropbox App Folder app.")
    if input("Type the exact account_id to continue: ").strip() != facts["account_id"]:
        raise Blocked("account confirmation mismatch")
    if input("Type the exact home_namespace_id to continue: ").strip() != facts["home_namespace_id"]:
        raise Blocked("home namespace confirmation mismatch")
    if input("Type the exact root_namespace_id to continue: ").strip() != facts["root_namespace_id"]:
        raise Blocked("root namespace confirmation mismatch")
    if input("Type APP FOLDER to attest this credential's configured access type: ").strip() != "APP FOLDER":
        raise Blocked("App Folder access type not confirmed")
    state_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    state = state_root / folder[1:]
    state.mkdir(mode=0o700)
    events = state / "events.jsonl"
    count_path = state / "requests.jsonl"
    count_path.touch(mode=0o600)
    _append(events, {"kind": "confirmed-preflight", "head": head, "facts": facts, "credential_label": LABEL})
    store_path, identity_path = state / "store.sqlite", state / "installation.json"
    store = Store.initialize(store_path, "qualification-operator")
    with open(identity_path, "x", encoding="utf-8") as f:
        f.write(store.identity.json() + "\n")
        f.flush()
        os.fsync(f.fileno())

    client = _identity_client(token)
    try:
        again = _identity(client, folder)
        if again != facts:
            raise Blocked("identity, root, or folder changed before creation")
    finally:
        client.close()
    from .dropbox_adapter import SingleRequestSession
    creator = NoRefreshDropbox(oauth2_access_token=token, max_retries_on_error=0,
                               max_retries_on_rate_limit=0, timeout=10,
                               session=SingleRequestSession(live=True))
    try:
        created = creator.files_create_folder_v2(folder, autorename=False).metadata
        observed = creator.files_get_metadata(folder)
        if (not isinstance(created, dropbox.files.FolderMetadata) or not isinstance(observed, dropbox.files.FolderMetadata)
                or not created.id or created.id != observed.id or observed.path_lower != folder):
            raise Blocked("created folder identity/containment mismatch")
        facts = dict(facts, folder_state="present", folder_id=observed.id)
        _append(events, {"kind": "folder-verified", "folder_path": folder, "folder_id": observed.id})
    finally:
        creator.close()

    cases = []
    destinations = set()

    def add(name, data):
        if len(destinations) >= MAX_DESTINATIONS or _count(count_path) >= MAX_UPLOADS:
            raise Blocked("qualification budget exhausted")
        op, writer = _operation(store, facts, folder, name, data, head, token, count_path)
        destinations.add(op.target.path)
        return op, writer

    try:
        text_op, text_writer = add("text.txt", b"CAK-301 qualification text\n")
        text_result = run(store, text_op.op_id, text_writer, "qualification-executor")
        if text_result["status"] != "retained_verified":
            raise Blocked("healthy text create/readback did not verify")
        cases.append("text-create-readback")
        _append(events, {"kind": cases[-1], "target": text_op.target.path,
                         "size": text_op.size, "sha256": text_op.input_hash,
                         "status": text_result["status"]})
        binary_op, binary_writer = add("binary.bin", bytes(range(256)) + b"\x00\xff")
        binary_result = run(store, binary_op.op_id, binary_writer, "qualification-executor")
        if binary_result["status"] != "retained_verified":
            raise Blocked("healthy binary create/readback did not verify")
        cases.append("binary-create-readback")
        _append(events, {"kind": cases[-1], "target": binary_op.target.path,
                         "size": binary_op.size, "sha256": binary_op.input_hash,
                         "status": binary_result["status"]})

        for label, payload in (("distinct", b"different content"), ("identical", b"CAK-301 qualification text\n")):
            read_identity(text_writer._client, text_writer.config, text_op)
            before = text_writer._client.files_get_metadata(text_op.target.path)
            try:
                strict_create(text_writer._client, text_op.target.path, payload)
            except dropbox.exceptions.ApiError as exc:
                if not exc.error.is_path() or not exc.error.get_path().reason.is_conflict():
                    raise Blocked("collision response not a typed conflict") from None
            else:
                raise Blocked("collision unexpectedly created a new object")
            after = text_writer._client.files_get_metadata(text_op.target.path)
            if (before.id, before.rev, before.size) != (after.id, after.rev, after.size):
                raise Blocked("collision changed original object")
            observed = text_writer.reader().observe(text_op, ((before.id, before.rev),))
            if (not observed.complete or len(observed.objects) != 1
                    or observed.objects[0].data != b"CAK-301 qualification text\n"):
                raise Blocked("collision readback changed original bytes")
            cases.append(label + "-content-same-target-collision")
            _append(events, {"kind": cases[-1], "target": text_op.target.path,
                             "attempt_size": len(payload), "attempt_sha256": digest(payload),
                             "request": "add/autorename=false/strict_conflict=true",
                             "response": "typed-path-conflict", "original_id": before.id,
                             "original_revision": before.rev, "unchanged": True,
                             "readback_sha256": digest(observed.objects[0].data)})

        equal_op, equal_writer = add("equal.txt", b"CAK-301 qualification text\n")
        equal_result = run(store, equal_op.op_id, equal_writer, "qualification-executor")
        if equal_result["status"] != "retained_verified":
            raise Blocked("equal-content distinct operation failed")
        cases.append("equal-content-distinct-target")
        _append(events, {"kind": cases[-1], "target": equal_op.target.path,
                         "size": equal_op.size, "sha256": equal_op.input_hash,
                         "status": equal_result["status"]})

        race_op, race_writer = add("race.txt", b"one local submission\n")
        race_writer.close()
        ctx = multiprocessing.get_context("spawn")
        results = ctx.Queue()
        workers = [ctx.Process(target=_worker, args=(str(store_path), str(identity_path),
                   race_writer.config, race_op.target, race_op.op_id, count_path, results)) for _ in range(2)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(60)
            if worker.is_alive():
                worker.terminate()
                worker.join()
                raise Blocked("local participant did not finish")
        if sorted([results.get(timeout=2) for _ in workers]) != ["retained_verified", "retained_verified"]:
            raise Blocked("local participant result mismatch")
        if sum(1 for line in count_path.read_text().splitlines() if json.loads(line)["path"] == race_op.target.path) != 1:
            raise Blocked("local admission emitted more than one upload")
        cases.append("two-participants-one-upload")
        _append(events, {"kind": cases[-1], "target": race_op.target.path,
                         "participants": 2, "upload_requests": 1,
                         "statuses": ["retained_verified", "retained_verified"]})

        ack_op, ack_writer = add("ack.txt", b"acknowledgement suppressed\n")
        submit = ack_writer.submit
        def suppress(op, data):
            submit(op, data)
            raise TimeoutError("acknowledgement deliberately suppressed")
        ack_writer.submit = suppress
        ack_result = run(store, ack_op.op_id, ack_writer, "qualification-executor")
        if ack_result["status"] != "hold":
            raise Blocked("acknowledgement loss did not hold")
        ack_reconcile = reconcile(store, ack_op.op_id, ack_writer.reader())
        if ack_reconcile["status"] != "hold":
            raise Blocked("unacknowledged object was incorrectly adopted")
        cases.append("acknowledgement-loss-hold")
        _append(events, {"kind": cases[-1], "target": ack_op.target.path,
                         "submitted_size": ack_op.size, "submitted_sha256": ack_op.input_hash,
                         "result": ack_result["status"], "reconcile": ack_reconcile["status"]})

        crash_op, crash_writer = add("interrupt.txt", b"interrupted before local acknowledgement\n")
        crash_writer.close()
        parent, child = ctx.Pipe()
        crash_results = ctx.Queue()
        worker = ctx.Process(target=_worker, args=(str(store_path), str(identity_path),
                             crash_writer.config, crash_op.target, crash_op.op_id,
                             count_path, crash_results, child))
        worker.start()
        if not parent.poll(60) or parent.recv() != "response-received":
            worker.terminate()
            worker.join()
            raise Blocked("in-flight interruption point unavailable")
        worker.terminate()
        worker.join(10)
        reader_writer = DropboxWriter(crash_writer.config, crash_op.target, access_token=token)
        try:
            crash_reconcile = reconcile(store, crash_op.op_id, reader_writer.reader())
            if crash_reconcile["status"] != "hold":
                raise Blocked("interrupted operation was incorrectly adopted")
        finally:
            reader_writer.close()
        cases.append("post-response-pre-ack-interruption-hold")
        _append(events, {"kind": cases[-1], "target": crash_op.target.path,
                         "signal": "provider-response-received-before-sdk-ack",
                         "child_exit": worker.exitcode, "reconcile": crash_reconcile["status"]})
    finally:
        for writer in (locals().get("text_writer"), locals().get("binary_writer"),
                       locals().get("equal_writer"), locals().get("ack_writer")):
            if writer is not None:
                writer.close()

    if len(destinations) > MAX_DESTINATIONS or _count(count_path) > MAX_UPLOADS:
        raise Blocked("qualification budget violated")
    record = {"profile": "live-qualification", "head": head, "sdk_version": "12.2.1",
              "checked_at": datetime.now(timezone.utc).isoformat(), "actor_account": facts["account_id"],
              "root_namespace": facts["root_namespace_id"], "home_namespace": facts["home_namespace_id"],
              "app_root": facts["app_root"], "parent_id": facts["folder_id"], "parent_path": folder,
              "credential_label": LABEL, "create": "strict-create-no-autorename", "retries": 0,
              "admission": "local-synchronous-call", "ceiling": "bounded-live-qualification-only",
              "invalidation": "head/SDK/config/account/namespace/parent/app-access/credential/readback/retry drift",
              "destinations": sorted(destinations), "upload_requests": _count(count_path),
              "cases": cases, "retention": "created objects retained; no cleanup",
              "limitations": "App Folder root ID and token access type are not returned by these SDK reads; operator attestation binds access type. Post-response interruption does not prove an on-wire kill or remote exactly-once."}
    with open(state / "qualification.json", "x", encoding="utf-8") as f:
        f.write(encode(record) + "\n")
        f.flush()
        os.fsync(f.fileno())
    _append(events, {"kind": "qualification-complete", "cases": cases, "upload_requests": record["upload_requests"]})
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description="Opt-in, one-shot CAK-301 App Folder qualification")
    parser.add_argument("--mode", required=True, choices=("preflight", "execute"))
    parser.add_argument("--folder", required=True, help="one fresh /cak-301-v2-qual-* folder inside the app's implicit root")
    parser.add_argument("--expected-head", required=True)
    args = parser.parse_args(argv)
    try:
        if not FOLDER_PATTERN.fullmatch(args.folder) or not re.fullmatch(r"[0-9a-f]{40}", args.expected_head):
            raise Blocked("invalid isolated folder or expected head")
        head = _head()
        if head != args.expected_head:
            raise Blocked("checkout head differs from reviewed qualification head")
        _versions()
        token = _token()
        client = _identity_client(token)
        try:
            facts = _identity(client, args.folder)
        finally:
            client.close()
        if args.mode == "preflight":
            print(encode({"status": "read-only-preflight", "head": head, "sdk_version": dropbox.__version__,
                          "credential_label": LABEL, "facts": facts,
                          "limitation": "App Folder root ID and token access type are not exposed by these SDK reads"}))
            return 0
        record = _execute(facts, args.folder, token, head, Path(".v2-live-qualification").absolute())
        print(encode({"status": "qualification-complete", "record": record}))
        return 0
    except BaseException as exc:
        # No raw provider, SDK, HTTP, or child exception payload reaches stdout.
        reason = str(exc) if isinstance(exc, Blocked) else "qualification stopped; inspect non-secret local events"
        print(encode({"status": "blocked", "reason": reason}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
