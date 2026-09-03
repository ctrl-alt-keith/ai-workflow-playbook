from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def markdown_section(path, heading):
    text = path.read_text(encoding="utf-8")
    start = text.index(heading)
    tail = text[start + len(heading) :]
    next_heading = re.search(r"\n#{1,3} ", tail)
    end = start + len(heading) + (next_heading.start() if next_heading else len(tail))
    return text[start:end]


class IssueOwnedPromptHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = normalized(DOCS / "prompt-contracts.md")
        cls.evidence = normalized(DOCS / "evidence-lifecycle.md")
        cls.prompts = normalized(DOCS / "prompts.md")
        cls.readiness = normalized(DOCS / "repo-readiness.md")
        cls.codex = normalized(DOCS / "tool-adapters" / "codex.md")
        cls.claude = normalized(DOCS / "tool-adapters" / "claude.md")
        cls.chatgpt = normalized(DOCS / "tool-adapters" / "chatgpt.md")
        cls.adapter_profiles = (
            markdown_section(
                DOCS / "tool-adapters" / "codex.md",
                "### Issue-Owned Durable Prompt Retrieval",
            ),
            markdown_section(
                DOCS / "tool-adapters" / "claude.md",
                "### Issue-Owned Durable Prompt Retrieval",
            ),
            markdown_section(
                DOCS / "tool-adapters" / "chatgpt.md",
                "### Issue-Owned Durable Prompt Capture And Handoff",
            ),
        )
        cls.delivery_envelope = markdown_section(
            DOCS / "prompts.md",
            "## Issue-Owned Durable Prompt Delivery Envelope Add-On",
        )
        cls.kickoff_boundary = markdown_section(
            DOCS / "core-model.md",
            "## Kickoff Mutation Boundaries",
        )
        cls.complete_prompt_shape = markdown_section(
            DOCS / "prompts.md",
            "## Complete Prompt Shape",
        )
        cls.presentation = markdown_section(
            DOCS / "prompts.md",
            "## Cross-Executor Prompt Presentation",
        )
        cls.chatgpt_prompt_presentation = markdown_section(
            DOCS / "tool-adapters" / "chatgpt.md",
            "### Prompt presentation",
        )
        cls.chatgpt_presentation = markdown_section(
            DOCS / "tool-adapters" / "chatgpt.md",
            "### Recipient-Capability Prompt Presentation",
        )
        cls.chatgpt_dropbox_bootstrap = markdown_section(
            DOCS / "tool-adapters" / "chatgpt.md",
            "### Dropbox Preview And Minimal Executor Handoff",
        )

    def test_prompt_contract_is_the_profile_owner(self):
        heading = "## Issue-Owned Durable Rendered-Prompt Handoff Profile"
        self.assertIn(heading, self.contract)
        self.assertNotIn(heading, self.evidence)
        self.assertIn(
            "prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile",
            self.evidence,
        )
        for projection in (self.prompts, self.codex, self.claude, self.chatgpt):
            self.assertIn(
                "prompt-contracts.md#issue-owned-durable-rendered-prompt-handoff-profile",
                projection.lower(),
            )

    def test_admission_and_capture_are_exact_and_fail_closed(self):
        for phrase in (
            "all six conditions are affirmative",
            "Routine prompts remain non-durable by default",
            "Redaction produces a different rendered-prompt identity",
            "one immutable issue-owned destination",
            "absent-create semantics",
            "no overwrite",
            "no autorename",
            "UTF-8 without a byte-order mark",
            "LF line endings",
            "explicit final-newline rule",
            "qualified comparison of the same frozen local bytes",
            "raw readback remains required",
            "Provider checksums and ordinary whole-file SHA-256 remain distinct algorithms and evidence",
        ):
            self.assertIn(phrase, self.contract)

    def test_model_a_delivery_and_evidence_boundaries(self):
        for phrase in (
            "There is no separate durable exchange, handoff, inbox, registry, or transport root",
            "one private OS-managed executor-owned attempt-local retrieval",
            "Copy/paste is not an exact-byte route",
            "Fallback changes delivery only",
            "the durable rendered prompt",
            "the delivery operation",
            "executor acknowledgement",
            "executor attempt",
            "attempt receipt",
            "executor output",
            "human disposition",
            "PRESERVED",
            "UNKNOWN",
        ):
            self.assertIn(phrase, self.contract)

    def test_delivery_envelope_is_external_to_rendered_prompt_identity(self):
        self.assertIn(
            "## Issue-Owned Durable Prompt Delivery Envelope Add-On",
            self.prompts,
        )
        self.assertNotIn(
            "## Issue-Owned Durable Prompt Handoff Add-On",
            self.prompts,
        )
        for phrase in (
            "This envelope is not part of the referenced rendered-prompt bytes or rendered-prompt digest",
            "add-on to the delivery packet",
            "derive final size, SHA-256, provider identity evidence, and delivery route only after the rendered prompt is frozen",
            "never embed a placeholder self-digest",
        ):
            self.assertIn(phrase, " ".join(self.delivery_envelope.split()))

        for phrase in (
            "Freeze the exact rendered-prompt bytes before deriving their final size",
            "The envelope is not part of the referenced rendered-prompt bytes or rendered-prompt digest",
            "Do not embed a placeholder digest",
            "A copied, reformatted, or otherwise changed prompt is not byte-identical",
        ):
            self.assertIn(phrase, self.contract)

    def test_claude_retrieval_verification_does_not_narrow_execution(self):
        for phrase in (
            "Retrieval and byte verification require only the minimum read capability",
            "After prompt acceptance, choose Claude's tools and permission mode from the bounded task's authorized execution requirements",
            "Read-only tools are mandatory only when",
            "Disable session persistence only when",
            "Prompt handoff alone does not prohibit write tools, tests, repository mutation, output creation, or session persistence",
        ):
            self.assertIn(phrase, self.claude)

        retrieval_section = self.adapter_profiles[1]
        self.assertNotIn("disable session persistence; grant only", retrieval_section)
        self.assertNotIn("grant only the narrow read-only tools", retrieval_section)

    def test_provider_revision_evidence_is_capability_conditional(self):
        for phrase in (
            "Record provider revision when the owning provider exposes it",
            "record explicitly that revision evidence is unavailable",
            "never fabricate a revision",
        ):
            self.assertIn(phrase, self.contract)
        self.assertNotIn(
            "provider identity, provider revision, provider content hash when available",
            self.contract,
        )
        self.assertNotIn(
            "object identity, revision, size, SHA-256",
            self.prompts,
        )

    def test_producing_receipt_and_state_predicates_are_distinct(self):
        self.assertIn("exactly one distinct producing receipt", self.contract)
        self.assertIn("It is not the rendered prompt, delivery evidence", self.contract)
        for state in (
            "`PRESERVED`",
            "`DELIVERED`",
            "`ACCEPTED`",
            "`STARTED`",
            "`COMPLETED`",
            "`FAILED`",
            "`UNKNOWN`",
        ):
            self.assertIn(state, self.contract)
        for boundary in (
            "prior ambiguous absent-create was reconciled exact",
            "One delivery operation identifies the exact rendered prompt, selected route, intended target, and observed delivery result",
            "A bounded failure class, attempt or delivery identity, and last verified state are recorded",
            "delivery alone is insufficient",
            "acknowledgement alone is insufficient",
            "does not imply correctness, human acceptance, merge, release, or adoption",
            "no later state is inferred",
        ):
            self.assertIn(boundary, self.contract)
        self.assertNotIn(
            "The smallest sufficient coordination evidence may report `PRESERVED`",
            self.contract,
        )

    def test_recovery_cleanup_and_authority_remain_bounded(self):
        for phrase in (
            "freshly retrieves current repository, provider, planning, and authority",
            "Historical prompt bytes and receipts remain historical evidence",
            "This profile creates no durable transport object to clean",
            "Remove only the private attempt-local retrieval",
            "Never delete or rewrite the durable prompt as transport cleanup",
            "transfer zero authority",
        ):
            self.assertIn(phrase, self.contract)

    def test_adapters_project_actual_route_without_provider_configuration(self):
        self.assertIn(
            "Do not use a locally synchronized provider mount as provider or durable "
            "identity",
            self.codex,
        )
        self.assertIn("controller-bound digest evidence plus exact read evidence", self.claude)
        for adapter in self.adapter_profiles:
            self.assertIn("provider", adapter.lower())
            self.assertNotRegex(adapter, re.compile(r"\b\d{8,}\b"))
            self.assertNotRegex(
                adapter,
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            )

        for reusable_section in (self.delivery_envelope, *self.adapter_profiles):
            self.assertNotRegex(reusable_section, re.compile(r"ns:\d+//"))
            self.assertNotRegex(reusable_section, re.compile(r"\bid:[A-Za-z0-9_-]+"))
            self.assertNotRegex(
                reusable_section,
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            )

    def test_qualified_machine_recipient_uses_file_first_presentation(self):
        presentation = " ".join(self.presentation.split())
        self.assertIn(
            "For any complete prompt, select presentation by the execution "
            "recipient's currently qualified capability and permitted destination, "
            "independently of the operator or viewer identity",
            presentation,
        )
        route = presentation.index("qualified Dropbox retrieval route")
        file = presentation.index("Dropbox-backed file")
        handoff = presentation.index("target-shaped [thin semantic handoff]")
        self.assertLess(route, file)
        self.assertLess(file, handoff)

    def test_codex_and_claude_handoffs_use_the_same_shared_model(self):
        presentation = " ".join(self.presentation.split())
        delivery_envelope = " ".join(self.delivery_envelope.split())
        self.assertIn("model applies symmetrically", presentation)
        self.assertIn("same shared presentation and handoff contract", presentation)
        self.assertIn(
            "immediately provide the target-shaped [thin semantic handoff]"
            "(#thin-semantic-handoff-envelope) without reproducing the complete prompt",
            presentation,
        )
        for phrase in (
            "one private OS-managed executor-owned attempt-local retrieval",
            "Fallback changes delivery only",
        ):
            self.assertIn(phrase, self.contract)
        for phrase in (
            "Exact durable identity: [immutable human locator, provider locator, "
            "object identity, size, SHA-256",
            "Verify raw or attempt-local bytes, size, SHA-256, UTF-8, no BOM, LF "
            "endings, and the declared final-newline rule before acceptance.",
            "Fail closed on collision, mismatch, missing identity, prohibited "
            "retention, unsupported required capability, or ambiguous authority.",
            "Prohibited delivery: no exchange root, mutable alias, shadow durable "
            "copy, or copy/paste claim of byte identity",
        ):
            self.assertIn(phrase, delivery_envelope)
        self.assertIn(
            "Do not reproduce the complete durable artifact in chat merely for transport.",
            self.evidence,
        )

        codex, claude = (" ".join(profile.split()) for profile in self.adapter_profiles[:2])
        directions = (
            (
                "Codex",
                "Claude",
                claude,
                "when Claude Code receives",
                "Direct provider consumption is qualified only when the current "
                "Claude surface can retrieve raw bytes and the required provider "
                "identity metadata",
                "Otherwise use one private OS-managed executor-attempt copy",
                "Bind the launch to its exact path, expected size, SHA-256, and "
                "declared text format",
                "Do not use a locally synchronized provider mount as provider or "
                "durable identity",
            ),
            (
                "Claude",
                "Codex",
                codex,
                "when Codex receives",
                "Prefer direct retrieval only when the current connector or provider "
                "route exposes raw bytes and the required provider identity metadata",
                "download the raw provider object once into a private OS-managed "
                "attempt-local directory",
                "verify the provider identity and raw bytes, and pass Codex the exact "
                "local path plus expected size and SHA-256",
                "Do not use a locally synchronized provider mount as provider or "
                "durable identity",
            ),
        )
        for (
            producer,
            recipient,
            recipient_profile,
            receipt,
            direct_route,
            fallback,
            verification,
            prohibited_local_substitute,
        ) in directions:
            with self.subTest(producer=producer, recipient=recipient):
                self.assertIn(receipt, recipient_profile)
                self.assertIn(direct_route, recipient_profile)
                self.assertIn(fallback, recipient_profile)
                self.assertIn(verification, recipient_profile)
                self.assertIn(prohibited_local_substitute, recipient_profile)
                self.assertIn("fail closed on the shared cleanup conditions", recipient_profile)
                self.assertLess(
                    recipient_profile.index(direct_route),
                    recipient_profile.index(fallback),
                )

    def test_cross_executor_prompt_handoffs_keep_the_kickoff_mutation_boundary(self):
        kickoff_boundary = " ".join(self.kickoff_boundary.split())
        presentation = " ".join(self.presentation.split())
        self.assertIn(
            "producing prompt or handoff evidence does not authorize repository "
            "implementation, remote-repository mutation, or unrelated planning-system "
            "mutation",
            kickoff_boundary,
        )
        self.assertIn("model applies symmetrically", presentation)
        self.assertIn("same shared presentation and handoff contract", presentation)

    def test_two_block_format_is_conditional_on_inline_presentation(self):
        complete_shape = " ".join(self.complete_prompt_shape.split())
        chatgpt_prompt = " ".join(self.chatgpt_prompt_presentation.split())
        self.assertIn(
            "When inline presentation is selected for a complete generated prompt",
            complete_shape,
        )
        self.assertIn(
            "When the model legitimately selects inline "
            "presentation for a complete, copy-ready prompt or downstream handoff",
            chatgpt_prompt,
        )

    def test_preview_does_not_gate_machine_handoff(self):
        presentation = " ".join(self.presentation.split())
        chatgpt_presentation = " ".join(self.chatgpt_presentation.split())
        self.assertIn("does not block the handoff or require prompt approval", presentation)
        for gate_phrase in ("Approve", "Revise", "Reject", "explicit approval", "before sending"):
            self.assertNotIn(gate_phrase, presentation)
        self.assertIn("Do not wait for prompt approval", chatgpt_presentation)

    def test_human_or_unqualified_recipient_uses_inline_presentation(self):
        presentation = " ".join(self.presentation.split())
        self.assertIn("For a human execution recipient", presentation)
        self.assertIn("machine execution recipient has no qualified Dropbox route", presentation)
        self.assertIn("present the complete prompt inline", presentation)
        self.assertIn("consecutive copyable code blocks", self.chatgpt)

    def test_material_governance_layers_without_capturing_routine_prompts(self):
        presentation = " ".join(self.presentation.split())
        self.assertIn("issue-owned durable rendered-prompt handoff profile", presentation)
        self.assertIn("A routine prompt delivered through a file does not", presentation)
        self.assertIn("use inline presentation only when the owning fallback contract permits", presentation)
        self.assertIn("two-block inline renderer", self.chatgpt_presentation)

    def test_chatgpt_preview_prefers_the_returned_file_id(self):
        preview = " ".join(self.chatgpt_dropbox_bootstrap.split())
        self.assertIn("Dropbox `file_preview` with `file_paths`", preview)
        file_id = preview.index("`file_id` returned by the write")
        namespace = preview.index("returned namespace path only when no file ID")
        self.assertLess(file_id, namespace)
        preview_call = preview.index("`file_preview`")
        download_link = preview.index("`download_link`")
        self.assertLess(preview_call, download_link)

    def test_chatgpt_connector_results_are_not_the_visible_widget(self):
        preview = " ".join(self.chatgpt_dropbox_bootstrap.split())
        self.assertIn("connector metadata are not a visibly rendered preview", preview)
        for substitute in (
            "`open_in_dropbox_url`",
            "copy or share links",
            "thumbnail URLs",
            "metadata for the widget",
        ):
            self.assertIn(substitute, preview)
        self.assertIn("only when the operator actually sees it", preview)
        self.assertIn("Preview remains optional and does not gate the handoff", preview)

    def test_chatgpt_example_has_normal_metadata_and_one_minimal_bootstrap(self):
        section = self.chatgpt_dropbox_bootstrap
        block_start = section.index("```text")
        metadata = section[:block_start]
        blocks = re.findall(r"```[^\n]*\n(.*?)\n```", section, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        bootstrap = blocks[0]
        for field in (
            "Thread routing:",
            "Recommended model:",
            "Recommended reasoning level:",
            "Reason:",
        ):
            self.assertIn(field, metadata)
            self.assertNotIn(field, bootstrap)
        self.assertLessEqual(len([line for line in bootstrap.splitlines() if line]), 8)
        for field in ("Download:", "Expected SHA-256:", "Execute:"):
            self.assertIn(field, bootstrap)
        self.assertIn("Keep the complete prompt in Dropbox", section)
        self.assertIn("do not summarize or reproduce the prompt", section)

    def test_retrieval_bootstrap_uses_a_shell_safe_name_and_direct_process(self):
        section = self.chatgpt_dropbox_bootstrap
        blocks = re.findall(r"```[^\n]*\n(.*?)\n```", section, re.DOTALL)
        self.assertEqual(len(blocks), 1)
        bootstrap = blocks[0]
        directory_name_line = next(
            line
            for line in bootstrap.splitlines()
            if line.startswith("Attempt directory basename:")
        )
        directory_name = directory_name_line.partition(":")[2].strip()
        local_name_line = next(
            line for line in bootstrap.splitlines() if line.startswith("Local filename:")
        )
        local_name = local_name_line.partition(":")[2].strip()

        self.assertRegex(directory_name, re.compile(r"\A[A-Za-z0-9._-]+\Z"))
        self.assertRegex(local_name, re.compile(r"\A[A-Za-z0-9._-]+\Z"))
        self.assertIn("direct argv/process invocation", bootstrap)
        self.assertIn(
            "workflow-generated attempt-local retrieval basenames",
            self.readiness,
        )
        self.assertIn("direct argv/process invocation", self.codex)
        codex_retrieval = self.adapter_profiles[0]
        self.assertIn(
            "repo-readiness.md#repo-local-workflow-state",
            codex_retrieval,
        )
        self.assertNotIn("[A-Za-z0-9._-]+", codex_retrieval)
        self.assertNotIn("spaces, quotes, brackets", codex_retrieval)

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            probe = root / "downloader-probe"
            marker = root / "downloader-invoked"
            probe.write_text(
                f"#!{sys.executable}\n"
                "from pathlib import Path\n"
                "import sys\n"
                "Path(sys.argv[1]).write_text('\\n'.join(sys.argv[2:]), "
                "encoding='utf-8')\n",
                encoding="utf-8",
            )
            probe.chmod(0o700)

            unsafe_target = root / "prompt retrieval (first attempt)" / local_name
            single_use_url = "https://example.invalid/file?token=a&single_use=1"
            shell_built_command = (
                f"{probe} {marker} --output {unsafe_target} {single_use_url}"
            )
            rejected = subprocess.run(
                ["/bin/sh", "-c", shell_built_command],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(rejected.returncode, 0)
            self.assertFalse(marker.exists())

            safe_directory = root / directory_name.replace("XXXXXXXX", "A1")
            self.assertRegex(safe_directory.name, re.compile(r"\A[A-Za-z0-9._-]+\Z"))
            safe_target = safe_directory / local_name
            invoked = subprocess.run(
                [
                    str(probe),
                    str(marker),
                    "--output",
                    str(safe_target),
                    single_use_url,
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(invoked.returncode, 0, invoked.stderr)
            self.assertEqual(
                marker.read_text(encoding="utf-8").splitlines(),
                ["--output", str(safe_target), single_use_url],
            )


if __name__ == "__main__":
    unittest.main()
