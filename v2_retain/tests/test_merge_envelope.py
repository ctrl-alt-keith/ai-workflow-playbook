from dataclasses import replace
import unittest

from v2_retain.merge_envelope import (
    Action, AttemptState, Authority, Candidate, Conditions, Decision, Envelope,
    retry_eligibility,
)


class MergeEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.candidate = Candidate(456, "approved-head", 7)
        self.action = Action()
        self.authority = Authority(self.action, self.candidate)
        self.envelope = Envelope(self.action, self.candidate, AttemptState.KNOWN_NO_EFFECT)

    def decide(self, **changes):
        envelope = changes.pop("envelope", self.envelope)
        observed = changes.pop("observed", self.candidate)
        action = changes.pop("action", self.action)
        conditions = changes.pop("conditions", Conditions())
        authority = changes.pop("authority", self.authority)
        self.assertEqual(changes, {})
        return retry_eligibility(envelope, observed, action, conditions, authority)

    def test_adversarial_matrix(self):
        changed = Candidate(456, "changed-head", 8)
        returned = Candidate(456, "approved-head", 9)
        cases = (
            ("recent valid retry", {}, Decision.RETRY_ELIGIBLE,
             "known-no-effect with fresh conditions"),
            ("outcome unknown holds", {"envelope": replace(self.envelope, attempt=AttemptState.OUTCOME_UNKNOWN)},
             Decision.HOLD_OUTCOME_UNKNOWN, "may have reached GitHub"),
            ("effected does not replay", {"envelope": replace(self.envelope, attempt=AttemptState.EFFECTED)},
             Decision.STOP_EFFECTED, "already effected"),
            ("first failure is not universally retryable", {"envelope": replace(self.envelope, attempt=AttemptState.NOT_SUBMITTED)},
             Decision.STOP_ATTEMPT_NOT_PROVEN_NO_EFFECT, "proven known-no-effect"),
            ("head change invalidates", {"observed": changed}, Decision.STOP_EPOCH_INVALIDATED,
             "previously divergent"),
            ("head return cannot resurrect", {"envelope": self.envelope.observe_candidate(changed), "observed": returned},
             Decision.STOP_EPOCH_INVALIDATED, "previously divergent"),
            ("stale checks stop", {"conditions": Conditions(checks="stale")}, Decision.STOP_CONDITIONS_STALE, "checks"),
            ("failed readiness stops", {"conditions": Conditions(readiness="failed")}, Decision.STOP_CONDITIONS_FAILED, "readiness"),
            ("failed mergeability stops", {"conditions": Conditions(mergeability="failed")}, Decision.STOP_CONDITIONS_FAILED, "mergeability"),
            ("failed policy stops", {"conditions": Conditions(repository_policy="failed")}, Decision.STOP_CONDITIONS_FAILED, "repository-policy"),
            ("green checks do not create authority", {"authority": None}, Decision.STOP_AUTHORITY_MISSING,
             "do not create authority"),
            ("worker readiness does not create authority", {"authority": None}, Decision.STOP_AUTHORITY_MISSING,
             "do not create authority"),
            ("merge capability does not create permission", {"authority": None}, Decision.STOP_AUTHORITY_MISSING,
             "do not create authority"),
            ("status query does not create authority", {"authority": None}, Decision.STOP_AUTHORITY_MISSING,
             "do not create authority"),
            ("same diff does not reuse authority", {"observed": changed}, Decision.STOP_EPOCH_INVALIDATED,
             "previously divergent"),
            ("earlier approval misses changed head", {"observed": changed}, Decision.STOP_EPOCH_INVALIDATED,
             "previously divergent"),
            ("revoked authority stops", {"authority": replace(self.authority, current=False)}, Decision.STOP_AUTHORITY_NOT_CURRENT,
             "revoked or expired"),
            ("changed merge method blocks", {"action": Action(method="merge")}, Decision.STOP_ACTION_MISMATCH,
             "method, destination, or route claim changed"),
            ("changed route claim blocks", {"action": Action(route_claim="alternate-route")}, Decision.STOP_ACTION_MISMATCH,
             "method, destination, or route claim changed"),
            ("uncorrelated output cannot prove success", {"envelope": replace(self.envelope, attempt=AttemptState.OUTCOME_UNKNOWN)},
             Decision.HOLD_OUTCOME_UNKNOWN, "may have reached GitHub"),
        )
        for name, arguments, decision, observation in cases:
            with self.subTest(name=name):
                result = self.decide(**arguments)
                self.assertEqual(result.decision, decision)
                self.assertIn(observation, result.observation)

    def test_renewed_authority_cannot_reuse_invalidated_envelope(self):
        changed = Candidate(456, "changed-head", 8)
        invalidated = self.envelope.observe_candidate(changed)
        renewed = Authority(self.action, changed)
        result = self.decide(envelope=invalidated, observed=changed, authority=renewed)
        self.assertEqual(result.decision, Decision.STOP_EPOCH_INVALIDATED)
        self.assertIn("previously divergent", result.observation)

    def test_authority_scope_is_exact(self):
        other = Authority(self.action, Candidate(456, "other-head", 7))
        result = self.decide(authority=other)
        self.assertEqual(result.decision, Decision.STOP_AUTHORITY_SCOPE_MISMATCH)
        self.assertIn("action and candidate", result.observation)
