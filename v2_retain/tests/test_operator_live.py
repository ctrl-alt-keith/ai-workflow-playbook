import json
from pathlib import Path
import tempfile
import unittest

from v2_retain.model import Blocked, digest
from v2_retain.operator_live import _decision


class OperatorDecisionTests(unittest.TestCase):
    def test_requires_exact_accepted_owner_bound_decision(self):
        data = b"owned record\n"
        record = {"candidate": digest(data), "property": "retain", "contract_ref": "CAK-301/operator", "contract_hash": digest(b"contract"), "owner": "Keith Minnig", "verdict": "accepted", "expires": 2000000000, "provenance": "explicit bounded authorization"}
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "decision.json"
            path.write_text(json.dumps(record))
            self.assertEqual(_decision(path, data, "Keith Minnig"), record)
            record["candidate"] = digest(b"other")
            path.write_text(json.dumps(record))
            with self.assertRaises(Blocked):
                _decision(path, data, "Keith Minnig")

    def test_expired_decision_is_not_accepted(self):
        data = b"owned record\n"
        record = {"candidate": digest(data), "property": "retain", "contract_ref": "CAK-301/operator", "contract_hash": digest(b"contract"), "owner": "Keith Minnig", "verdict": "accepted", "expires": 1, "provenance": "explicit bounded authorization"}
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "decision.json"
            path.write_text(json.dumps(record))
            with self.assertRaises(Blocked):
                _decision(path, data, "Keith Minnig")

