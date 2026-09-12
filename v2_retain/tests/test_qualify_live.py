from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from v2_retain.model import Blocked
from v2_retain.qualify_live import _counted, main


class FakeAdapter:
    def send(self, request, **kwargs):
        return object()


class FakeSession:
    def __init__(self):
        self.adapter = FakeAdapter()

    def get_adapter(self, _):
        return self.adapter


class FakeWriter:
    def __init__(self):
        self._client = type("Client", (), {"_session": FakeSession()})()
        self.config = type("Config", (), {"parent_path": "/folder"})()


class Request:
    def __init__(self, path):
        self.url = "https://content.dropboxapi.com/2/files/upload"
        self.headers = {"Dropbox-API-Arg": json.dumps({"path": path, "mode": {".tag": "add"},
                                                       "autorename": False, "strict_conflict": True})}
        self.body = b"test"


class QualifyLiveTests(unittest.TestCase):
    def test_explicit_mode_requires_resolved_environment_token_before_network(self):
        output = StringIO()
        with patch("v2_retain.qualify_live._head", return_value="a" * 40), \
             patch("v2_retain.qualify_live._identity_client") as client, \
             patch.dict(os.environ, {"DROPBOX_ACCESS_TOKEN": "op://unresolved"}), redirect_stdout(output):
            status = main(["--mode", "execute", "--folder", "/cak-301-v2-qual-20260912-01",
                           "--expected-head", "a" * 40])
        self.assertEqual(status, 2)
        client.assert_not_called()
        self.assertNotIn("op://unresolved", output.getvalue())

    def test_upload_and_unique_destination_caps_are_reserved_before_send(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requests.jsonl"
            path.touch()
            writer = FakeWriter()
            _counted(writer, path)
            adapter = writer._client._session.adapter
            for i in range(8):
                adapter.send(Request("/folder/file" + str(i)))
            with self.assertRaises(Blocked):
                adapter.send(Request("/folder/ninth"))
            for _ in range(4):
                adapter.send(Request("/folder/file0"))
            with self.assertRaises(Blocked):
                adapter.send(Request("/folder/file0"))
            self.assertEqual(len(path.read_text().splitlines()), 12)

    def test_raw_provider_exception_payload_is_not_printed(self):
        output = StringIO()
        with patch("v2_retain.qualify_live._head", return_value="a" * 40), \
             patch("v2_retain.qualify_live._identity_client", side_effect=RuntimeError("secret-sentinel")), \
             patch.dict(os.environ, {"DROPBOX_ACCESS_TOKEN": "secret-sentinel"}), redirect_stdout(output):
            status = main(["--mode", "preflight", "--folder", "/cak-301-v2-qual-20260912-01",
                           "--expected-head", "a" * 40])
        self.assertEqual(status, 2)
        self.assertNotIn("secret-sentinel", output.getvalue())


if __name__ == "__main__":
    unittest.main()
