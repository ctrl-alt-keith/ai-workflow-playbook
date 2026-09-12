"""One provisional retention contract, independent of provider or UI status."""

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import re

MAX_BYTES = 16 * 1024 * 1024
MAX_OBSERVATIONS = 256
CONTRACT = "retain-exact/experimental-1"


class Blocked(Exception):
    """A required fact or boundary cannot be established."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class Target:
    account: str
    namespace: str
    parent: str
    path: str

    def validate(self):
        # Deliberately narrow ASCII lowercase target profile; no path aliases.
        if not all((self.account, self.namespace, self.parent)):
            raise Blocked("target owner missing")
        if not re.fullmatch(r"/(?:[a-z0-9_-]+/)*[a-z0-9_-]+(?:\.[a-z0-9_-]+)*", self.path):
            raise Blocked("target must be an exact lowercase ASCII path")


@dataclass(frozen=True)
class Operation:
    op_id: str
    owner: str
    source_ref: str
    contract_ref: str
    contract_hash: str
    actor: str
    target: Target
    grant_ref: str
    not_before: float
    expires_at: float
    retention_ref: str
    visibility_ref: str
    input_hash: str
    size: int
    route_hash: str
    text_utf8: bool = False
    final_lf: bool = False
    decision_owner: str = ""
    decision_property: str = ""
    predecessor: str = ""
    semantics: str = CONTRACT

    @property
    def effect_id(self):
        return self.op_id + "/retain"

    def validate(self, data):
        self.target.validate()
        required = (self.op_id, self.owner, self.source_ref, self.contract_ref,
                    self.actor, self.grant_ref, self.retention_ref, self.visibility_ref)
        if not all(isinstance(v, str) and 0 < len(v) <= 1024 for v in required):
            raise Blocked("missing or oversized operation reference")
        for value in (self.contract_hash, self.input_hash, self.route_hash):
            if not re.fullmatch(r"[0-9a-f]{64}", value):
                raise Blocked("invalid exact digest")
        if self.semantics != CONTRACT or bool(self.decision_owner) != bool(self.decision_property):
            raise Blocked("unsupported contract or incomplete decision scope")
        if not all(math.isfinite(v) for v in (self.not_before, self.expires_at)) or self.not_before >= self.expires_at:
            raise Blocked("invalid original validity")
        if len(data) != self.size or self.size > MAX_BYTES or digest(data) != self.input_hash:
            raise Blocked("input identity or size mismatch")
        if self.text_utf8:
            try:
                data.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise Blocked("invalid UTF-8") from exc
        if self.final_lf and not data.endswith(b"\n"):
            raise Blocked("required final LF missing")

    def json(self):
        return encode(asdict(self))

    @classmethod
    def parse(cls, raw):
        obj = json.loads(raw)
        obj["target"] = Target(**obj["target"])
        return cls(**obj)


@dataclass(frozen=True)
class Object:
    object_id: str
    revision: str
    target: Target
    size: int
    data: bytes
    correlated: bool


@dataclass(frozen=True)
class Observation:
    objects: tuple[Object, ...] = ()
    complete: bool = False
    scope: str = "unknown"
    error: str = ""


@dataclass(frozen=True)
class Qualification:
    route: str
    build: str
    config_hash: str
    target_scope: Target
    evidence_ref: str
    checked_at: str
    environment: str
    create: str = "strict-create-no-autorename"
    retries: int = 0
    admission: str = "local-synchronous-call"
    ceiling: str = "local-test-only"
    collision_request_ref: str = "unqualified"
    collision_response_ref: str = "unqualified"
    invalidation: str = "build/config/account/namespace/parent/identity/readback/retry drift"
    actor_account: str = ""
    root_namespace: str = ""
    home_namespace: str = ""
    app_root: str = ""
    parent_id: str = ""
    parent_path: str = ""
    credential_label: str = ""
    sdk_version: str = ""
    head: str = ""

    @property
    def fingerprint(self):
        return digest(encode(asdict(self)).encode())

    def require_local(self, op):
        if (self.environment != "local" or self.ceiling != "local-test-only"
                or self.retries != 0 or self.create != "strict-create-no-autorename"
                or self.admission != "local-synchronous-call"
                or not all((self.build, self.config_hash, self.evidence_ref, self.checked_at))
                or self.fingerprint != op.route_hash
                or self.target_scope != op.target):
            raise Blocked("route unqualified or configuration drift")

    def require_active(self, op):
        if self.environment == "local":
            return self.require_local(op)
        if (self.environment != "live-qualification" or self.ceiling != "bounded-live-qualification-only"
                or self.retries != 0 or self.create != "strict-create-no-autorename"
                or self.admission != "local-synchronous-call"
                or not all((self.build, self.config_hash, self.evidence_ref, self.checked_at,
                            self.actor_account, self.root_namespace, self.home_namespace,
                            self.app_root, self.parent_id, self.parent_path,
                            self.credential_label, self.sdk_version, self.head))
                or self.app_root != "implicit-app-folder-root"
                or self.fingerprint != op.route_hash or self.target_scope != op.target
                or self.actor_account != op.target.account or self.parent_id != op.target.parent
                or self.parent_path != op.target.path.rsplit("/", 1)[0]):
            raise Blocked("live qualification route or scope not bound")
