"""Synthetic local eligibility model for one conditional squash-merge retry.

This model is deliberately not a GitHub client or a reusable approval system.
It makes local applicability decisions only: I1 supplies current facts, I2
supplies bounded authority, I3 holds unknown effects, I4 binds the exact
candidate/action, and I5 keeps route/claim changes visible.
"""

from dataclasses import dataclass, replace
from enum import Enum


class AttemptState(str, Enum):
    NOT_SUBMITTED = "not-submitted"
    KNOWN_NO_EFFECT = "known-no-effect"
    OUTCOME_UNKNOWN = "outcome-unknown"
    EFFECTED = "effected"


class Decision(str, Enum):
    RETRY_ELIGIBLE = "retry-eligible"
    HOLD_OUTCOME_UNKNOWN = "hold-outcome-unknown"
    STOP_EFFECTED = "stop-effected"
    STOP_ATTEMPT_NOT_PROVEN_NO_EFFECT = "stop-attempt-not-proven-no-effect"
    STOP_EPOCH_INVALIDATED = "stop-candidate-epoch-invalidated"
    STOP_ACTION_MISMATCH = "stop-action-mismatch"
    STOP_CONDITIONS_STALE = "stop-conditions-stale"
    STOP_CONDITIONS_FAILED = "stop-conditions-failed"
    STOP_AUTHORITY_MISSING = "stop-authority-missing"
    STOP_AUTHORITY_NOT_CURRENT = "stop-authority-not-current"
    STOP_AUTHORITY_SCOPE_MISMATCH = "stop-authority-scope-mismatch"


@dataclass(frozen=True)
class Candidate:
    pull_request: int
    head_sha: str
    context_epoch: int


@dataclass(frozen=True)
class Action:
    method: str = "squash"
    destination: str = "main"
    route_claim: str = "github-squash-merge"


@dataclass(frozen=True)
class Conditions:
    checks: str = "valid"
    readiness: str = "valid"
    mergeability: str = "valid"
    repository_policy: str = "valid"

    def problem(self):
        values = {
            "checks": self.checks,
            "readiness": self.readiness,
            "mergeability": self.mergeability,
            "repository-policy": self.repository_policy,
        }
        for name, value in values.items():
            if value == "stale":
                return "stale", name
            if value != "valid":
                return "failed", name
        return None, ""


@dataclass(frozen=True)
class Authority:
    action: Action
    candidate: Candidate
    current: bool = True


@dataclass(frozen=True)
class Envelope:
    action: Action
    candidate: Candidate
    attempt: AttemptState
    epoch_invalidated: bool = False

    def observe_candidate(self, observed: Candidate):
        """Monotonically remember a candidate/context divergence (I4)."""
        return replace(self, epoch_invalidated=self.epoch_invalidated or observed != self.candidate)


@dataclass(frozen=True)
class Eligibility:
    decision: Decision
    observation: str
    envelope: Envelope


def retry_eligibility(envelope, observed_candidate, action, conditions, authority):
    """Return an explainable local retry decision; it never performs a merge."""
    envelope = envelope.observe_candidate(observed_candidate)
    def result(decision, observation):
        return Eligibility(decision, observation, envelope)
    if envelope.attempt is AttemptState.OUTCOME_UNKNOWN:
        return result(Decision.HOLD_OUTCOME_UNKNOWN, "a prior submission may have reached GitHub")
    if envelope.attempt is AttemptState.EFFECTED:
        return result(Decision.STOP_EFFECTED, "the logical action is already effected")
    if envelope.attempt is not AttemptState.KNOWN_NO_EFFECT:
        return result(Decision.STOP_ATTEMPT_NOT_PROVEN_NO_EFFECT, "retry needs proven known-no-effect")
    if envelope.epoch_invalidated:
        return result(Decision.STOP_EPOCH_INVALIDATED, "candidate epoch was previously divergent")
    if action != envelope.action:
        return result(Decision.STOP_ACTION_MISMATCH, "method, destination, or route claim changed")
    kind, name = conditions.problem()
    if kind == "stale":
        return result(Decision.STOP_CONDITIONS_STALE, name)
    if kind == "failed":
        return result(Decision.STOP_CONDITIONS_FAILED, name)
    if authority is None:
        return result(Decision.STOP_AUTHORITY_MISSING, "conditions and capability do not create authority")
    if not authority.current:
        return result(Decision.STOP_AUTHORITY_NOT_CURRENT, "authority was revoked or expired")
    if authority.candidate != envelope.candidate or authority.action != envelope.action:
        return result(Decision.STOP_AUTHORITY_SCOPE_MISMATCH, "authority is not scoped to this action and candidate")
    return result(Decision.RETRY_ELIGIBLE, "known-no-effect with fresh conditions and current scoped authority")
