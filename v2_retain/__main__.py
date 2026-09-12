"""Opt-in local operation commands. Authority administration is separate."""

import argparse
import json
from pathlib import Path

from .local import LocalReader, LocalWriter
from .model import Blocked, MAX_BYTES, Operation
from .operation import run
from .reconcile import reconcile, show
from .store import Identity, Store


def main(argv=None):
    parser = argparse.ArgumentParser(description="Experimental exact retention; local synthetic inputs only")
    parser.add_argument("--store", required=True)
    parser.add_argument("--identity", required=True, help="operator-owned installation note")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--spec", required=True)
    prepare.add_argument("--input", required=True)
    prepare.add_argument("--owner", required=True)
    for name in ("run", "reconcile", "show"):
        p = sub.add_parser(name)
        p.add_argument("operation")
        if name != "show":
            p.add_argument("--destination", required=True, help="owned local fixture database")
            p.add_argument("--actor", required=True)
    args = parser.parse_args(argv)
    try:
        store = Store(args.store, Identity.parse(Path(args.identity).read_text()))
        if args.command == "prepare":
            op = Operation.parse(Path(args.spec).read_text())
            with open(args.input, "rb") as f:
                data = f.read(MAX_BYTES + 1)
            store.prepare(op, data, args.owner)
            result = show(store, op.op_id)
        elif args.command == "show":
            result = show(store, args.operation)
        else:
            with store.session() as c:
                op, _ = store.load(c, args.operation)
            if args.command == "reconcile":
                # Construct only a reader, never a writer, for this command.
                result = reconcile(store, op.op_id, LocalReader(args.destination, op.target, args.actor))
            else:
                result = run(store, op.op_id, LocalWriter(args.destination, op.target, args.actor), args.actor)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (Blocked, OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc) if isinstance(exc, Blocked) else "invalid or unavailable input"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
