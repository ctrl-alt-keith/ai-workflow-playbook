"""Pure local recovery model for one bounded decision.

This is a synthetic CAK-301 dogfood seam.  It joins a compact breadcrumb to
explicit observations supplied by the owners it names; it performs no I/O and
cannot issue an effect.  Reconstructing a decision is deliberately distinct
from recovering current authority to take its bounded next action.
"""

from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class EffectState(str, Enum):
    KNOWN_NO_EFFECT = "known-no-effect"
    UNKNOWN = "unknown"
    EFFECTED = "effected"


class RecoveryDecision(str, Enum):
    RECOVERED_CURRENT_BOUNDED_AUTHORITY = "recovered-current-bounded-authority"
    HOLD_REQUIRED_OWNER_UNAVAILABLE = "hold-required-owner-unavailable"
    HOLD_OWNER_MISMATCH = "hold-owner-mismatch"
    HOLD_DECISION_INAPPLICABLE = "hold-decision-inapplicable"
    HOLD_CURRENT_CANDIDATE_DIVERGED = "hold-current-candidate-diverged"
    HOLD_EFFECT_UNKNOWN = "hold-effect-unknown"
    STOP_EFFECT_ALREADY_OBSERVED = "stop-effect-already-observed"
    HOLD_ROUTE_UNQUALIFIED = "hold-route-unqualified"
    RECOVERED_NO_CURRENT_AUTHORITY = "recovered-no-current-authority"


class NextAction(str, Enum):
    HOLD = "hold"
    LOCAL_BOUNDED_ACTION_ONLY = "local-bounded-action-only"


@dataclass(frozen=True)
class Breadcrumb:
    """Small durable handle; owners, not this handle, control current facts."""

    decision_ref: str
    decision_owner: str
    repository_owner: str
    authority_owner: str
    effect_owner: str
    route_owner: str
    candidate: str
    action: str
    property: str
    contract: str


@dataclass(frozen=True)
class DecisionRecord:
    ref: str
    owner: str
    candidate: str
    action: str
    property: str
    contract: str
    verdict: Verdict


@dataclass(frozen=True)
class Observation:
    owner: str
    available: bool = True


@dataclass(frozen=True)
class RepositoryObservation(Observation):
    candidate: str = ""


@dataclass(frozen=True)
class AuthorityObservation(Observation):
    current: bool = False
    candidate: str = ""
    action: str = ""


@dataclass(frozen=True)
class EffectObservation(Observation):
    state: EffectState = EffectState.UNKNOWN


@dataclass(frozen=True)
class RouteObservation(Observation):
    supports_action: bool = False
    claim_ceiling: str = ""


@dataclass(frozen=True)
class RecoveryResult:
    decision: RecoveryDecision
    next_action: NextAction
    observation: str
    claim_ceiling: str = ""


def _hold(decision, observation):
    return RecoveryResult(decision, NextAction.HOLD, observation)


def recover(
    breadcrumb: Breadcrumb,
    record: DecisionRecord,
    repository: RepositoryObservation,
    authority: AuthorityObservation,
    effect: EffectObservation,
    route: RouteObservation,
) -> RecoveryResult:
    """Recover only the supplied bounded decision and its current ceiling."""
    observations = (
        ("decision", record.owner, breadcrumb.decision_owner, True),
        ("repository", repository.owner, breadcrumb.repository_owner, repository.available),
        ("authority", authority.owner, breadcrumb.authority_owner, authority.available),
        ("effect", effect.owner, breadcrumb.effect_owner, effect.available),
        ("route", route.owner, breadcrumb.route_owner, route.available),
    )
    for name, actual_owner, expected_owner, available in observations:
        if not available:
            return _hold(RecoveryDecision.HOLD_REQUIRED_OWNER_UNAVAILABLE, f"{name} owner is unavailable")
        if actual_owner != expected_owner:
            return _hold(RecoveryDecision.HOLD_OWNER_MISMATCH, f"{name} fact came from a non-owning source")

    if (
        record.ref != breadcrumb.decision_ref
        or record.candidate != breadcrumb.candidate
        or record.action != breadcrumb.action
        or record.property != breadcrumb.property
        or record.contract != breadcrumb.contract
        or record.verdict is not Verdict.APPROVED
    ):
        return _hold(RecoveryDecision.HOLD_DECISION_INAPPLICABLE, "durable decision is not approved for this exact bounded question")
    if repository.candidate != breadcrumb.candidate:
        return _hold(RecoveryDecision.HOLD_CURRENT_CANDIDATE_DIVERGED, "current repository owner contradicts the durable decision")
    if effect.state is EffectState.UNKNOWN:
        return _hold(RecoveryDecision.HOLD_EFFECT_UNKNOWN, "effect truth remains unknown")
    if effect.state is EffectState.EFFECTED:
        return _hold(RecoveryDecision.STOP_EFFECT_ALREADY_OBSERVED, "logical effect is already observed")
    if not route.supports_action or not route.claim_ceiling:
        return _hold(RecoveryDecision.HOLD_ROUTE_UNQUALIFIED, "current route cannot support the bounded action")
    if not authority.current or authority.candidate != breadcrumb.candidate or authority.action != breadcrumb.action:
        return _hold(RecoveryDecision.RECOVERED_NO_CURRENT_AUTHORITY, "reconstructed approval is not current scoped execution authority")
    return RecoveryResult(
        RecoveryDecision.RECOVERED_CURRENT_BOUNDED_AUTHORITY,
        NextAction.LOCAL_BOUNDED_ACTION_ONLY,
        "current owners joined; the model permits only its named local bounded action",
        route.claim_ceiling,
    )
