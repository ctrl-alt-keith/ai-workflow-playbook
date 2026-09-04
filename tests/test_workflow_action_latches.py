from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPO_READINESS = ROOT / "docs" / "repo-readiness.md"
PROMPTS = ROOT / "docs" / "prompts.md"
REVIEW_PACKET = ROOT / "docs" / "review-packet.md"
CHATGPT_ADAPTER = ROOT / "docs" / "tool-adapters" / "chatgpt.md"


class Mode(str, Enum):
    PROMPT_AUTHORING = "orchestration/prompt-authoring"
    REVIEW_AUDIT = "review/audit"


class PromptState(str, Enum):
    DESIGN = "PROMPT_DESIGN"
    FROZEN = "PROMPT_FROZEN"
    DROPBOX_TRANSPORT_ONLY = "DROPBOX_TRANSPORT_ONLY"
    HANDED_OFF = "HANDOFF_EMITTED"
    BLOCKED = "BLOCKED"


class RuntimePrerequisite(str, Enum):
    CONNECTOR_MUTATION_CONFIRMATION = "connector-mutation-confirmation"


class Action(str, Enum):
    READ_ISSUE = "read-issue"
    READ_REPOSITORY = "read-repository"
    READ_GITHUB_PR = "read-github-pr"
    HYDRATE_SOURCES = "hydrate-sources"
    FREEZE_PROMPT = "freeze-prompt"
    EDIT_PROMPT = "edit-prompt"
    DISCOVER_CONNECTOR = "discover-connector"
    REQUEST_PERMISSION = "request-permission"
    CREATE_ISSUE_FOLDER = "create-issue-folder"
    CREATE_PROMPT_FILE = "create-prompt-file"
    VERIFY_PROMPT = "verify-prompt"
    PREVIEW_PROMPT = "preview-prompt"
    MINT_DOWNLOAD_LINK = "mint-download-link"
    EMIT_HANDOFF = "emit-handoff"
    RENDER_INLINE = "render-inline"
    GITHUB_WRITE = "github-write"
    LINEAR_WRITE = "linear-write"
    REPOSITORY_MUTATION = "repository-mutation"
    PROVIDER_CONFIGURATION = "provider-configuration"
    AUTHENTICATION_MUTATION = "authentication-mutation"
    DOWNSTREAM_EXECUTION = "downstream-execution"
    CLONE = "clone"
    CHECKOUT = "checkout"
    CREATE_WORKTREE = "create-worktree"
    RUN_LOCAL_TESTS = "run-local-tests"
    CREATE_TEMP_REPOSITORY = "create-temp-repository"
    CLEANUP_TEMP_REPOSITORY = "cleanup-temp-repository"
    SHELL_WRAPPER = "shell-wrapper"


PROMPT_READS = {
    Action.READ_ISSUE,
    Action.READ_REPOSITORY,
    Action.READ_GITHUB_PR,
    Action.HYDRATE_SOURCES,
}
TRANSPORT_ACTIONS = {
    Action.CREATE_ISSUE_FOLDER,
    Action.CREATE_PROMPT_FILE,
    Action.VERIFY_PROMPT,
    Action.PREVIEW_PROMPT,
    Action.MINT_DOWNLOAD_LINK,
    Action.EMIT_HANDOFF,
}
PROMPT_MUTATION_FORBIDDEN = {
    Action.GITHUB_WRITE,
    Action.LINEAR_WRITE,
    Action.REPOSITORY_MUTATION,
    Action.PROVIDER_CONFIGURATION,
    Action.AUTHENTICATION_MUTATION,
    Action.DOWNSTREAM_EXECUTION,
}
LOCAL_REPRODUCTION_ACTIONS = {
    Action.CLONE,
    Action.CHECKOUT,
    Action.CREATE_WORKTREE,
    Action.REPOSITORY_MUTATION,
    Action.RUN_LOCAL_TESTS,
    Action.CREATE_TEMP_REPOSITORY,
    Action.CLEANUP_TEMP_REPOSITORY,
    Action.SHELL_WRAPPER,
}


@dataclass(frozen=True)
class ControllerLatch:
    """Test-only conformance evaluator for post-classification action eligibility."""

    mode: Mode
    model_route: str
    prompt_state: PromptState | None = None
    frozen_prompt_digest: str | None = None
    task_authorized: bool = False
    hydration_revision: int = 0
    prompt_design_revision: int = 0
    runtime_blocker: RuntimePrerequisite | None = None
    connector_evidence_complete: bool = False
    local_reproduction_authorized: bool = False
    proven_connector_actions: frozenset[str] = frozenset()
    invalidated_actions: frozenset[Action] = frozenset()

    @classmethod
    def prompt_authoring(cls, *, model_route: str):
        return cls(
            mode=Mode.PROMPT_AUTHORING,
            model_route=model_route,
            prompt_state=PromptState.DESIGN,
            task_authorized=True,
            hydration_revision=1,
            prompt_design_revision=1,
        )

    @classmethod
    def review(cls, *, connector_evidence_complete: bool):
        return cls(
            mode=Mode.REVIEW_AUDIT,
            model_route="review-model",
            connector_evidence_complete=connector_evidence_complete,
            invalidated_actions=frozenset(LOCAL_REPRODUCTION_ACTIONS),
        )

    def eligible_actions(self):
        if self.mode is Mode.REVIEW_AUDIT:
            actions = {Action.READ_GITHUB_PR}
            if self.local_reproduction_authorized:
                actions |= LOCAL_REPRODUCTION_ACTIONS - {Action.SHELL_WRAPPER}
            return actions - set(self.invalidated_actions)

        if self.prompt_state is PromptState.DESIGN:
            return (PROMPT_READS | {Action.FREEZE_PROMPT}) - set(
                self.invalidated_actions
            )
        if self.prompt_state is PromptState.FROZEN:
            return {Action.EDIT_PROMPT} - set(self.invalidated_actions)
        if self.prompt_state is PromptState.DROPBOX_TRANSPORT_ONLY:
            return TRANSPORT_ACTIONS - set(self.invalidated_actions)
        return set()

    def assert_eligible(self, action):
        if action not in self.eligible_actions():
            raise ValueError(f"ineligible action: {action.value}")

    def freeze(self, digest):
        if self.prompt_state is not PromptState.DESIGN or not digest:
            raise ValueError("prompt can freeze only from design with an exact digest")
        return replace(
            self,
            prompt_state=PromptState.FROZEN,
            frozen_prompt_digest=digest,
            invalidated_actions=self.invalidated_actions
            | frozenset(PROMPT_MUTATION_FORBIDDEN),
        )

    def enter_dropbox_transport(self):
        if self.prompt_state is not PromptState.FROZEN:
            raise ValueError("transport-only requires frozen prompt bytes")
        return replace(
            self,
            prompt_state=PromptState.DROPBOX_TRANSPORT_ONLY,
            invalidated_actions=self.invalidated_actions
            | frozenset(
                {
                    Action.HYDRATE_SOURCES,
                    Action.EDIT_PROMPT,
                    Action.DISCOVER_CONNECTOR,
                    Action.REQUEST_PERMISSION,
                    Action.RENDER_INLINE,
                }
            ),
        )

    def block_on_connector_confirmation(self):
        if self.prompt_state is not PromptState.FROZEN or not self.task_authorized:
            raise ValueError("connector confirmation block requires authorized prompt")
        return replace(
            self,
            prompt_state=PromptState.BLOCKED,
            runtime_blocker=RuntimePrerequisite.CONNECTOR_MUTATION_CONFIRMATION,
        )

    def confirm_connector_mutation(self):
        if (
            self.prompt_state is not PromptState.BLOCKED
            or self.runtime_blocker
            is not RuntimePrerequisite.CONNECTOR_MUTATION_CONFIRMATION
        ):
            raise ValueError("connector confirmation is not required")
        return replace(
            self,
            prompt_state=PromptState.FROZEN,
            runtime_blocker=None,
        )

    def revise_prompt(self, digest, *, material_requirement_change):
        if not material_requirement_change:
            raise ValueError("transport correction cannot revise frozen prompt bytes")
        return replace(
            self,
            prompt_state=PromptState.FROZEN,
            frozen_prompt_digest=digest,
            invalidated_actions=self.invalidated_actions
            | frozenset(PROMPT_MUTATION_FORBIDDEN),
        )

    def connector_discovery_required(
        self,
        action_name,
        *,
        later_failure=False,
        acting_identity_changed=False,
        materially_different_capability=False,
        provider_drift=False,
    ):
        if action_name not in self.proven_connector_actions:
            return True
        return any(
            (
                later_failure,
                acting_identity_changed,
                materially_different_capability,
                provider_drift,
            )
        )


@dataclass(frozen=True)
class PromptHandoffEvidence:
    expected_file_id: str
    observed_file_id: str
    expected_size: int
    observed_size: int
    expected_sha256: str
    observed_sha256: str
    download_url: str
    retrieval_succeeded: bool = True
    collision: bool = False

    def compact_handoff(self):
        if not self.retrieval_succeeded:
            raise ValueError("prompt retrieval failed")
        if self.collision:
            raise ValueError("prompt destination collision")
        if self.observed_file_id != self.expected_file_id:
            raise ValueError("Dropbox identity mismatch")
        if self.observed_size != self.expected_size:
            raise ValueError("prompt size mismatch")
        if self.observed_sha256 != self.expected_sha256:
            raise ValueError("prompt digest mismatch")
        if not self.download_url:
            raise ValueError("fresh download URL missing")
        return (
            f"Download: {self.download_url}\n"
            f"Dropbox ID: {self.observed_file_id}\n"
            f"Expected bytes: {self.observed_size}\n"
            f"Expected SHA-256: {self.observed_sha256}\n"
        )


class WorkflowActionLatchTests(unittest.TestCase):
    def test_each_latch_has_one_canonical_heading_owner(self):
        expected_owners = {
            "### Interaction-mode action eligibility latch": REPO_READINESS,
            "### Prompt freeze and transport-only latch": PROMPTS,
            "### Connector-sufficient review latch": REVIEW_PACKET,
        }
        markdown = {
            path: path.read_text(encoding="utf-8") for path in DOCS.rglob("*.md")
        }

        for heading, expected_owner in expected_owners.items():
            owners = {path for path, contents in markdown.items() if heading in contents}
            self.assertEqual(owners, {expected_owner}, heading)

        self.assertIn(
            "prompts.md#prompt-freeze-and-transport-only-latch",
            CHATGPT_ADAPTER.read_text(encoding="utf-8").lower(),
        )

    def test_prompt_authoring_allowlist_is_model_independent(self):
        for model_route in ("stronger", "lower-cost"):
            latch = ControllerLatch.prompt_authoring(model_route=model_route)
            self.assertEqual(latch.mode, Mode.PROMPT_AUTHORING)
            self.assertTrue(PROMPT_MUTATION_FORBIDDEN.isdisjoint(latch.eligible_actions()))

            frozen = latch.freeze("sha256:prompt-v1")
            transport = frozen.enter_dropbox_transport()
            self.assertEqual(transport.frozen_prompt_digest, "sha256:prompt-v1")
            self.assertEqual(transport.eligible_actions(), TRANSPORT_ACTIONS)
            self.assertTrue(
                PROMPT_MUTATION_FORBIDDEN.isdisjoint(transport.eligible_actions())
            )

    def test_material_constraint_change_revises_only_prompt_bytes(self):
        frozen = ControllerLatch.prompt_authoring(model_route="stronger").freeze(
            "sha256:prompt-v1"
        )
        revised = frozen.revise_prompt(
            "sha256:prompt-v2", material_requirement_change=True
        )

        self.assertNotEqual(frozen.frozen_prompt_digest, revised.frozen_prompt_digest)
        self.assertNotIn(Action.LINEAR_WRITE, revised.eligible_actions())
        self.assertNotIn(Action.REPOSITORY_MUTATION, revised.eligible_actions())

    def test_dropbox_correction_reuses_frozen_state_and_connector_evidence(self):
        frozen = replace(
            ControllerLatch.prompt_authoring(model_route="lower-cost").freeze(
                "sha256:prompt-v1"
            ),
            proven_connector_actions=frozenset(
                {
                    "dropbox.create_file",
                    "dropbox.get_file_metadata",
                    "dropbox.download_link",
                }
            ),
        )
        transport = frozen.enter_dropbox_transport()

        self.assertEqual(transport.frozen_prompt_digest, frozen.frozen_prompt_digest)
        for action in (
            Action.REQUEST_PERMISSION,
            Action.HYDRATE_SOURCES,
            Action.DISCOVER_CONNECTOR,
            Action.RENDER_INLINE,
        ):
            with self.assertRaisesRegex(ValueError, "ineligible action"):
                transport.assert_eligible(action)
        self.assertFalse(
            transport.connector_discovery_required("dropbox.create_file")
        )
        self.assertTrue(
            transport.connector_discovery_required(
                "dropbox.create_file", provider_drift=True
            )
        )

    def test_connector_confirmation_blocks_then_resumes_frozen_transport(self):
        frozen = ControllerLatch.prompt_authoring(model_route="stronger").freeze(
            "sha256:prompt-v1"
        )
        blocked = frozen.block_on_connector_confirmation()
        self.assertEqual(blocked.prompt_state, PromptState.BLOCKED)
        self.assertTrue(blocked.task_authorized)
        self.assertEqual(
            blocked.runtime_blocker,
            RuntimePrerequisite.CONNECTOR_MUTATION_CONFIRMATION,
        )
        self.assertEqual(blocked.eligible_actions(), set())

        resumed = blocked.confirm_connector_mutation().enter_dropbox_transport()
        self.assertEqual(resumed.prompt_state, PromptState.DROPBOX_TRANSPORT_ONLY)
        self.assertEqual(resumed.runtime_blocker, None)
        self.assertEqual(resumed.frozen_prompt_digest, blocked.frozen_prompt_digest)
        self.assertEqual(resumed.hydration_revision, blocked.hydration_revision)
        self.assertEqual(
            resumed.prompt_design_revision,
            blocked.prompt_design_revision,
        )

        issue_folder_exists = False
        transport_trace = (
            (() if issue_folder_exists else (Action.CREATE_ISSUE_FOLDER,))
            + (
                Action.CREATE_PROMPT_FILE,
                Action.VERIFY_PROMPT,
                Action.MINT_DOWNLOAD_LINK,
                Action.EMIT_HANDOFF,
            )
        )
        self.assertEqual(
            transport_trace,
            (
                Action.CREATE_ISSUE_FOLDER,
                Action.CREATE_PROMPT_FILE,
                Action.VERIFY_PROMPT,
                Action.MINT_DOWNLOAD_LINK,
                Action.EMIT_HANDOFF,
            ),
        )
        for action in transport_trace:
            resumed.assert_eligible(action)
        self.assertTrue(PROMPT_MUTATION_FORBIDDEN.isdisjoint(transport_trace))
        self.assertNotIn(Action.HYDRATE_SOURCES, transport_trace)
        self.assertNotIn(Action.EDIT_PROMPT, transport_trace)
        self.assertNotIn(Action.RENDER_INLINE, transport_trace)

    def test_transport_trace_is_exact_and_handoff_contains_no_prompt_body(self):
        transport = ControllerLatch.prompt_authoring(model_route="stronger").freeze(
            "sha256:prompt-v1"
        ).enter_dropbox_transport()
        trace = (
            Action.CREATE_ISSUE_FOLDER,
            Action.CREATE_PROMPT_FILE,
            Action.VERIFY_PROMPT,
            Action.PREVIEW_PROMPT,
            Action.MINT_DOWNLOAD_LINK,
            Action.EMIT_HANDOFF,
        )
        for action in trace:
            transport.assert_eligible(action)

        self.assertEqual(trace.count(Action.CREATE_PROMPT_FILE), 1)
        self.assertEqual(trace.count(Action.MINT_DOWNLOAD_LINK), 1)
        self.assertNotIn(Action.RENDER_INLINE, trace)

        evidence = PromptHandoffEvidence(
            expected_file_id="id:prompt-v1",
            observed_file_id="id:prompt-v1",
            expected_size=13761,
            observed_size=13761,
            expected_sha256="8cc802ede64d9454f50aa533b0316b076072c35f7303efeba8857747c3949363",
            observed_sha256="8cc802ede64d9454f50aa533b0316b076072c35f7303efeba8857747c3949363",
            download_url="https://dropbox.example/single-use",
        )
        handoff = evidence.compact_handoff()
        self.assertIn("Dropbox ID: id:prompt-v1", handoff)
        self.assertIn("Expected bytes: 13761", handoff)
        self.assertIn("Expected SHA-256: 8cc802ed", handoff)
        self.assertNotIn("complete prompt body", handoff)

    def test_prompt_handoff_integrity_failures_are_terminal(self):
        valid = PromptHandoffEvidence(
            expected_file_id="id:prompt-v1",
            observed_file_id="id:prompt-v1",
            expected_size=100,
            observed_size=100,
            expected_sha256="a" * 64,
            observed_sha256="a" * 64,
            download_url="https://dropbox.example/single-use",
        )
        failures = (
            (replace(valid, retrieval_succeeded=False), "retrieval failed"),
            (replace(valid, collision=True), "destination collision"),
            (replace(valid, observed_file_id="id:other"), "identity mismatch"),
            (replace(valid, observed_size=99), "size mismatch"),
            (replace(valid, observed_sha256="b" * 64), "digest mismatch"),
            (replace(valid, download_url=""), "download URL missing"),
        )
        for evidence, message in failures:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    evidence.compact_handoff()

    def test_connector_sufficient_review_invalidates_local_execution_plan(self):
        review = ControllerLatch.review(connector_evidence_complete=True)
        self.assertEqual(review.eligible_actions(), {Action.READ_GITHUB_PR})

        for action in LOCAL_REPRODUCTION_ACTIONS:
            with self.assertRaisesRegex(ValueError, "ineligible action"):
                review.assert_eligible(action)

        # A failed forbidden clone cannot make alternate clone or cleanup forms eligible.
        for retry in (Action.CLONE, Action.SHELL_WRAPPER, Action.CLEANUP_TEMP_REPOSITORY):
            with self.assertRaisesRegex(ValueError, "ineligible action"):
                review.assert_eligible(retry)


if __name__ == "__main__":
    unittest.main()
