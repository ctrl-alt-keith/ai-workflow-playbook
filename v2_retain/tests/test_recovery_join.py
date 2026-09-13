import unittest
from dataclasses import replace

from v2_retain.recovery_join import (
    AuthorityObservation, Breadcrumb, DecisionRecord, EffectObservation,
    EffectState, NextAction, RecoveryDecision, RepositoryObservation,
    RouteObservation, Verdict, recover,
)


class RecoveryJoinTests(unittest.TestCase):
    def setUp(self):
        self.breadcrumb = Breadcrumb(
            decision_ref="decision-458", decision_owner="github-decision",
            repository_owner="github-repository", authority_owner="human-authority",
            effect_owner="github-effect", route_owner="local-profile",
            candidate="9271a57", action="squash-merge", property="merge-authorization",
            contract="merge-envelope-v1",
        )
        self.record = DecisionRecord("decision-458", "github-decision", "9271a57", "squash-merge",
                                     "merge-authorization", "merge-envelope-v1", Verdict.APPROVED)
        self.repository = RepositoryObservation("github-repository", candidate="9271a57")
        self.authority = AuthorityObservation("human-authority", current=True, candidate="9271a57", action="squash-merge")
        self.effect = EffectObservation("github-effect", state=EffectState.KNOWN_NO_EFFECT)
        self.route = RouteObservation("local-profile", supports_action=True, claim_ceiling="local-model-only")

    def decide(self, **changes):
        values = {
            "record": self.record, "repository": self.repository, "authority": self.authority,
            "effect": self.effect, "route": self.route,
        }
        values.update(changes)
        return recover(self.breadcrumb, **values)

    def test_compact_breadcrumb_joins_current_owners(self):
        result = self.decide()
        self.assertEqual(result.decision, RecoveryDecision.RECOVERED_CURRENT_BOUNDED_AUTHORITY)
        self.assertEqual(result.next_action, NextAction.LOCAL_BOUNDED_ACTION_ONLY)
        self.assertEqual(result.claim_ceiling, "local-model-only")

    def test_approved_summary_and_worker_reconstruction_are_not_authority(self):
        result = self.decide(authority=replace(self.authority, current=False))
        self.assertEqual(result.decision, RecoveryDecision.RECOVERED_NO_CURRENT_AUTHORITY)
        self.assertEqual(result.next_action, NextAction.HOLD)

    def test_matching_candidate_does_not_resurrect_stale_authority(self):
        result = self.decide(authority=replace(self.authority, current=False))
        self.assertEqual(result.decision, RecoveryDecision.RECOVERED_NO_CURRENT_AUTHORITY)

    def test_durable_copy_is_not_owner_for_mutable_repository_fact(self):
        result = self.decide(repository=replace(self.repository, owner="dropbox-copy"))
        self.assertEqual(result.decision, RecoveryDecision.HOLD_OWNER_MISMATCH)
        self.assertIn("non-owning", result.observation)

    def test_current_owner_beats_stale_durable_approval(self):
        result = self.decide(repository=replace(self.repository, candidate="7105604"))
        self.assertEqual(result.decision, RecoveryDecision.HOLD_CURRENT_CANDIDATE_DIVERGED)

    def test_old_merge_instruction_cannot_be_unbounded_standing_authority(self):
        result = self.decide(authority=replace(self.authority, action="merge-anything"))
        self.assertEqual(result.decision, RecoveryDecision.RECOVERED_NO_CURRENT_AUTHORITY)

    def test_unknown_effect_holds_even_with_current_authority(self):
        result = self.decide(effect=replace(self.effect, state=EffectState.UNKNOWN))
        self.assertEqual(result.decision, RecoveryDecision.HOLD_EFFECT_UNKNOWN)

    def test_observed_effect_stops_the_bounded_action(self):
        result = self.decide(effect=replace(self.effect, state=EffectState.EFFECTED))
        self.assertEqual(result.decision, RecoveryDecision.STOP_EFFECT_ALREADY_OBSERVED)

    def test_required_owner_unavailable_holds_only_the_affected_conclusion(self):
        result = self.decide(route=replace(self.route, available=False))
        self.assertEqual(result.decision, RecoveryDecision.HOLD_REQUIRED_OWNER_UNAVAILABLE)
        self.assertIn("route owner", result.observation)

    def test_exact_decision_applicability_and_route_capability_are_required(self):
        decision = self.decide(record=replace(self.record, contract="other-contract"))
        route = self.decide(route=replace(self.route, supports_action=False))
        ceiling = self.decide(route=replace(self.route, claim_ceiling=""))
        self.assertEqual(decision.decision, RecoveryDecision.HOLD_DECISION_INAPPLICABLE)
        self.assertEqual(route.decision, RecoveryDecision.HOLD_ROUTE_UNQUALIFIED)
        self.assertEqual(ceiling.decision, RecoveryDecision.HOLD_ROUTE_UNQUALIFIED)
