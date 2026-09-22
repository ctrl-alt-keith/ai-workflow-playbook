"""One explicit, operator-owned live retention; never a default CLI path."""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import dropbox

from .admin import Admin
from .dropbox_adapter import Config, DropboxWriter, NoRefreshDropbox, SingleRequestSession
from .model import Blocked, Operation, Target, digest, encode
from .operation import run
from .qualify_live import FOLDER_PATTERN, LABEL, _head, _identity, _identity_client, _token, _versions
from .store import Store


def _decision(path, data, owner):
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    required = ("candidate", "property", "contract_ref", "contract_hash", "owner", "verdict", "expires", "provenance")
    if (set(record) != set(required) or record["candidate"] != digest(data)
            or record["owner"] != owner or record["verdict"] != "accepted"
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
    args = p.parse_args(argv)
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
        state = Path(".v2-operator-retention").absolute() / args.folder[1:]
        state.mkdir(mode=0o700, parents=True)
        store = Store.initialize(state / "store.sqlite", args.owner)
        (state / "installation.json").write_text(store.identity.json() + "\n", encoding="utf-8")
        creator = NoRefreshDropbox(oauth2_access_token=token, max_retries_on_error=0, max_retries_on_rate_limit=0,
                                   timeout=10, session=SingleRequestSession(live=True))
        try:
            created = creator.files_create_folder_v2(args.folder, autorename=False).metadata
            observed = creator.files_get_metadata(args.folder)
            if not isinstance(created, dropbox.files.FolderMetadata) or not isinstance(observed, dropbox.files.FolderMetadata) or created.id != observed.id or observed.path_lower != args.folder:
                raise Blocked("created folder identity mismatch")
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
            result = run(store, op.op_id, writer, args.actor)
        finally:
            writer.close()
        if result["status"] != "retained_verified" or result["decision"] != "accepted":
            raise Blocked("operator retention did not verify exact accepted decision")
        record = {"status": "retained_verified", "head": head, "folder": args.folder, "folder_id": observed.id,
                  "target": target.path, "input_sha256": digest(data), "decision": decision, "result": result,
                  "checked_at": datetime.now(timezone.utc).isoformat(), "ceiling": "one bounded operator retention only"}
        (state / "receipt.json").write_text(encode(record) + "\n", encoding="utf-8")
        print(encode(record))
        return 0
    except (Blocked, OSError, ValueError, TypeError, json.JSONDecodeError):
        print(encode({"status": "blocked", "reason": "operator retention stopped; inspect non-secret durable state"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
