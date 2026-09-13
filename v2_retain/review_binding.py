"""Pure local model of exact evaluation-to-acceptance binding.

This synthetic CAK-301 dogfood seam answers one narrow review-path question:
a favorable evaluation is usable only when the decision owner accepts that
evaluation for the same candidate, property, and governing contract. It does
not retrieve sources, run an evaluator, or authorize an effect.
"""

from dataclasses import dataclass
from enum import Enum


class EvaluationVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"


class ReviewDecision(str, Enum):
    ACCEPTED_LOCAL_REVIEW_EVIDENCE = "accepted-local-review-evidence"
    HOLD_OWNER_MISMATCH = "hold-owner-mismatch"
    HOLD_EVALUATION_INAPPLICABLE = "hold-evaluation-inapplicable"
    HOLD_ACCEPTANCE_MISSING = "hold-acceptance-missing"
    HOLD_ACCEPTANCE_INAPPLICABLE = "hold-acceptance-inapplicable"
    HOLD_ROUTE_UNQUALIFIED = "hold-route-unqualified"


class NextAction(str, Enum):
    HOLD = "hold"
    NO_EXECUTION_AUTHORITY = "no-execution-authority"


@dataclass(frozen=True)
class ReviewQuestion:
    candidate: str
    property: str
    contract: str
    evaluation_owner: str
    acceptance_owner: str
    route_owner: str
    required_route_profile: str


@dataclass(frozen=True)
class Evaluation:
    ref: str
    owner: str
    candidate: str
    property: str
    contract: str
    verdict: EvaluationVerdict


@dataclass(frozen=True)
class Acceptance:
    owner: str
    evaluation_ref: str
    candidate: str
    property: str
    contract: str
    accepted: bool


@dataclass(frozen=True)
class RouteObservation:
    owner: str
    profile: str
    supports_review_use: bool
    claim_ceiling: str


@dataclass(frozen=True)
class ReviewResult:
    decision: ReviewDecision
    next_action: NextAction
    observation: str
    claim_ceiling: str = ""


def _hold(decision, observation):
    return ReviewResult(decision, NextAction.HOLD, observation)


def bind(
    question: ReviewQuestion,
    evaluation: Evaluation,
    acceptance: Acceptance | None,
    route: RouteObservation,
) -> ReviewResult:
    """Return only the local review-evidence ceiling for this exact question."""
    for actual, expected in (
        (evaluation.owner, question.evaluation_owner),
        (route.owner, question.route_owner),
    ):
        if actual != expected:
            return _hold(
                ReviewDecision.HOLD_OWNER_MISMATCH,
                "evaluation or route came from a non-owning source",
            )
    if (
        evaluation.candidate != question.candidate
        or evaluation.property != question.property
        or evaluation.contract != question.contract
        or evaluation.verdict is not EvaluationVerdict.PASS
    ):
        return _hold(
            ReviewDecision.HOLD_EVALUATION_INAPPLICABLE,
            "evaluation does not pass for this exact review question",
        )
    if acceptance is None:
        return _hold(ReviewDecision.HOLD_ACCEPTANCE_MISSING, "a favorable evaluation is not acceptance")
    if acceptance.owner != question.acceptance_owner:
        return _hold(ReviewDecision.HOLD_OWNER_MISMATCH, "acceptance came from a non-owning source")
    if (
        not acceptance.accepted
        or acceptance.evaluation_ref != evaluation.ref
        or acceptance.candidate != question.candidate
        or acceptance.property != question.property
        or acceptance.contract != question.contract
    ):
        return _hold(
            ReviewDecision.HOLD_ACCEPTANCE_INAPPLICABLE,
            "acceptance is not exclusively bound to this evaluation and question",
        )
    if (
        route.profile != question.required_route_profile
        or not route.supports_review_use
        or not route.claim_ceiling
    ):
        return _hold(
            ReviewDecision.HOLD_ROUTE_UNQUALIFIED,
            "current route cannot support the bounded review use",
        )
    return ReviewResult(
        ReviewDecision.ACCEPTED_LOCAL_REVIEW_EVIDENCE,
        NextAction.NO_EXECUTION_AUTHORITY,
        "acceptance is exact and route-qualified; it grants no execution authority",
        route.claim_ceiling,
    )
