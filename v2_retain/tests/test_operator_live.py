from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from v2_retain.model import Blocked, digest
import v2_retain.operator_live as operator_live
from v2_retain.operator_live import _decision, main


class OperatorDecisionTests(unittest.TestCase):

    def test_identity_uses_valid_access_token_without_renewal(self):
        facts = {"account_id": "account", "home_namespace_id": "1", "root_namespace_id": "1", "folder_state": "absent"}
        client = MagicMock()
        with patch.object(operator_live, "_identity_client", return_value=client), \
             patch.object(operator_live, "_identity", return_value=facts), \
             patch.object(operator_live, "renew_pkce_access_token") as renew:
            token, observed, renewed = operator_live._identity_with_renewal("access", "/cak-301-v2-qual-20260923-operator")
        self.assertEqual((token, observed, renewed), ("access", facts, False))
        renew.assert_not_called()

    def test_identity_renews_only_before_content_admission_and_reobserves(self):
        first = MagicMock()
        second = MagicMock()
        facts = {"account_id": "account", "home_namespace_id": "1", "root_namespace_id": "1", "folder_state": "absent"}
        with patch.object(operator_live, "_identity_client", side_effect=[first, second]), \
             patch.object(operator_live, "_identity", side_effect=[Blocked("implicit credential refresh disabled"), facts]), \
             patch.object(operator_live, "renew_pkce_access_token", return_value="renewed") as renew:
            with patch.dict("os.environ", {"DROPBOX_REFRESH_TOKEN": "refresh", "DROPBOX_CLIENT_ID": "client"}, clear=False):
                token, observed, renewed = operator_live._identity_with_renewal("expired", "/cak-301-v2-qual-20260923-operator")
        self.assertEqual((token, observed, renewed), ("renewed", facts, True))
        renew.assert_called_once_with("expired", "refresh", "client")
        first.close.assert_called_once()
        second.close.assert_called_once()
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

    def test_post_state_failure_redacts_and_records_block_before_recovery(self):
        class FolderMetadata:
            def __init__(self, folder_id, path_lower):
                self.id = folder_id
                self.path_lower = path_lower

        class Store:
            identity = SimpleNamespace(json=lambda: "{}")

            def prepare(self, *args):
                pass

            def session(self):
                return MagicMock()

        secret = "unexpected-secret-detail"
        head = "a" * 40
        facts = {"account_id": "account", "home_namespace_id": "1", "root_namespace_id": "1", "folder_state": "absent"}
        folder = FolderMetadata("folder-id", "/cak-301-v2-qual-20260922-operator")
        creator = MagicMock()
        creator.files_create_folder_v2.return_value = SimpleNamespace(metadata=folder)
        creator.files_get_metadata.return_value = folder
        writer = MagicMock()
        writer.qualification.fingerprint = "b" * 64
        store = Store()

        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            source = root / "record.md"
            source.write_text("record\n", encoding="utf-8")
            decision = root / "decision.json"
            decision.write_text(json.dumps({"candidate": digest(source.read_bytes()), "property": "retain", "contract_ref": "CAK-301/operator", "contract_hash": "c" * 64, "owner": "Keith", "verdict": "accepted", "expires": 2000000000, "provenance": "explicit authorization"}), encoding="utf-8")
            args = ["--input", str(source), "--decision", str(decision), "--folder", folder.path_lower,
                    "--name", "record.md", "--source-ref", "source", "--owner", "Keith", "--actor", "actor",
                    "--grant-provenance", "grant", "--expected-head", head, "--state-root", str(root / "state")]
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch.object(operator_live, "_head", return_value=head), \
                 patch.object(operator_live, "_versions"), \
                 patch.object(operator_live, "_token", return_value="token"), \
                 patch.object(operator_live, "_identity_client", return_value=MagicMock()), \
                 patch.object(operator_live, "_identity", return_value=facts), \
                 patch.object(operator_live, "Config"), \
                 patch.object(operator_live, "NoRefreshDropbox", return_value=creator), \
                 patch.object(operator_live, "DropboxWriter", return_value=writer), \
                 patch.object(operator_live, "Store") as stores, \
                 patch.object(operator_live, "Admin"), \
                 patch.object(operator_live, "run", side_effect=RuntimeError(secret)) as run, \
                 patch.object(operator_live, "project", return_value={"status": "hold"}), \
                 patch.object(operator_live.dropbox.files, "FolderMetadata", FolderMetadata), \
                 patch("builtins.input", side_effect=[facts["account_id"], facts["home_namespace_id"], facts["root_namespace_id"], "APP FOLDER"]), \
                 redirect_stdout(stdout), redirect_stderr(stderr):
                stores.initialize.return_value = store
                self.assertEqual(main(args), 2)
                run.assert_called_once()

            events = (root / "state" / ".v2-operator-retention" / folder.path_lower[1:] / "events.jsonl").read_text(encoding="utf-8")
            records = [json.loads(line) for line in events.splitlines()]
            kinds = [record["kind"] for record in records]
            self.assertLess(kinds.index("blocked"), kinds.index("recovery-projection"))
            self.assertNotIn(secret, events)
            self.assertNotIn(secret, stdout.getvalue())
            self.assertNotIn(secret, stderr.getvalue())
