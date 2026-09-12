"""Official SDK seam. Network disabled except explicit loopback fixture tests.

Current sources, checked 2026-09-12, and all claim ceilings are in README.md.
No error string from the historical connector is classified here.
"""

from dataclasses import asdict, dataclass
from importlib.metadata import version
import posixpath
import re
from urllib.parse import urlsplit

import dropbox
import requests
from requests.adapters import HTTPAdapter

from .model import Blocked, MAX_BYTES, Object, Observation, Qualification, digest, encode


class NoRefreshDropbox(dropbox.Dropbox):
    def refresh_access_token(self, *args, **kwargs):
        # SDK 12.2.1 has an expired-token retry branch independent of 5xx/429.
        raise Blocked("implicit credential refresh disabled")


class BoundedHTTPAdapter(HTTPAdapter):
    def __init__(self, fixture_origin=None):
        super().__init__(max_retries=0)
        if fixture_origin is not None and not re.fullmatch(r"http://127\.0\.0\.1:[0-9]+", fixture_origin):
            raise Blocked("only explicit loopback fixtures supported")
        self.fixture_origin = fixture_origin

    def send(self, request, **kwargs):
        if self.fixture_origin is None:
            raise Blocked("live provider transport not enabled in increments 0-2")
        if urlsplit(request.url).hostname not in {"api.dropboxapi.com", "content.dropboxapi.com"}:
            raise Blocked("unexpected SDK endpoint")
        # Preserve real SDK serialization and HTTPAdapter/urllib3 behavior,
        # replacing only the socket destination with the explicit local fixture.
        request.url = self.fixture_origin + urlsplit(request.url).path
        return super().send(request, **kwargs)


class SingleRequestSession(requests.Session):
    def __init__(self, fixture_origin=None):
        super().__init__()
        self.trust_env = False
        self.mount("https://", BoundedHTTPAdapter(fixture_origin))
        self.mount("http://", BoundedHTTPAdapter())

    def request(self, method, url, **kwargs):
        kwargs["allow_redirects"] = False
        response = super().request(method, url, **kwargs)
        if 300 <= response.status_code < 400:
            response.close()
            raise Blocked("redirect refused")
        return response


class ReadOnlySession(SingleRequestSession):
    def request(self, method, url, **kwargs):
        if urlsplit(url).path not in {"/2/users/get_current_account", "/2/files/get_metadata", "/2/files/download"}:
            raise Blocked("reader transport refuses non-read route")
        return super().request(method, url, **kwargs)


@dataclass(frozen=True)
class Config:
    account: str
    namespace: str
    parent: str
    parent_path: str
    actor: str
    credential_ref: str
    timeout: float = 10

    @property
    def fingerprint(self):
        return digest(encode(asdict(self)).encode())

    def validate(self):
        if not all((self.account, self.parent, self.actor, self.credential_ref)) or not self.namespace.isdecimal() or not 0 < self.timeout <= 30:
            raise Blocked("explicit account/namespace/parent/actor/credential binding required")


def make_client(config, *, fixture_origin=None, read_only=False):
    config.validate()
    if version("dropbox") != "12.2.1" or version("requests") != "2.34.2" or version("urllib3") != "2.7.0":
        raise Blocked("transport dependency drift")
    session = (ReadOnlySession if read_only else SingleRequestSession)(fixture_origin)
    # Only a synthetic credential is accepted in this development surface.
    # Provisioning actual credentials belongs to the separately authorized stage.
    client = NoRefreshDropbox(oauth2_access_token="synthetic-local-test-token",
                             max_retries_on_error=0, max_retries_on_rate_limit=0,
                             timeout=config.timeout, session=session,
                             headers={"Dropbox-API-Path-Root": encode({".tag": "namespace_id", "namespace_id": config.namespace})})
    return client


def check_config(client, config, op):
    if (config.account, config.namespace, config.parent) != (op.target.account, op.target.namespace, op.target.parent) or posixpath.dirname(op.target.path) != config.parent_path or config.actor != op.actor:
        raise Blocked("Dropbox account/namespace/parent/actor scope mismatch")
    if (client._max_retries_on_error != 0 or client._max_retries_on_rate_limit != 0
            or client._oauth2_refresh_token or client._session.trust_env
            or type(client) is not NoRefreshDropbox or type(client._session) not in {SingleRequestSession, ReadOnlySession}
            or client._oauth2_access_token != "synthetic-local-test-token"
            or client._timeout != config.timeout
            or client._session.auth or client._session.proxies
            or client._session.get_adapter("https://content.dropboxapi.com").max_retries.total != 0
            or client._headers != {"Dropbox-API-Path-Root": encode({".tag": "namespace_id", "namespace_id": config.namespace})}):
        raise Blocked("effective transport configuration drift")


def transport_fingerprint(client, config):
    adapter = client._session.get_adapter("https://content.dropboxapi.com")
    if type(adapter) is not BoundedHTTPAdapter:
        raise Blocked("transport implementation drift")
    return digest(encode([config.fingerprint, adapter.fixture_origin]).encode())


def read_identity(client, config, op):
    check_config(client, config, op)
    account = client.users_get_current_account()
    parent = client.files_get_metadata(config.parent_path)
    if account.account_id != config.account or not isinstance(parent, dropbox.files.FolderMetadata) or parent.id != config.parent or parent.path_lower != config.parent_path:
        raise Blocked("observed account or parent mismatch")


class DropboxReader:
    __slots__ = ("__client", "config", "qualification")

    def __init__(self, client, config, qualification):
        self.__client, self.config, self.qualification = client, config, qualification

    def observe(self, op, known=()):
        self.qualification.require_local(op)
        if self.qualification.config_hash != transport_fingerprint(self.__client, self.config):
            raise Blocked("reader configuration drift")
        client = self.__client
        read_identity(client, self.config, op)
        try:
            current = client.files_get_metadata(op.target.path)
        except dropbox.exceptions.ApiError as exc:
            # Documented tagged lookup error; absence remains only this read.
            if exc.error.is_path() and exc.error.get_path().is_not_found():
                return Observation((), True, "single target lookup; no terminal absence claim")
            return Observation(error="metadata unavailable")
        if not isinstance(current, dropbox.files.FileMetadata):
            return Observation(error="target is not a file")
        versions = list(dict.fromkeys([*known, (current.id, current.rev)]))
        objects = []
        for object_id, revision in versions:
            metadata, response = client.files_download("rev:" + revision)
            try:
                parts, size = [], 0
                for part in response.iter_content(65536):
                    size += len(part)
                    if size > MAX_BYTES:
                        raise Blocked("readback exceeds payload ceiling")
                    parts.append(part)
                data = b"".join(parts)
            finally:
                response.close()
            if (metadata.id, metadata.rev) != (object_id, revision) or metadata.path_lower != op.target.path:
                return Observation(tuple(objects), False, "revision readback", "returned identity/containment mismatch")
            objects.append(Object(metadata.id, metadata.rev, op.target, metadata.size, data, (object_id, revision) in known))
        after = client.files_get_metadata(op.target.path)
        stable = (after.id, after.rev, after.path_lower) == (current.id, current.rev, op.target.path)
        return Observation(tuple(objects), stable, "target plus returned versions; no global cardinality claim", "" if stable else "version drift")


class DropboxWriter:
    def __init__(self, config, target, *, fixture_origin=None):
        self.config = config
        self._client = make_client(config, fixture_origin=fixture_origin)
        self._read_client = make_client(config, fixture_origin=fixture_origin, read_only=True)
        self.qualification = Qualification("dropbox-sdk", "12.2.1/requests-2.34.2/urllib3-2.7.0", transport_fingerprint(self._client, config),
                                           target, "repository-loopback-acceptance", "2026-09-12", "local" if fixture_origin else "unqualified")

    def reader(self):
        return DropboxReader(self._read_client, self.config, self.qualification)

    def close(self):
        self._client.close()
        self._read_client.close()

    def check_binding(self, op, actor):
        check_config(self._client, self.config, op)
        if actor != self.config.actor or self.qualification.config_hash != transport_fingerprint(self._client, self.config):
            raise Blocked("acting identity mismatch")

    def submit(self, op, data):
        self.qualification.require_local(op)
        self.check_binding(op, op.actor)
        metadata = self._client.files_upload(data, op.target.path, mode=dropbox.files.WriteMode.add,
                                             autorename=False, strict_conflict=True, mute=True)
        if not isinstance(metadata, dropbox.files.FileMetadata) or metadata.path_lower != op.target.path or metadata.size != len(data):
            raise Blocked("upload returned identity mismatch; possible effect")
        return metadata.id, metadata.rev
