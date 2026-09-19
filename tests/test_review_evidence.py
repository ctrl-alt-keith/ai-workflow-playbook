"""Deterministic local evidence boundaries, using no live provider access."""

from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
from types import MappingProxyType
import unittest


SPEC = importlib.util.spec_from_file_location(
    "review_evidence", Path(__file__).resolve().parents[1] / "scripts/review_evidence.py")
evidence = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evidence)


class EvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name).resolve()
        self.bundle = self.parent / "bundle"
        self.content = b"Issue-owned selected evidence\n"
        self.source = {
            "id": "design-v1.txt", "provider": "dropbox", "namespace": "ns:123",
            "object_id": "id:synthetic-object", "revision": "revision-1",
            "byte_length": len(self.content),
            "sha256": hashlib.sha256(self.content).hexdigest(),
            "content_path": "evidence/design-v1.txt",
        }
        self.manifest = {
            "schema": evidence.BUNDLE_SCHEMA,
            "reviewed_candidate": {
                "kind": "repository_commit", "repository": "owner/repository", "commit": "a" * 40,
            },
            "applicability": {"status": "applicable", "basis": "Selected by the controller"},
            "sources": [self.source],
        }
        self.bytes = {self.source["id"]: self.content}

    def stage(self):
        return evidence.stage_bundle(self.bundle, self.manifest, self.bytes)

    def rewrite(self, path, content):
        path.chmod(0o600)
        path.write_bytes(content)
        path.chmod(0o400)

    def test_selected_bytes_round_trip_and_private_read_only_modes(self):
        self.bundle.mkdir(mode=0o700)
        result = self.stage()
        self.assertEqual(result, self.manifest)
        self.assertEqual(evidence.verify_bundle(self.bundle), self.manifest)
        for path in [self.bundle, self.bundle / "evidence"]:
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o700)
        for path in [self.bundle / "manifest.json", self.bundle / self.source["content_path"]]:
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o400)
        self.manifest["applicability"]["basis"] = "Caller changed its input"
        self.assertNotEqual(result, self.manifest)
        with self.assertRaises(evidence.EvidenceError):
            self.stage()

    def test_read_only_mapping_inputs_and_immutable_artifact_size(self):
        self.manifest["reviewed_candidate"] = MappingProxyType(self.manifest["reviewed_candidate"])
        self.assertEqual(evidence.stage_bundle(self.bundle, MappingProxyType(self.manifest),
                                              MappingProxyType(self.bytes)), self.manifest)
        artifact = {key: value for key, value in self.source.items()
                    if key not in ("id", "content_path")}
        artifact.update(kind="immutable_artifact", byte_length=0)
        self.manifest["reviewed_candidate"] = artifact
        with self.assertRaises(evidence.EvidenceError):
            evidence.stage_bundle(self.parent / "second", self.manifest, self.bytes)

    def test_tagged_artifact_and_explicit_supersession_keep_original_identity(self):
        original = {key: value for key, value in self.source.items()
                    if key not in ("id", "content_path")}
        original["kind"] = "immutable_artifact"
        successor = dict(original, revision="revision-2", sha256="b" * 64)
        self.manifest["reviewed_candidate"] = original
        self.manifest["applicability"] = {
            "status": "superseded", "basis": "Controller's append-only disposition",
            "evidence_ref": "issue:CAK-310/comment:synthetic-exact-record",
            "superseded_by": successor,
        }
        result = self.stage()
        self.assertEqual(result["reviewed_candidate"], original)
        self.assertEqual(result["applicability"]["superseded_by"], successor)
        self.assertNotEqual(result["reviewed_candidate"], successor)

    def test_unobservable_applicability_and_empty_source_content_are_preserved(self):
        self.manifest["reviewed_candidate"]["commit"] = "a" * 64
        self.manifest["applicability"] = {"status": "unobservable", "basis": "No current decision"}
        self.source.update(byte_length=0, sha256=hashlib.sha256(b"").hexdigest())
        self.bytes[self.source["id"]] = b""
        self.assertEqual(self.stage(), self.manifest)

    def test_rejects_malformed_candidate_and_ambiguous_applicability(self):
        mutations = [
            lambda m: m["reviewed_candidate"].update(commit="main"),
            lambda m: m["reviewed_candidate"].update(kind="commit"),
            lambda m: m["reviewed_candidate"].update(revision="mixed-tag"),
            lambda m: m["reviewed_candidate"].update(repository="https://example.com/owner/repo"),
            lambda m: m["applicability"].update(status="superseded"),
            lambda m: m["applicability"].update(superseded_by=m["reviewed_candidate"]),
            lambda m: m["applicability"].update(status="superseded", superseded_by=m["reviewed_candidate"]),
            lambda m: m["applicability"].update(basis=" "),
            lambda m: m["applicability"].update(evidence_ref=""),
            lambda m: m.update(schema="future/v2"),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                manifest = deepcopy(self.manifest)
                mutate(manifest)
                with self.assertRaises(evidence.EvidenceError):
                    evidence.stage_bundle(self.bundle, manifest, self.bytes)
                self.assertFalse(self.bundle.exists())

    def test_rejects_source_selection_and_identity_ambiguity_before_writing(self):
        for key, value in [("id", ".."), ("id", "with/slash"), ("content_path", "../outside"),
                           ("content_path", "evidence/other"), ("namespace", "123"),
                           ("provider", "unknown"), ("object_id", "path:/filename"),
                           ("revision", ""), ("byte_length", True), ("sha256", "A" * 64)]:
            with self.subTest(key=key, value=value):
                manifest = deepcopy(self.manifest)
                manifest["sources"][0][key] = value
                with self.assertRaises(evidence.EvidenceError):
                    evidence.stage_bundle(self.bundle, manifest, self.bytes)
        self.manifest["sources"].append(deepcopy(self.source))
        with self.assertRaises(evidence.EvidenceError):
            self.stage()
        self.manifest["sources"].pop()
        for supplied in [{}, dict(self.bytes, extra=b"unselected"),
                         {self.source["id"]: b"wrong"}]:
            with self.assertRaises(evidence.EvidenceError):
                evidence.stage_bundle(self.bundle, self.manifest, supplied)
        self.assertFalse(self.bundle.exists())

    def test_detects_content_tamper_missing_extra_and_writable_files(self):
        self.stage()
        path = self.bundle / self.source["content_path"]
        for content in [b"short", b"x" * len(self.content)]:
            self.rewrite(path, content)
            with self.assertRaises(evidence.EvidenceError):
                evidence.verify_bundle(self.bundle)
        self.rewrite(path, self.content)
        path.chmod(0o600)
        with self.assertRaises(evidence.EvidenceError):
            evidence.verify_bundle(self.bundle)
        path.chmod(0o400)
        extra = self.bundle / "evidence" / "unselected"
        extra.write_bytes(b"extra")
        with self.assertRaises(evidence.EvidenceError):
            evidence.verify_bundle(self.bundle)
        extra.unlink()
        path.unlink()
        with self.assertRaises(evidence.EvidenceError):
            evidence.verify_bundle(self.bundle)

    def test_rejects_duplicate_json_keys_and_manifest_path_escape(self):
        self.stage()
        path = self.bundle / "manifest.json"
        raw = path.read_bytes()
        self.rewrite(path, raw.replace(b'"sources":', b'"sources": [], "sources":', 1))
        with self.assertRaises(evidence.EvidenceError):
            evidence.verify_bundle(self.bundle)
        self.manifest["sources"][0]["content_path"] = "../../outside"
        self.rewrite(path, json.dumps(self.manifest).encode())
        with self.assertRaises(evidence.EvidenceError):
            evidence.verify_bundle(self.bundle)

    def test_rejects_symlinks_hardlinks_and_special_files(self):
        self.stage()
        path = self.bundle / self.source["content_path"]
        outside = self.parent / "outside"
        outside.write_bytes(self.content)
        outside.chmod(0o400)
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises((evidence.EvidenceError, OSError)):
            evidence.verify_bundle(self.bundle)
        path.unlink()
        os.link(outside, path)
        with self.assertRaises(evidence.EvidenceError):
            evidence.verify_bundle(self.bundle)
        path.unlink()
        os.mkfifo(path, 0o400)
        with self.assertRaises(evidence.EvidenceError):
            evidence.verify_bundle(self.bundle)
        alias = self.parent / "alias"
        alias.symlink_to(self.bundle, target_is_directory=True)
        with self.assertRaises((evidence.EvidenceError, OSError)):
            evidence.verify_bundle(alias)

    def test_rejects_nonprivate_root_and_symlinked_parent_before_writes(self):
        self.bundle.mkdir(mode=0o755)
        with self.assertRaises(evidence.EvidenceError):
            self.stage()
        self.assertEqual(list(self.bundle.iterdir()), [])
        alias = self.parent / "alias"
        alias.symlink_to(self.parent, target_is_directory=True)
        with self.assertRaises((evidence.EvidenceError, OSError)):
            evidence.stage_bundle(alias / "other-bundle", self.manifest, self.bytes)
        self.assertFalse((self.parent / "other-bundle").exists())


if __name__ == "__main__":
    unittest.main()
