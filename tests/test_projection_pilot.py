"""Exercise the experimental validator/selector, not a second test-only model."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("projection_pilot", ROOT / "scripts/projection_pilot.py")
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


def fixture():
    raw = b"# Fixture\n\nRequired clause.\n\nSupporting example.\n"
    section, blocks = pilot.blocks(raw, "# Fixture")
    source = {"id": "src", "path": "source.md", "sha256": pilot.digest(raw), "heading": "# Fixture",
              "section_sha256": pilot.digest(section.encode()),
              "coverage": [{"sha256": pilot.digest(b.encode()), "lines": [i * 2 + 1, i * 2 + 1],
                            "class": "normative" if i == 1 else "supporting", "rules": ["r"] if i == 1 else [],
                            "canonical_reads": []} for i, b in enumerate(blocks)]}
    terms = [{"id": "needed", "type": "boolean", "values": [False, True], "role": "fact",
              "source": "src", "definition": "Externally established need."},
             {"id": "mode", "type": "enum", "values": ["read", "write"], "role": "effect",
              "source": "src", "definition": "Candidate required behavior, not permission."}]
    when = {"eq": ["needed", True]}
    rule = {"id": "r", "kind": "requirement", "status": "candidate", "superseded_by": None,
            "source": "src", "owner": {"source": "src", "question": "action"}, "when": when,
            "consequence": {"kind": "obligation", "term": "mode", "value": "read", "meaning": "Read required source."},
            "persistence": {"starts": "Need", "retains": "Required read", "terminates_when": {"not": when}},
            "failure": {"mode": "defined", "when": when, "operation": "conclusion", "response": "Stop missing-source conclusion."},
            "dependencies": [], "validation": ["fixture"], "execution_qualified": False,
            "interpretation": "Test contract.", "supporting_sources": []}
    return {"schema_version": 1, "status": "experimental", "complete": False, "sources": [source],
            "terms": terms, "rules": [rule], "evaluation_cases": [{"id": "fixture", "scenario": "Required source",
            "expected": ["Report read obligation"], "forbidden": ["Grant permission"], "sources": ["src"]}],
            "consumer": {"id": "design", "mode": "read_only_design",
            "schema_version": 1, "live_consumption": False, "capabilities": sorted(pilot.CAPABILITIES),
            "canonical_reads": ["src"]}}, raw


class ProjectionContracts(unittest.TestCase):
    def setUp(self):
        self.model, self.raw = fixture()

    def second(self, **updates):
        rule = deepcopy(self.model["rules"][0])
        rule.update(id="r2", **updates)
        self.model["rules"].append(rule)
        return rule

    def invalid(self, message):
        with self.assertRaisesRegex(pilot.ContractError, message):
            pilot.validate(self.model)

    def test_three_valued_truth_tables_and_presence(self):
        true = {"eq": ["a", True]}
        false = {"eq": ["b", True]}
        unknown = {"eq": ["c", True]}
        facts = {"a": True, "b": False}
        for expr, expected in [({"all": [true, unknown]}, None), ({"all": [false, unknown]}, False),
                               ({"any": [true, unknown]}, True), ({"any": [false, unknown]}, None),
                               ({"not": unknown}, None), ({"present": "c"}, None),
                               ({"present": "b"}, True), ({"in": ["a", [False, True]]}, True)]:
            self.assertIs(pilot.evaluate(expr, facts), expected)
        self.assertIs(pilot.evaluate({"present": "a"}, {"a": None}), False)

    def test_unknown_never_drops_potentially_applicable_rule_or_emits_permission(self):
        result = pilot.select(self.model, {})
        self.assertEqual([row["rule"]["id"] for row in result["rules"]], ["r"])
        self.assertIsNone(result["rules"][0]["activation"])
        self.assertEqual(result["unknown_facts"], ["needed"])
        self.assertEqual(result["permission"], "not_evaluated")
        self.assertEqual(pilot.select(self.model, {"needed": False})["rules"], [])

    def test_typed_conditions_validate_unreachable_branches(self):
        cases = [({"eq": ["missing", True]}, "undefined fact"),
                 ({"eq": ["needed", 1]}, "typed operand"),
                 ({"eval": "True"}, "unsupported condition"),
                 ({"all": [{"eq": ["needed", False]}, {"in": ["needed", ["bad"]]}]}, "typed operand")]
        for expr, message in cases:
            with self.subTest(expr=expr):
                self.model["rules"][0]["when"] = expr
                self.invalid(message)
        with self.assertRaises(pilot.ContractError):
            pilot.select(fixture()[0], {"needed": 1})

    def test_references_kinds_and_duplicate_ids(self):
        for mutation, message in [
            (lambda d: d["rules"].append(deepcopy(d["rules"][0])), "duplicate ID"),
            (lambda d: d["rules"][0].update(kind="permission"), "unknown rule kind"),
            (lambda d: d["rules"][0].update(source="missing"), "missing source"),
            (lambda d: d["rules"][0]["consequence"].update(term="missing"), "undefined or mistyped"),
            (lambda d: d["rules"][0]["dependencies"].append({"relation": "requires", "target": "missing"}), "invalid dependency target"),
            (lambda d: d["terms"][0].update(source="missing"), "undefined term owner"),
            (lambda d: d["consumer"]["canonical_reads"].append("missing"), "missing consumer")]:
            with self.subTest(message=message):
                self.model = fixture()[0]
                mutation(self.model)
                self.invalid(message)

    def test_mechanically_impossible_predicate(self):
        self.model["rules"][0]["when"] = {"all": [{"eq": ["needed", True]}, {"not": {"in": ["needed", [True]]}}]}
        self.invalid("impossible predicate")

    def test_overlap_requires_precedence_covering_entire_overlap(self):
        second = self.second()
        second["consequence"]["value"] = "write"
        self.invalid("incompatible overlapping")
        edge = {"relation": "overrides", "target": "r", "question": "action", "source": "src",
                "justification": "Source-backed narrower requirement.", "when": {"eq": ["needed", False]}}
        second["dependencies"] = [edge]
        self.invalid("incompatible overlapping")
        edge["when"] = {"eq": ["needed", True]}
        pilot.validate(self.model)
        edge["question"] = "another question"
        self.invalid("outside its bounded question")

    def test_disjoint_effects_and_duplicate_diagnostics(self):
        second = self.second(when={"eq": ["needed", False]})
        second["consequence"]["value"] = "write"
        pilot.validate(self.model)
        second["consequence"]["value"] = "read"
        warnings = pilot.validate(self.model)
        self.assertEqual(warnings[0]["diagnostic"], "possible_semantic_duplicate_never_auto_merge")
        self.assertEqual(len(self.model["rules"]), 2)

    def test_prerequisite_cycles_include_mixed_before_and_requires_but_not_references(self):
        second = self.second()
        first = self.model["rules"][0]
        first["dependencies"] = [{"relation": "before", "target": "r2"}]
        second["dependencies"] = [{"relation": "before", "target": "r"}]
        self.invalid("prerequisite/before cycle")
        first["dependencies"][0]["relation"] = "requires"
        second["dependencies"][0]["relation"] = "requires"
        self.invalid("prerequisite/before cycle")
        first["dependencies"][0]["relation"] = "refers_to"
        second["dependencies"][0]["relation"] = "refers_to"
        pilot.validate(self.model)

    def test_precedence_cycles_even_when_effects_match(self):
        second = self.second()
        for rule, target in [(self.model["rules"][0], "r2"), (second, "r")]:
            rule["dependencies"] = [{"relation": "overrides", "target": target, "question": "action",
                                     "source": "src", "justification": "Fixture", "when": {"eq": ["needed", True]}}]
        self.invalid("precedence cycle")

    def test_failure_inheritance_qualification_and_cycles(self):
        second = self.second()
        first = self.model["rules"][0]
        first.update(execution_qualified=True, failure={"mode": "inherited", "from": "r2", "operation": "conclusion"})
        pilot.validate(self.model)
        second["failure"] = {"mode": "unresolved", "reason": "Source judgment not resolved"}
        self.invalid("lacks resolved required failure")
        first["execution_qualified"] = False
        self.assertTrue(pilot.validate(self.model))
        second["failure"] = {"mode": "inherited", "from": "r", "operation": "conclusion"}
        self.invalid("failure inheritance cycle")

    def test_dependency_closure_retains_inactive_prerequisite_without_claiming_activation(self):
        second = self.second(when={"eq": ["needed", False]})
        self.model["rules"][0]["dependencies"] = [{"relation": "requires", "target": second["id"]}]
        result = pilot.select(self.model, {"needed": True})
        self.assertEqual(len(result["rules"]), 2)
        self.assertIs(result["rules"][1]["activation"], False)
        self.assertIn("requires", result["rules"][1]["selection"][0])

    def test_failure_inheritance_cannot_leak_retired_rule_into_canonical_reads(self):
        self.second(status="retired")
        self.model["rules"][0]["failure"] = {"mode": "inherited", "from": "r2", "operation": "conclusion"}
        with self.assertRaisesRegex(pilot.ContractError, "failure inheritance from retired ID"):
            pilot.select(self.model, {"needed": True})

    def test_retirement_never_reassigns_ids_or_silently_redirects_dependencies(self):
        second = self.second()
        self.model["rules"][0].update(status="retired", superseded_by="r2")
        self.assertEqual([r["rule"]["id"] for r in pilot.select(self.model, {})["rules"]], ["r2"])
        second["dependencies"] = [{"relation": "requires", "target": "r"}]
        self.invalid("dependency on retired")

    def test_authority_rule_only_records_external_checks(self):
        rule = self.model["rules"][0]
        rule["kind"] = "authority"
        self.invalid("authority must identify")
        rule["consequence"]["kind"] = "authority_source"
        rule["authority"] = {"source": "src", "checks": ["Read live human direction"]}
        self.assertEqual(pilot.select(self.model, {"needed": True})["permission"], "not_evaluated")

    def test_consumer_capabilities_and_false_completeness(self):
        self.model["consumer"]["capabilities"].remove("eq")
        self.invalid("lacks required capabilities")
        self.model = fixture()[0]
        self.model["complete"] = True
        self.invalid("cannot claim complete")
        self.model = fixture()[0]
        self.model["consumer"]["live_consumption"] = True
        self.invalid("unsupported consumer")

    def test_coverage_detects_added_changed_removed_and_unprojected_blocks(self):
        with patch.object(pilot, "source_bytes", return_value=self.raw):
            pilot.validate(self.model, ROOT)
        for changed in [self.raw.replace(b"Required clause.", b"Changed clause."),
                        self.raw + b"\nNew requirement outside old spans.\n",
                        self.raw.replace(b"Supporting example.\n", b""),
                        self.raw.replace(b"Supporting example.", b"Required new qualifier.")]:
            with self.subTest(changed=changed), patch.object(pilot, "source_bytes", return_value=changed):
                changes = pilot.coverage_diff(self.model, ROOT)
                self.assertIn("coverage_drift", [c["change"] for c in changes])
                with self.assertRaisesRegex(pilot.ContractError, "source-binding drift"):
                    pilot.validate(self.model, ROOT)
        block = self.model["sources"][0]["coverage"][1]
        block["rules"] = []
        self.invalid("normative clause omitted")
        block["canonical_reads"] = ["src"]
        pilot.validate(self.model)
        self.assertIn("src", pilot.select(self.model, {"needed": False})["canonical_reads"])

    def test_supporting_text_cannot_become_a_rule_and_regeneration_is_deterministic(self):
        initial = deepcopy(self.model)
        self.assertEqual(pilot.canonical(pilot.select(self.model, {})), pilot.canonical(pilot.select(self.model, {})))
        self.assertEqual(initial, self.model)
        block = self.model["sources"][0]["coverage"][2]
        block["rules"] = ["r"]
        self.invalid("supporting/unresolved text")


class EightUnitPilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads((ROOT / "docs/experimental-projection/pilot.json").read_bytes())

    def test_reviewed_input_structure_and_exact_unit_set(self):
        # Source freshness is deliberately opt-in; normal prose edits do not inherit a new gate.
        pilot.validate(self.model)
        self.assertEqual(set(self.model["pilot_units"]), {
            "startup-floor", "conditional-activation", "mode-persistence", "retrieval-triggers",
            "claim-verification", "retrieval-recovery", "interaction-mode", "action-latch"})
        self.assertEqual({r["id"] for r in self.model["rules"]}, {"pb." + u for u in self.model["pilot_units"]})

    def test_bootstrap_recovery_keeps_qualified_alternate_source_path(self):
        # Observed rejection is a transport fact; source_available stays true after a qualified connector succeeds.
        result = pilot.select(self.model, {"repository_work": True, "retrieval_missed": True,
                              "source_available": True, "mandatory_trigger": True, "verification_complete": False})
        recovery = next(row["rule"] for row in result["rules"] if row["rule"]["id"] == "pb.retrieval-recovery")
        self.assertIs(pilot.evaluate(recovery["failure"]["when"], {"source_available": True}), False)
        self.assertIn("src.codex", result["canonical_reads"])
        self.assertIn("src.retrieval", result["canonical_reads"])
        self.assertIs(pilot.evaluate(recovery["failure"]["when"], {"source_available": False}), True)

    def test_continuation_persistence_and_steering_are_reported_not_applied(self):
        facts = {"repository_work": True, "startup_succeeded": True, "repository_changed": False,
                 "leaves_repository_work": False, "human_style_override": False, "material_change": False,
                 "human_direction_changed": True, "interaction_mode": "review_audit", "pending_incompatible": True}
        before = deepcopy(facts)
        result = pilot.select(self.model, facts)
        rows = {r["rule"]["id"]: r["rule"] for r in result["rules"]}
        self.assertIs(pilot.evaluate(rows["pb.mode-persistence"]["persistence"]["terminates_when"], facts), False)
        self.assertIs(pilot.evaluate(rows["pb.action-latch"]["failure"]["when"], facts), True)
        self.assertEqual(before, facts)


if __name__ == "__main__":
    unittest.main()
