import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ANCHOR_PATH = DOCS / "prompt-contract-semantic-anchors-v1.json"
VECTOR_PATH = DOCS / "prompt-contract-canonicalization-vectors-v1.json"


def load_json_without_duplicate_keys(text):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(text, object_pairs_hook=unique_object)


class PromptContractSemanticAnchorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))

    def test_anchor_identity_and_required_keys(self):
        self.assertEqual(
            self.anchor["artifact_type"], "prompt_contract_semantic_anchors"
        )
        self.assertEqual(self.anchor["anchor_version"], "1.0.0")

        required_keys = {
            "artifact_classes",
            "authority_reference_requirements",
            "canonicalization",
            "compatibility_rules",
            "contract_receipt_boundary",
            "fresh_selection_rules",
            "invariants",
            "mandatory_fail_closed_triggers",
            "ownership_precedence",
            "reasoning_classes",
            "required_identity_names",
            "rendered_prompt_bytes",
            "replay_pinned_identities",
            "transport_invariants",
            "versioning_categories",
        }
        self.assertTrue(required_keys.issubset(self.anchor))

        required_identities = {
            "schema_version",
            "canonicalization_scheme",
            "canonicalization_version",
            "semantic_prompt_contract",
            "validation_profile",
            "validator_identity",
            "source_manifest",
            "authority_source_and_durable_lineage",
            "hydrator",
            "hydrated_context",
            "representation_adapter",
            "renderer",
            "rendered_prompt",
            "transport_policy",
            "transport_selection",
            "attempt",
            "checkpoint",
            "runtime_safety_policy_observation",
        }
        self.assertEqual(set(self.anchor["required_identity_names"]), required_identities)

    def test_prompt_contract_artifacts_have_no_duplicate_object_keys(self):
        for path in (ANCHOR_PATH, VECTOR_PATH):
            with self.subTest(path=path.name):
                load_json_without_duplicate_keys(path.read_text(encoding="utf-8"))

    def test_strict_loader_rejects_nested_duplicate_object_keys(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key: invariant"):
            load_json_without_duplicate_keys(
                '{"contract":{"invariant":true,"invariant":false}}'
            )

    def test_contract_receipt_boundary(self):
        boundary = self.anchor["contract_receipt_boundary"]
        self.assertEqual(
            boundary["contract_created_and_hashed_before"],
            ["source_hydration", "prompt_rendering"],
        )
        self.assertTrue(boundary["receipt_is_append_only"])
        self.assertTrue(boundary["receipt_references_contract_digest"])
        self.assertTrue(boundary["receipt_records_selected_and_derived_identities"])

        forbidden = {
            "contract_digest",
            "selected_source_manifest_digest",
            "hydrated_context_digest",
            "rendered_prompt_digest",
            "actual_transport_selection",
            "validation_results",
            "execution_results",
            "checkpoint_output",
            "runtime_safety_policy_identity",
        }
        self.assertEqual(set(boundary["contract_must_not_include"]), forbidden)

    def test_replay_authority_and_zero_effect_anchors(self):
        replay_required = {
            "semantic_contract_digest_and_version",
            "schema_identity",
            "canonicalization_identity",
            "source_bytes_and_references",
            "source_manifest_digest",
            "hydrated_context_digest",
            "hydrator_identity",
            "representation_adapter_identity",
            "renderer_identity",
            "validation_profile",
            "validator_identity",
            "rendered_prompt_bytes",
            "ordered_transport_policy",
            "attempt_and_checkpoint_lineage",
            "durable_state_or_receipt_lineage",
            "authority_source_reference_and_asserted_action",
        }
        self.assertEqual(set(self.anchor["replay_pinned_identities"]), replay_required)

        authority_required = {
            "approval_source_identity",
            "startup_state_or_durable_receipt_identity",
            "asserted_permitted_action",
            "authority_assertion_non_authoritative",
        }
        self.assertEqual(
            set(self.anchor["authority_reference_requirements"]), authority_required
        )

        invariants = self.anchor["invariants"]
        for name in (
            "no_authority",
            "no_orchestration",
            "no_state_transition",
            "prompt_text_is_not_authorization",
            "validation_is_not_authorization",
        ):
            self.assertIs(invariants[name], True)

    def test_reasoning_versioning_transport_and_fresh_selection(self):
        self.assertEqual(self.anchor["reasoning_classes"], ["light", "medium", "high"])

        categories = self.anchor["versioning_categories"]
        self.assertIn("authority", categories["major"])
        self.assertIn("replay", categories["major"])
        self.assertIn(
            "executor_visible_imperative_instruction_change", categories["minor"]
        )
        self.assertEqual(
            categories["patch"],
            ["strictly_non_behavioral_executor_invisible_change"],
        )

        fresh = self.anchor["fresh_selection_rules"]
        self.assertTrue(fresh["select_once_before_hydration"])
        self.assertTrue(fresh["no_input_moves_during_attempt"])
        self.assertIn("validator_identity", fresh["immutable_for_attempt"])

        transport = self.anchor["transport_invariants"]
        self.assertTrue(transport["fallback_changes_delivery_only"])
        self.assertEqual(
            transport["selection_rule"],
            "first_currently_available_permitted_route_in_declared_order",
        )
        self.assertIn("authority_handling", transport["must_preserve"])

    def test_anchor_excludes_repository_specific_operational_schema(self):
        serialized = json.dumps(self.anchor, ensure_ascii=False).lower()
        forbidden_fragments = (
            "knowledge-vault",
            "cak-62",
            "renderer_template",
            "workflow_state_schema",
            "receipt_schema",
            "repository_file_path",
            ".py",
        )
        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, serialized)

    def test_documentation_links_are_synchronized(self):
        required_references = {
            "prompts.md": "prompt-contracts.md",
            "start-here.md": "prompt-contracts.md",
            "source-first-retrieval.md": "prompt-contracts.md",
            "sparse-rehydration-and-source-grounding.md": "prompt-contracts.md",
            "orchestration-and-parallelism.md": "prompt-contracts.md",
            "review-packet.md": "prompt-contracts.md",
            "feature-lifecycle.md": "prompt-contracts.md",
            "tool-adapters/codex.md": "prompt-contracts.md",
            "tool-adapters/copilot.md": "prompt-contracts.md",
        }
        for relative_path, link in required_references.items():
            contents = (DOCS / relative_path).read_text(encoding="utf-8")
            self.assertIn(link, contents, relative_path)

        canonical_doc = (DOCS / "prompt-contracts.md").read_text(encoding="utf-8")
        self.assertIn(ANCHOR_PATH.name, canonical_doc)
        self.assertIn(VECTOR_PATH.name, canonical_doc)

    def test_local_links_in_affected_documentation_resolve(self):
        affected_documents = (
            "prompt-contracts.md",
            "prompts.md",
            "start-here.md",
            "source-first-retrieval.md",
            "sparse-rehydration-and-source-grounding.md",
            "orchestration-and-parallelism.md",
            "review-packet.md",
            "feature-lifecycle.md",
            "tool-adapters/codex.md",
            "tool-adapters/copilot.md",
        )
        link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
        for relative_path in affected_documents:
            document = DOCS / relative_path
            for target in link_pattern.findall(document.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_text = target.split("#", 1)[0]
                if not path_text:
                    continue
                resolved = (document.parent / path_text).resolve()
                self.assertTrue(resolved.exists(), f"{relative_path}: {target}")


class PromptContractCanonicalizationVectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vectors = json.loads(VECTOR_PATH.read_text(encoding="utf-8"))

    def test_vector_identity_and_structure(self):
        self.assertEqual(
            self.vectors["artifact_type"], "rfc8785_jcs_conformance_vectors"
        )
        self.assertEqual(self.vectors["vector_version"], "1.0.0")
        self.assertEqual(self.vectors["canonicalization_scheme"], "RFC8785-JCS")
        self.assertEqual(self.vectors["canonicalization_version"], 1)
        self.assertEqual(self.vectors["digest_algorithm"], "SHA-256")
        self.assertTrue(self.vectors["valid_vectors"])
        self.assertTrue(self.vectors["invalid_vectors"])

    def test_valid_vector_bytes_and_sha256(self):
        digest_pattern = re.compile(r"^sha256:[0-9a-f]{64}$")
        expected_digests = {
            "property-ordering": "sha256:43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777",
            "nested-objects-arrays": "sha256:ac589af80b931835a02a998a93425d38810e2581c35225b5003e255239789b98",
            "control-and-escaped-characters": "sha256:48ef3c76e1ba451bf80def3c316e3aad6056c531130c741c31dddb22a33fe907",
            "representative-unicode-no-normalization": "sha256:b5e31a432617868fc1276fceb4f9003be05cb4161be30e40bf5fddc822b75d12",
            "accepted-integer-and-floating-point-forms": "sha256:8573194d331e3ae7c5339b095461d7aa4c66157f85b59f2a2e63eb8b38110e3d",
            "empty-structures": "sha256:13b38aeab2e18a2c62de2945db9600720801b483e41936f5a154dbda7261be70",
        }
        for vector in self.vectors["valid_vectors"]:
            self.assertEqual(
                set(vector),
                {
                    "expected_canonical_hex",
                    "expected_sha256",
                    "input_json",
                    "name",
                },
            )
            canonical_bytes = bytes.fromhex(vector["expected_canonical_hex"])
            expected_digest = "sha256:" + hashlib.sha256(canonical_bytes).hexdigest()
            self.assertRegex(vector["expected_sha256"], digest_pattern)
            self.assertEqual(vector["expected_sha256"], expected_digest)
            self.assertEqual(
                vector["expected_sha256"], expected_digests[vector["name"]]
            )

            input_value = json.loads(vector["input_json"])
            canonical_value = json.loads(canonical_bytes.decode("utf-8"))
            self.assertEqual(input_value, canonical_value, vector["name"])
            self.assertFalse(canonical_bytes.startswith(b"\xef\xbb\xbf"))

    def test_valid_vector_coverage(self):
        names = {vector["name"] for vector in self.vectors["valid_vectors"]}
        required = {
            "property-ordering",
            "nested-objects-arrays",
            "control-and-escaped-characters",
            "representative-unicode-no-normalization",
            "accepted-integer-and-floating-point-forms",
            "empty-structures",
        }
        self.assertEqual(names, required)

    def test_invalid_vector_classifications(self):
        classifications = {
            vector["classification"] for vector in self.vectors["invalid_vectors"]
        }
        required = {
            "invalid_unicode_unpaired_surrogate",
            "non_finite_number",
            "incompatible_numeric_value",
            "unknown_canonicalization_major",
            "non_i_json_duplicate_property",
            "malformed_json",
        }
        self.assertEqual(classifications, required)

        for vector in self.vectors["invalid_vectors"]:
            self.assertIn("name", vector)
            self.assertIn("input_json", vector)
            self.assertIn("classification", vector)


if __name__ == "__main__":
    unittest.main()
