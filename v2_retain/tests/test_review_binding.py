"""Adversarial tests for the bounded local review-binding model."""

import unittest
from dataclasses import replace

from v2_retain.review_binding import (
    Acceptance,
    Evaluation,
    EvaluationVerdict,
    NextAction,
    ReviewDecision,
    ReviewQuestion,
    RouteObservation,
    bind,
)


class ReviewBindingTests(unittest.TestCase):
    def setUp(self):
        self.question = ReviewQuestion(
            "candidate:7", "retain", "C1", "evaluator", "reviewer", "route-owner", "profile:direct"
        )
        self.evaluation = Evaluation(
            "eval:7", "evaluator", "candidate:7", "retain", "C1", EvaluationVerdict.PASS
        )
        self.acceptance = Acceptance("reviewer", "eval:7", "candidate:7", "retain", "C1", True)
        self.route = RouteObservation(
            "route-owner", "profile:direct", True, "local-review-evidence-only"
        )

    def result(self, **changes):
        return bind(
            self.question,
            self.evaluation,
            changes.get("acceptance", self.acceptance),
            changes.get("route", self.route),
        )

    def test_exact_accepted_evaluation_stays_evidence_only(self):
        result = self.result()
        self.assertEqual(result.decision, ReviewDecision.ACCEPTED_LOCAL_REVIEW_EVIDENCE)
        self.assertEqual(result.next_action, NextAction.NO_EXECUTION_AUTHORITY)
        self.assertEqual(result.claim_ceiling, "local-review-evidence-only")

    def test_pass_is_not_acceptance(self):
        self.assertEqual(
            self.result(acceptance=None).decision,
            ReviewDecision.HOLD_ACCEPTANCE_MISSING,
        )

    def test_same_candidate_c0_pass_cannot_satisfy_c1(self):
        evaluation = replace(self.evaluation, contract="C0")
        self.assertEqual(
            bind(self.question, evaluation, self.acceptance, self.route).decision,
            ReviewDecision.HOLD_EVALUATION_INAPPLICABLE,
        )

    def test_acceptance_must_bind_the_exact_evaluation_and_question(self):
        for acceptance in (
            replace(self.acceptance, evaluation_ref="eval:other"),
            replace(self.acceptance, contract="C0"),
            replace(self.acceptance, property="publish"),
            replace(self.acceptance, candidate="candidate:other"),
            replace(self.acceptance, accepted=False),
        ):
            self.assertEqual(
                self.result(acceptance=acceptance).decision,
                ReviewDecision.HOLD_ACCEPTANCE_INAPPLICABLE,
            )

    def test_worker_or_reviewer_owner_substitution_holds(self):
        result = bind(
            self.question, replace(self.evaluation, owner="worker"), self.acceptance, self.route
        )
        self.assertEqual(result.decision, ReviewDecision.HOLD_OWNER_MISMATCH)
        self.assertEqual(
            self.result(route=replace(self.route, owner="worker")).decision,
            ReviewDecision.HOLD_OWNER_MISMATCH,
        )
        self.assertEqual(
            self.result(acceptance=replace(self.acceptance, owner="worker")).decision,
            ReviewDecision.HOLD_OWNER_MISMATCH,
        )

    def test_historical_qualification_cannot_cover_a_changed_profile(self):
        for route in (
            replace(self.route, profile="profile:replacement"),
            replace(self.route, supports_review_use=False),
            replace(self.route, claim_ceiling=""),
        ):
            self.assertEqual(
                self.result(route=route).decision,
                ReviewDecision.HOLD_ROUTE_UNQUALIFIED,
            )

    def test_failed_or_other_property_evaluation_is_not_usable(self):
        for evaluation in (
            replace(self.evaluation, verdict=EvaluationVerdict.FAIL),
            replace(self.evaluation, property="publish"),
        ):
            self.assertEqual(
                bind(self.question, evaluation, self.acceptance, self.route).decision,
                ReviewDecision.HOLD_EVALUATION_INAPPLICABLE,
            )


if __name__ == "__main__":
    unittest.main()
