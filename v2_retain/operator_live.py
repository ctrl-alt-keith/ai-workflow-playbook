"""One explicit, operator-owned live retention; never a default CLI path."""
import argparse
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import dropbox

from .admin import Admin
from .dropbox_adapter import Config, DropboxWriter, NoRefreshDropbox, SingleRequestSession
from .model import Blocked, Operation, Target, digest, encode
from .operation import run
from .qualify_live import FOLDER_PATTERN, LABEL, _head, _identity, _identity_client, _token, _versions
from .store import Store


def _write(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def _append(path, event):
    with open(path, "a", encoding="utf-8") as f:
        f.write(encode(event) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _decision(path, data, owner):
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    required = ("candidate", "property", "contract_ref", "contract_hash", "owner", "verdict", "expires", "provenance")
    if (set(record) != set(required) or record["candidate"] != digest(data)
            or record["owner"] != owner or record["verdict"] != "accepted"
            or not isinstance(record["expires"], (int, float)) or not math.isfinite(record["expires"])
            or record["expires"] <= time.time()
            or not all(isinstance(record[k], str) and record[k] for k in required if k not in {"expires"})):
        raise Blocked("exact accepted decision record required")
    return record


def main(argv=None):
    p = argparse.ArgumentParser(description="Explicit one-shot CAK-301 operator retention")
    p.add_argument("--input", required=True)
    p.add_argument("--decision", required=True)
    p.add_argument("--folder", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--source-ref", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--actor", required=True)
    p.add_argument("--grant-provenance", required=True)
    p.add_argument("--expected-head", required=True)
    p.add_argument("--state-root", required=True)
    args = p.parse_args(argv)
    state = events = None
    try:
        if not FOLDER_PATTERN.fullmatch(args.folder) or not args.name.endswith(".md") or "/" in args.name:
            raise Blocked("isolated folder and markdown name required")
        head = _head()
        if head != args.expected_head:
            raise Blocked("checkout head differs from reviewed operator command head")
        _versions()
        data = Path(args.input).read_bytes()
        if not data or len(data) > 16 * 1024 * 1024:
            raise Blocked("bounded nonempty input required")
        decision = _decision(args.decision, data, args.owner)
        Target("preflight-account", "0", "preflight-parent", args.folder + "/" + args.name).validate()
        token = _token()
        client = _identity_client(token)
        try:
            facts = _identity(client, args.folder)
        finally:
            client.close()
        if facts["folder_state"] != "absent":
            raise Blocked("isolated operator folder already exists")
        print(encode({"status": "read-only-preflight", "facts": facts, "input_sha256": digest(data),
                      "decision": {k: decision[k] for k in ("candidate", "property", "contract_ref", "owner", "verdict")}}))
        if input("Type exact account_id: ").strip() != facts["account_id"]:
            raise Blocked("account confirmation mismatch")
        if input("Type exact home_namespace_id: ").strip() != facts["home_namespace_id"]:
            raise Blocked("home namespace confirmation mismatch")
        if input("Type exact root_namespace_id: ").strip() != facts["root_namespace_id"]:
            raise Blocked("root namespace confirmation mismatch")
        if input("Type APP FOLDER: ").strip() != "APP FOLDER":
            raise Blocked("App Folder access type not confirmed")
        Config(facts["account_id"], facts["home_namespace_id"], "preflight-parent", args.folder, args.actor, LABEL, profile="live-qualification", root_namespace=facts["root_namespace_id"], home_namespace=facts["home_namespace_id"], head=head).validate()
        state_root = Path(args.state_root)
        if not state_root.is_absolute() or Path.cwd() in (state_root, *state_root.parents):
            raise Blocked("operator state root must be absolute and outside the worktree")
        state_root = state_root / ".v2-operator-retention"
        state_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(state_root, 0o700)
        state = state_root / args.folder[1:]
        state.mkdir(mode=0o700)
        events = state / "events.jsonl"
        _append(events, {"kind": "confirmed-preflight", "head": head, "facts": facts})
        store = Store.initialize(state / "store.sqlite", args.owner)
        _write(state / "installation.json", store.identity.json() + "\n")
        client = _identity_client(token)
        try:
            if _identity(client, args.folder) != facts:
                raise Blocked("identity, root, or folder changed before creation")
        finally:
            client.close()
        creator = NoRefreshDropbox(oauth2_access_token=token, max_retries_on_error=0, max_retries_on_rate_limit=0,
                                   timeout=10, session=SingleRequestSession(live=True))
        try:
            created = creator.files_create_folder_v2(args.folder, autorename=False).metadata
            observed = creator.files_get_metadata(args.folder)
            if not isinstance(created, dropbox.files.FolderMetadata) or not isinstance(observed, dropbox.files.FolderMetadata) or created.id != observed.id or observed.path_lower != args.folder:
                raise Blocked("created folder identity mismatch")
            _append(events, {"kind": "folder-verified", "folder_path": args.folder, "folder_id": observed.id})
        finally:
            creator.close()
        target = Target(facts["account_id"], facts["home_namespace_id"], observed.id, args.folder + "/" + args.name)
        config = Config(target.account, target.namespace, target.parent, args.folder, args.actor, LABEL,
                        profile="live-qualification", root_namespace=facts["root_namespace_id"], home_namespace=facts["home_namespace_id"], head=head)
        writer = DropboxWriter(config, target, access_token=token)
        try:
            now = datetime.now(timezone.utc).timestamp()
            op = Operation("operator-" + args.name[:-3], args.owner, args.source_ref, decision["contract_ref"], decision["contract_hash"], args.actor, target,
                           "grant:" + args.name, now - 1, now + 1200, "retain:operator-review", "visibility:private-app-folder", digest(data), len(data), writer.qualification.fingerprint,
                           decision_owner=decision["owner"], decision_property=decision["property"])
            store.prepare(op, data, args.owner)
            admin = Admin(store, args.owner)
            admin.grant(op.op_id, args.grant_provenance)
            admin.decision(op.op_id, **decision)
            result = run(store, op.op_id, writer, args.actor, require_accepted_decision=True)
        finally:
            writer.close()
        record = {"status": result["status"], "head": head, "folder": args.folder, "folder_id": observed.id,
                  "target": target.path, "input_sha256": digest(data), "decision": decision, "result": result,
                  "checked_at": datetime.now(timezone.utc).isoformat(), "ceiling": "one bounded operator retention only"}
        _append(events, {"kind": "operation-result", "status": result["status"], "may_have_submitted": result.get("may_have_submitted", False), "reporting_gap": result.get("reporting_gap", "")})
        _write(state / "receipt.json", encode(record) + "\n")
        print(encode(record))
        return 0 if result["status"] == "retained_verified" and result["decision"] == "accepted" else 2
    except BaseException:
        if events is not None:
            try:
                recovery = {"kind": "blocked", "reason": "operator retention stopped; inspect non-secret durable state"}
                if "store" in locals() and "op" in locals():
                    with store.session() as c:
                        recovery["result"] = __import__("v2_retain.reconcile", fromlist=["project"]).project(store, c, op.op_id)
                _append(events, recovery)
            except BaseException:
                pass
        print(encode({"status": "blocked", "reason": "operator retention stopped; inspect non-secret durable state"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
