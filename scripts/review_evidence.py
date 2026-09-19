"""Local, integrity-checked supplied evidence; never a provider observation.

The controller owns source selection, authorization, provider verification, and
the applicability decision. This module validates their representation and the
selected bytes. It grants no capability or authority and makes no network calls.
See review-evidence.md for the consumer boundary and v1 manifest contract.
"""

from collections.abc import Mapping
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any


BUNDLE_SCHEMA = "governed-review-evidence-bundle/v1"
MANIFEST_NAME = "manifest.json"


class EvidenceError(ValueError):
    """Malformed identity, unsafe bundle layout, or integrity failure."""


def _fields(value, required, optional=()):
    if not isinstance(value, Mapping):
        raise EvidenceError("expected an object")
    if not set(required) <= set(value) or set(value) - set(required) - set(optional):
        raise EvidenceError("missing or unsupported fields")


def _text(value):
    if (not isinstance(value, str) or not value.strip() or value != value.strip()
            or any(ord(character) < 32 or ord(character) == 127 for character in value)):
        raise EvidenceError("expected nonempty, unambiguous text")
    return value


def _match(value, pattern):
    if not re.fullmatch(pattern, _text(value), flags=re.ASCII):
        raise EvidenceError("malformed identity or path")


def _content_identity(value, *, positive=False):
    if value["provider"] != "dropbox":
        raise EvidenceError("unsupported provider")
    _match(value["namespace"], r"ns:[0-9]+")
    _match(value["object_id"], r"id:[A-Za-z0-9_-]+")
    _text(value["revision"])
    if type(value["byte_length"]) is not int or value["byte_length"] < int(positive):
        raise EvidenceError("invalid byte length")
    _match(value["sha256"], r"[0-9a-f]{64}")


def _candidate(value):
    if not isinstance(value, Mapping):
        raise EvidenceError("expected tagged candidate")
    if value.get("kind") == "repository_commit":
        _fields(value, ("kind", "repository", "commit"))
        _match(value["repository"], r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
        if any(part in (".", "..") for part in value["repository"].split("/")):
            raise EvidenceError("ambiguous repository identity")
        _match(value["commit"], r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
    elif value.get("kind") == "immutable_artifact":
        _fields(value, ("kind", "provider", "namespace", "object_id", "revision",
                        "byte_length", "sha256"))
        _content_identity(value, positive=True)
    else:
        raise EvidenceError("unsupported candidate kind")


def _manifest(value):
    _fields(value, ("schema", "reviewed_candidate", "applicability", "sources"))
    if value["schema"] != BUNDLE_SCHEMA:
        raise EvidenceError("unsupported bundle schema")
    _candidate(value["reviewed_candidate"])
    applicability = value["applicability"]
    _fields(applicability, ("status", "basis"), ("evidence_ref", "superseded_by"))
    status = applicability["status"]
    if status not in ("applicable", "superseded", "unobservable"):
        raise EvidenceError("unsupported applicability status")
    _text(applicability["basis"])
    if "evidence_ref" in applicability:
        _text(applicability["evidence_ref"])
    if (status == "superseded") != ("superseded_by" in applicability):
        raise EvidenceError("supersession requires status and exact successor")
    if status == "superseded":
        _candidate(applicability["superseded_by"])
        if applicability["superseded_by"] == value["reviewed_candidate"]:
            raise EvidenceError("candidate cannot supersede itself")
    if not isinstance(value["sources"], list) or not value["sources"]:
        raise EvidenceError("expected selected evidence sources")
    seen = set()
    for source in value["sources"]:
        _fields(source, ("id", "provider", "namespace", "object_id", "revision",
                         "byte_length", "sha256", "content_path"))
        _match(source["id"], r"[A-Za-z0-9._-]+")
        if source["id"] in (".", "..") or source["id"] in seen:
            raise EvidenceError("invalid or duplicate source id")
        seen.add(source["id"])
        if source["content_path"] != "evidence/" + source["id"]:
            raise EvidenceError("content path must name its source under evidence/")
        _content_identity(source)
    # Accept Mapping implementations, returning detached plain JSON objects.
    applicability = dict(applicability)
    if "superseded_by" in applicability:
        applicability["superseded_by"] = dict(applicability["superseded_by"])
    return {"schema": value["schema"], "reviewed_candidate": dict(value["reviewed_candidate"]),
            "applicability": applicability, "sources": [dict(source) for source in value["sources"]]}


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise EvidenceError("duplicate JSON key")
        value[key] = item
    return value


def _check_stat(info, *, directory):
    expected = 0o700 if directory else 0o400
    correct_type = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    if (not correct_type or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) != expected
            or (not directory and info.st_nlink != 1)):
        raise EvidenceError("bundle object has unsafe type, owner, mode, or links")


@contextmanager
def _directory(path):
    """Open every component without following links, retaining the final fd."""
    path = Path(path).absolute()
    if ".." in path.parts:
        raise EvidenceError("parent traversal is prohibited")
    descriptor = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            next_descriptor = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                      dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        _check_stat(os.fstat(descriptor), directory=True)
        yield descriptor
        # Reject replacement of the visible root during this operation.
        info = path.lstat()
        opened = os.fstat(descriptor)
        if (info.st_dev, info.st_ino) != (opened.st_dev, opened.st_ino):
            raise EvidenceError("bundle directory identity changed")
        _check_stat(info, directory=True)
    finally:
        os.close(descriptor)


def _read_file(directory, name):
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    with os.fdopen(descriptor, "rb") as stream:
        _check_stat(os.fstat(stream.fileno()), directory=False)
        return stream.read()


def _write_file(directory, name, content):
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o400, dir_fd=directory)
    with os.fdopen(descriptor, "wb") as stream:
        os.fchmod(stream.fileno(), 0o400)
        stream.write(content)


def _check_content(source, content):
    if (type(content) is not bytes or len(content) != source["byte_length"]
            or hashlib.sha256(content).hexdigest() != source["sha256"]):
        raise EvidenceError("source byte length or SHA-256 mismatch")


def stage_bundle(bundle_dir: Path, manifest: Mapping[str, Any],
                 source_bytes: Mapping[str, bytes]) -> dict[str, Any]:
    """Create selected local evidence exclusively under a private bundle root.

    The parent must already exist under the caller's authorized attempt-local
    storage contract. An existing root must be empty, owned by this user, 0700,
    and free of symlinks. On failure, partial output is left for the owning
    attempt's cleanup; it is never reused, overwritten, or considered valid.
    """
    validated = _manifest(manifest)
    if not isinstance(source_bytes, Mapping) or set(source_bytes) != {
            source["id"] for source in validated["sources"]}:
        raise EvidenceError("source bytes do not match the selected source set")
    for source in validated["sources"]:
        _check_content(source, source_bytes[source["id"]])
    bundle_dir = Path(bundle_dir).absolute()
    # Validate the parent before mkdir; never create through an aliased parent.
    with _directory(bundle_dir.parent) as parent:
        try:
            os.mkdir(bundle_dir.name, 0o700, dir_fd=parent)
        except FileExistsError:
            pass
        with _directory(bundle_dir) as root:
            if os.listdir(root):
                raise EvidenceError("bundle destination must be empty")
            os.mkdir("evidence", 0o700, dir_fd=root)
            evidence = os.open("evidence", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                               dir_fd=root)
            try:
                for source in validated["sources"]:
                    _write_file(evidence, source["id"], source_bytes[source["id"]])
            finally:
                os.close(evidence)
            content = (json.dumps(validated, ensure_ascii=True, sort_keys=True, indent=2)
                       + "\n").encode("utf-8")
            _write_file(root, MANIFEST_NAME, content)
    return verify_bundle(bundle_dir)


def verify_bundle(bundle_dir: Path) -> dict[str, Any]:
    """Revalidate local structure/bytes; never assert live provider observation.

    This does not authenticate the controller's claims or resist an authorized
    same-user process replacing the entire bundle. The launcher must bind this
    returned manifest to its exact candidate and restrict the reviewer to reads.
    """
    with _directory(bundle_dir) as root:
        if set(os.listdir(root)) != {MANIFEST_NAME, "evidence"}:
            raise EvidenceError("unexpected or missing bundle files")
        try:
            manifest = _manifest(json.loads(_read_file(root, MANIFEST_NAME),
                                           object_pairs_hook=_unique_object))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise EvidenceError("invalid manifest JSON") from error
        evidence = os.open("evidence", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                           dir_fd=root)
        try:
            _check_stat(os.fstat(evidence), directory=True)
            if set(os.listdir(evidence)) != {source["id"] for source in manifest["sources"]}:
                raise EvidenceError("unexpected or missing evidence files")
            for source in manifest["sources"]:
                _check_content(source, _read_file(evidence, source["id"]))
        finally:
            os.close(evidence)
    return manifest
