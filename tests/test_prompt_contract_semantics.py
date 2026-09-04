import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ANCHOR_PATH = DOCS / "prompt-contract-semantic-anchors-v4.json"
HISTORICAL_V3_ANCHOR_PATH = DOCS / "prompt-contract-semantic-anchors-v3.json"
HISTORICAL_V2_ANCHOR_PATH = DOCS / "prompt-contract-semantic-anchors-v2.json"
LEGACY_V1_ANCHOR_PATH = DOCS / "prompt-contract-semantic-anchors-v1.json"
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
        cls.historical_v3_anchor = json.loads(
            HISTORICAL_V3_ANCHOR_PATH.read_text(encoding="utf-8")
        )
        cls.historical_v2_anchor = json.loads(
            HISTORICAL_V2_ANCHOR_PATH.read_text(encoding="utf-8")
        )
        cls.legacy_v1_anchor = json.loads(
            LEGACY_V1_ANCHOR_PATH.read_text(encoding="utf-8")
        )

    def test_anchor_identity_and_required_keys(self):
        self.assertEqual(
            self.anchor["artifact_type"], "prompt_contract_semantic_anchors"
        )
        self.assertEqual(self.anchor["anchor_version"], "4.0.0")
        self.assertEqual(self.anchor["compatibility_major"], 4)

        self.assertEqual(self.historical_v3_anchor["anchor_version"], "3.0.0")
        self.assertEqual(self.historical_v3_anchor["compatibility_major"], 3)
        historical_v3_bytes = HISTORICAL_V3_ANCHOR_PATH.read_bytes()
        self.assertEqual(len(historical_v3_bytes), 12604)
        self.assertEqual(
            hashlib.sha256(historical_v3_bytes).hexdigest(),
            "b448601611b63fba505640b917f27e23c2d7fb61816ebd32ffd7a305dcb709c7",
        )

        self.assertEqual(self.historical_v2_anchor["anchor_version"], "2.0.0")
        self.assertEqual(self.historical_v2_anchor["compatibility_major"], 2)
        historical_v2_bytes = HISTORICAL_V2_ANCHOR_PATH.read_bytes()
        self.assertEqual(len(historical_v2_bytes), 11593)
        self.assertEqual(
            hashlib.sha256(historical_v2_bytes).hexdigest(),
            "71abb264847a2c950dfaccc9e438d8db7cb0dab14a1424552688a09ba03fb4f5",
        )
        historical_v2_capture = self.historical_v2_anchor[
            "issue_owned_durable_handoff_profile"
        ]["durable_capture"]
        self.assertIs(historical_v2_capture["raw_provider_readback_required"], True)
        self.assertNotIn(
            "integrity_verification",
            self.historical_v2_anchor["issue_owned_durable_handoff_profile"],
        )

        self.assertEqual(self.legacy_v1_anchor["anchor_version"], "1.1.0")
        legacy_v1_bytes = LEGACY_V1_ANCHOR_PATH.read_bytes()
        self.assertEqual(len(legacy_v1_bytes), 8662)
        self.assertEqual(
            hashlib.sha256(legacy_v1_bytes).hexdigest(),
            "e0ee48d832e911c2b88caf3e5fc82bf826ac0d4a2315b19302d88e20ffbd488c",
        )
        legacy_capture = self.legacy_v1_anchor[
            "issue_owned_durable_handoff_profile"
        ]["durable_capture"]
        self.assertIs(legacy_capture["provider_revision_required"], True)
        self.assertNotIn(
            "provider_revision_recorded_when_available", legacy_capture
        )

        supersession = self.anchor["supersession"]
        self.assertEqual(
            supersession["supersedes_for_new_compatible_selection"],
            HISTORICAL_V3_ANCHOR_PATH.name,
        )
        self.assertIs(
            supersession["historical_consumers_remain_pinned_to_recorded_major"],
            True,
        )
        self.assertIs(supersession["implicit_major_adoption_prohibited"], True)

        historical_v3_supersession = self.historical_v3_anchor["supersession"]
        self.assertEqual(
            historical_v3_supersession[
                "supersedes_for_new_compatible_selection"
            ],
            HISTORICAL_V2_ANCHOR_PATH.name,
        )
        self.assertIs(
            historical_v3_supersession[
                "historical_consumers_remain_pinned_to_recorded_major"
            ],
            True,
        )
        self.assertIs(
            historical_v3_supersession["implicit_major_adoption_prohibited"],
            True,
        )

        required_keys = {
            "artifact_classes",
            "authority_reference_requirements",
            "canonicalization",
            "compatibility_rules",
            "contract_receipt_boundary",
            "fresh_selection_rules",
            "invariants",
            "issue_owned_durable_handoff_profile",
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
        for path in (
            LEGACY_V1_ANCHOR_PATH,
            HISTORICAL_V2_ANCHOR_PATH,
            HISTORICAL_V3_ANCHOR_PATH,
            ANCHOR_PATH,
            VECTOR_PATH,
        ):
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

    def test_issue_owned_durable_handoff_profile(self):
        profile = self.anchor["issue_owned_durable_handoff_profile"]
        self.assertEqual(len(profile["admission_conditions"]), 6)
        self.assertEqual(profile["route"], "exact_airtable_record")
        self.assertEqual(
            profile["qualification"],
            "small_canonical_text_for_chatgpt_or_claude",
        )
        self.assertEqual(
            profile["record_fields"],
            [
                "Handoff Key",
                "Payload",
                "Payload Bytes",
                "SHA-256",
                "Producer",
            ],
        )
        self.assertEqual(
            set(profile["evidence_identities"]),
            {
                "rendered_prompt",
                "airtable_record",
                "external_handoff_envelope",
                "producing_receipt",
                "delivery_operation",
                "executor_attempt",
                "attempt_receipt",
                "executor_output",
                "human_disposition",
            },
        )
        attempt = profile["record_attempt"]
        for key in (
            "one_new_record_per_attempt",
            "frozen_record_never_updated",
            "correction_creates_new_key_and_record",
            "predecessor_lineage_external",
            "key_uniqueness_not_assumed",
            "record_immutability_not_assumed",
        ):
            self.assertTrue(attempt[key])

        envelope_fields = set(profile["external_envelope_fields"])
        self.assertEqual(
            envelope_fields,
            {
                "base_id",
                "table_id",
                "record_id",
                "expected_handoff_key",
                "utf8_no_bom_lf_and_final_newline_rule",
                "expected_payload_bytes",
                "expected_sha256",
                "producer_executor_and_attempt_identity",
                "predecessor_identity_when_applicable",
            },
        )

        verification = profile["consumer_verification"]
        for key in (
            "retrieve_by_exact_record_id",
            "fuzzy_or_key_search_as_retrieval_prohibited",
            "exactly_one_result_required",
            "expected_key_and_field_set_required",
            "payload_reencoded_under_declared_text_rules",
            "byte_length_and_sha256_independently_recomputed",
            "recomputed_stored_and_external_values_must_agree",
            "missing_multiple_stale_transformed_truncated_or_mismatched_fails_closed",
        ):
            self.assertTrue(verification[key])

        attribution = profile["attribution"]
        self.assertTrue(attribution["shared_airtable_user_is_not_executor_identity"])
        self.assertTrue(attribution["producer_field_is_declared_metadata"])
        self.assertTrue(
            attribution["executor_attribution_remains_external_attempt_evidence"]
        )
        self.assertEqual(
            set(profile["prohibited_normal_route_mechanics"]),
            {
                "file_provider_fallback",
                "file_preview",
                "download_link",
                "attempt_local_prompt_download",
                "mutable_record_update",
                "copy_paste_as_exact_identity",
            },
        )

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

        self.assertIn(
            "compatibility_major_exact_match", self.anchor["compatibility_rules"]
        )
        self.assertIn(
            "compatibility_major_mismatch",
            self.anchor["mandatory_fail_closed_triggers"],
        )

        transport = self.anchor["transport_invariants"]
        self.assertEqual(
            transport["qualifying_small_canonical_text_route"],
            "airtable_exact_record",
        )
        self.assertTrue(transport["file_provider_is_not_normal_route_or_fallback"])
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
            "tool-adapters/claude.md": "prompt-contracts.md",
            "tool-adapters/copilot.md": "prompt-contracts.md",
            "tool-adapters/chatgpt.md": "prompt-contracts.md",
        }
        for relative_path, link in required_references.items():
            contents = (DOCS / relative_path).read_text(encoding="utf-8")
            self.assertIn(link, contents, relative_path)

        canonical_doc = (DOCS / "prompt-contracts.md").read_text(encoding="utf-8")
        self.assertIn(ANCHOR_PATH.name, canonical_doc)
        self.assertIn(HISTORICAL_V3_ANCHOR_PATH.name, canonical_doc)
        self.assertIn(HISTORICAL_V2_ANCHOR_PATH.name, canonical_doc)
        self.assertIn(LEGACY_V1_ANCHOR_PATH.name, canonical_doc)
        self.assertIn(VECTOR_PATH.name, canonical_doc)

        for relative_path in ("prompts.md", "tool-adapters/codex.md"):
            contents = (DOCS / relative_path).read_text(encoding="utf-8")
            self.assertIn(ANCHOR_PATH.name, contents, relative_path)

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
