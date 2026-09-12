"""Operator-owned grant/decision interface; executor imports no admin path."""

import math
import time
import uuid

from .model import Blocked, digest


class Admin:
    def __init__(self, store, owner):
        if owner != store.identity.owner:
            raise Blocked("wrong authority owner")
        self.store, self.owner = store, owner

    def grant(self, op_id, provenance):
        if not provenance:
            raise Blocked("human provenance required")
        with self.store.session() as c:
            op, _ = self.store.load(c, op_id)
            c.execute("INSERT INTO grant_record VALUES (?,?,?,?,?)", (op.grant_ref, op_id, digest(op.json().encode()), self.owner, provenance))

    def revoke(self, grant_ref, provenance):
        if not provenance:
            raise Blocked("human provenance required")
        with self.store.session() as c:
            c.execute("INSERT INTO revocation VALUES (?,?,?)", (grant_ref, provenance, time.time()))

    def decision(self, op_id, *, candidate, property, contract_ref, contract_hash, owner, verdict, expires, provenance):
        if verdict not in {"accepted", "rejected", "abandoned"} or not math.isfinite(expires) or not all((candidate, property, contract_ref, contract_hash, owner, provenance)):
            raise Blocked("complete scoped disposition required")
        with self.store.session() as c:
            self.store.load(c, op_id)
            c.execute("INSERT INTO decision VALUES (?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), op_id, candidate, property, contract_ref, contract_hash, owner, verdict, expires, provenance))


def main(argv=None):
    import argparse
    import json
    import os
    from pathlib import Path
    from .store import Store, Identity
    from .local import initialize_destination

    p = argparse.ArgumentParser(description="Operator-only local authority administration")
    p.add_argument("--store", required=True)
    p.add_argument("--identity", required=True)
    p.add_argument("--owner", required=True)
    commands = p.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    for name in ("grant", "revoke"):
        sub = commands.add_parser(name)
        sub.add_argument("reference")
        sub.add_argument("--provenance", required=True)
    d = commands.add_parser("decision")
    d.add_argument("--record", required=True)
    local = commands.add_parser("init-local-destination")
    local.add_argument("path")
    args = p.parse_args(argv)
    try:
        if args.command == "init":
            if Path(args.identity).exists():
                raise Blocked("installation note already exists")
            store = Store.initialize(args.store, args.owner)
            fd = os.open(args.identity, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as f:
                f.write(store.identity.json() + "\n")
                f.flush()
                os.fsync(f.fileno())
        else:
            store = Store(args.store, Identity.parse(Path(args.identity).read_text()))
            admin = Admin(store, args.owner)
            if args.command == "grant":
                admin.grant(args.reference, args.provenance)
            elif args.command == "revoke":
                admin.revoke(args.reference, args.provenance)
            elif args.command == "decision":
                admin.decision(**json.loads(Path(args.record).read_text()))
            else:
                initialize_destination(args.path)
        print(json.dumps({"status": "recorded", "authority_owner": args.owner}))
        return 0
    except (Blocked, OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc) if isinstance(exc, Blocked) else "invalid or unavailable input"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
