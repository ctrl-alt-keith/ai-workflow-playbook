"""Official SDK seam. Default transport is loopback-only; live is explicit.

Current sources, checked 2026-09-12, and all claim ceilings are in README.md.
No error string from the historical connector is classified here.
"""

from dataclasses import asdict, dataclass
from importlib.metadata import version
import os
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
    def __init__(self, fixture_origin=None, *, live=False):
        super().__init__(max_retries=0)
        if live and fixture_origin is not None:
            raise Blocked("live transport cannot use fixture origin")
        if fixture_origin is not None and not re.fullmatch(r"http://127\.0\.0\.1:[0-9]+", fixture_origin):
            raise Blocked("only explicit loopback fixtures supported")
        self.fixture_origin = fixture_origin
        self.live = live

    def send(self, request, **kwargs):
        parsed = urlsplit(request.url)
        if parsed.scheme != "https" or parsed.hostname not in {"api.dropboxapi.com", "content.dropboxapi.com"} or parsed.port is not None:
            raise Blocked("unexpected SDK endpoint")
        if self.live:
            return super().send(request, **kwargs)
        if self.fixture_origin is None:
            raise Blocked("provider transport disabled outside explicit live qualification")
        # Preserve real SDK serialization and HTTPAdapter/urllib3 behavior,
        # replacing only the socket destination with the explicit local fixture.
        request.url = self.fixture_origin + urlsplit(request.url).path
        return super().send(request, **kwargs)


class SingleRequestSession(requests.Session):
    def __init__(self, fixture_origin=None, *, live=False):
        super().__init__()
        self.trust_env = False
        self.mount("https://", BoundedHTTPAdapter(fixture_origin, live=live))
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
        if urlsplit(url).path not in {"/2/users/get_current_account", "/2/files/get_metadata", "/2/files/download", "/2/files/list_folder"}:
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
    profile: str = "local"
    root_namespace: str = ""
    home_namespace: str = ""
    head: str = ""

    @property
    def fingerprint(self):
        return digest(encode(asdict(self)).encode())

    def validate(self):
        if not all((self.account, self.parent, self.actor, self.credential_ref)) or not self.namespace.isdecimal() or not 0 < self.timeout <= 30:
            raise Blocked("explicit account/namespace/parent/actor/credential binding required")
        if self.profile not in {"local", "live-qualification"}:
            raise Blocked("unknown Dropbox profile")
        if self.profile == "live-qualification" and (not self.root_namespace.isdecimal() or not self.home_namespace.isdecimal()
                or self.namespace != self.home_namespace or not re.fullmatch(r"[0-9a-f]{40}", self.head)):
            raise Blocked("live account root and exact head required")


def make_client(config, *, fixture_origin=None, read_only=False, access_token=None):
    config.validate()
    if version("dropbox") != "12.2.1" or version("requests") != "2.34.2" or version("urllib3") != "2.7.0":
        raise Blocked("transport dependency drift")
    live = config.profile == "live-qualification"
    if live:
        if (fixture_origin is not None or not access_token or access_token.startswith("op://")
                or access_token == "synthetic-local-test-token"
                or os.environ.get("DROPBOX_ACCESS_TOKEN") != access_token):
            raise Blocked("resolved environment credential required for live qualification")
    elif access_token is not None:
        raise Blocked("default profile refuses supplied credential")
    session = (ReadOnlySession if read_only else SingleRequestSession)(fixture_origin, live=live)
    client = NoRefreshDropbox(oauth2_access_token=access_token if live else "synthetic-local-test-token",
                             max_retries_on_error=0, max_retries_on_rate_limit=0,
                             timeout=config.timeout, session=session,
                             headers={} if live else {"Dropbox-API-Path-Root": encode({".tag": "namespace_id", "namespace_id": config.namespace})})
    return client


def check_config(client, config, op):
    if (config.account, config.namespace, config.parent) != (op.target.account, op.target.namespace, op.target.parent) or posixpath.dirname(op.target.path) != config.parent_path or config.actor != op.actor:
        raise Blocked("Dropbox account/namespace/parent/actor scope mismatch")
    if (client._max_retries_on_error != 0 or client._max_retries_on_rate_limit != 0
            or client._oauth2_refresh_token or client._session.trust_env
            or type(client) is not NoRefreshDropbox or type(client._session) not in {SingleRequestSession, ReadOnlySession}
            or not client._oauth2_access_token
            or (config.profile == "local" and client._oauth2_access_token != "synthetic-local-test-token")
            or (config.profile == "live-qualification" and (client._oauth2_access_token == "synthetic-local-test-token" or client._oauth2_access_token.startswith("op://")))
            or client._timeout != config.timeout
            or client._session.auth or client._session.proxies
            or client._session.get_adapter("https://content.dropboxapi.com").max_retries.total != 0
            or client._headers != ({} if config.profile == "live-qualification" else {"Dropbox-API-Path-Root": encode({".tag": "namespace_id", "namespace_id": config.namespace})})
            or client._session.get_adapter("https://content.dropboxapi.com").live != (config.profile == "live-qualification")):
        raise Blocked("effective transport configuration drift")


def transport_fingerprint(client, config):
    adapter = client._session.get_adapter("https://content.dropboxapi.com")
    if type(adapter) is not BoundedHTTPAdapter:
        raise Blocked("transport implementation drift")
    return digest(encode([config.fingerprint, adapter.fixture_origin, adapter.live]).encode())


def read_identity(client, config, op):
    check_config(client, config, op)
    account = client.users_get_current_account()
    if config.profile == "live-qualification":
        root = account.root_info
        if root is None or root.root_namespace_id != config.root_namespace or root.home_namespace_id != config.home_namespace:
            raise Blocked("account root namespace mismatch")
        # The App Folder is the implicit API root; Dropbox does not return
        # metadata for that root. A read-only root listing verifies access.
        client.files_list_folder("")
    parent = client.files_get_metadata(config.parent_path)
    if account.account_id != config.account or not isinstance(parent, dropbox.files.FolderMetadata) or parent.id != config.parent or parent.path_lower != config.parent_path:
        raise Blocked("observed account or parent mismatch")


def strict_create(client, path, data):
    return client.files_upload(data, path, mode=dropbox.files.WriteMode.add,
                               autorename=False, strict_conflict=True, mute=True)


class DropboxReader:
    __slots__ = ("__client", "config", "qualification")

    def __init__(self, client, config, qualification):
        self.__client, self.config, self.qualification = client, config, qualification

    def observe(self, op, known=()):
        self.qualification.require_active(op)
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
    def __init__(self, config, target, *, fixture_origin=None, access_token=None):
        self.config = config
        self._client = make_client(config, fixture_origin=fixture_origin, access_token=access_token)
        self._read_client = make_client(config, fixture_origin=fixture_origin, read_only=True, access_token=access_token)
        self.qualification = Qualification("dropbox-sdk", "12.2.1/requests-2.34.2/urllib3-2.7.0", transport_fingerprint(self._client, config),
                                           target, "repository-loopback-acceptance" if fixture_origin else "live-identity-and-scope-preflight",
                                           "2026-09-12", "local" if fixture_origin else "live-qualification" if config.profile == "live-qualification" else "unqualified",
                                           ceiling="bounded-live-qualification-only" if config.profile == "live-qualification" else "local-test-only",
                                           actor_account=config.account if config.profile == "live-qualification" else "",
                                           root_namespace=config.root_namespace, home_namespace=config.home_namespace,
                                           app_root="implicit-app-folder-root" if config.profile == "live-qualification" else "",
                                           parent_id=config.parent if config.profile == "live-qualification" else "",
                                           parent_path=config.parent_path if config.profile == "live-qualification" else "",
                                           credential_label=config.credential_ref if config.profile == "live-qualification" else "",
                                           sdk_version="12.2.1" if config.profile == "live-qualification" else "",
                                           head=config.head)

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
        self.qualification.require_active(op)
        self.check_binding(op, op.actor)
        if len(data) != op.size or digest(data) != op.input_hash:
            raise Blocked("submitted bytes do not match operation")
        if self.config.profile == "live-qualification":
            read_identity(self._client, self.config, op)
        metadata = strict_create(self._client, op.target.path, data)
        if not isinstance(metadata, dropbox.files.FileMetadata) or metadata.path_lower != op.target.path or metadata.size != len(data):
            raise Blocked("upload returned identity mismatch; possible effect")
        return metadata.id, metadata.rev
