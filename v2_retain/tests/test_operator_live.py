import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from v2_retain.model import Blocked, digest
from v2_retain.operator_live import _decision, main


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


    def test_rejects_nonaccepted_and_nan_decisions(self):
        data = b"owned record\n"
        base = {"candidate": digest(data), "property": "retain", "contract_ref": "CAK-301/operator", "contract_hash": digest(b"contract"), "owner": "Keith Minnig", "verdict": "rejected", "expires": 2000000000, "provenance": "explicit bounded authorization"}
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "decision.json"
            path.write_text(json.dumps(base))
            with self.assertRaises(Blocked):
                _decision(path, data, "Keith Minnig")
            base["verdict"], base["expires"] = "accepted", float("nan")
            path.write_text(json.dumps(base))
            with self.assertRaises(Blocked):
                _decision(path, data, "Keith Minnig")

    def test_state_root_rejected_before_identity_network(self):
        args = ["--input", __file__, "--decision", __file__, "--folder", "/cak-301-v2-qual-20260922-operator", "--name", "record.md", "--source-ref", "source", "--owner", "Keith", "--actor", "actor", "--grant-provenance", "grant", "--expected-head", "a" * 40, "--state-root", str(Path.cwd())]
        with patch("v2_retain.operator_live._head") as head:
            self.assertEqual(main(args), 2)
        head.assert_not_called()
