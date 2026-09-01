from dataclasses import dataclass, fields, replace
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "docs" / "prompts.md"

STAGES = (
    "artifact-production",
    "artifact-classification",
    "operator-viewer-resolution",
    "execution-recipient-resolution",
    "capability-and-transport-resolution",
    "presentation-selection",
    "renderer-selection",
    "delivery-outcome",
)


@dataclass(frozen=True)
class DeliveryCase:
    """Resolved semantic inputs for the test-only conformance evaluator.

    The Playbook owns semantic classification. Raw request wording is
    intentionally absent from this post-resolution boundary so later delivery
    stages cannot reinterpret it.
    """

    produces_prompt: bool
    complete_executable: bool
    operator_viewer: str
    execution_recipient: str
    recipient_class: str
    capability_resolved: bool = True
    qualified_file_capability: bool = False
    permitted_file_destination: bool = False
    inline_fallback_permitted: bool = False
    known_route_limitations: tuple[str, ...] = ()
    route_disqualified: bool = False


@dataclass(frozen=True)
class CapabilityRouteResolution:
    route: str
    qualification: str
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class AppliedDelivery:
    presentation: str
    renderer: str
    outcome: str
    diagnostics: tuple[str, ...] = ()


def decision_tail(case, classification, capability_failure_count=0):
    if classification == "conceptual-fragment":
        route = "not-applicable"
        qualification = "not-applicable"
    elif case.recipient_class == "unresolved":
        route = "blocked"
        qualification = "unresolved"
    elif case.recipient_class == "human":
        route = "inline-route"
        qualification = "qualified"
    elif capability_failure_count > 1 or not case.capability_resolved:
        route = "blocked"
        qualification = "unresolved"
    elif case.route_disqualified:
        route = (
            "inline-fallback-permitted"
            if case.inline_fallback_permitted
            else "blocked"
        )
        qualification = "route-disqualified"
    elif case.qualified_file_capability and case.permitted_file_destination:
        route = "qualified-file-route"
        qualification = (
            "qualified-with-known-limitation"
            if case.known_route_limitations
            else "qualified"
        )
    elif case.inline_fallback_permitted:
        route = "inline-fallback-permitted"
        qualification = "unresolved"
    else:
        route = "blocked"
        qualification = "unresolved"

    route_resolution = CapabilityRouteResolution(
        route=route,
        qualification=qualification,
        diagnostics=case.known_route_limitations,
    )

    if classification == "conceptual-fragment":
        presentation = "lightweight"
    elif route == "qualified-file-route":
        presentation = "file-backed"
    elif route in ("inline-route", "inline-fallback-permitted"):
        presentation = "inline"
    else:
        presentation = "blocked"

    renderer = {
        "lightweight": "lightweight",
        "file-backed": "thin-handoff",
        "inline": "canonical-inline-two-block",
        "blocked": "none",
    }[presentation]
    outcome = {
        "lightweight": "lightweight-response",
        "file-backed": "dropbox-backed-thin-handoff",
        "inline": "inline-complete-prompt",
        "blocked": "blocked-no-renderer",
    }[presentation]

    return (
        (STAGES[4], route_resolution),
        (STAGES[5], presentation),
        (STAGES[6], renderer),
        (STAGES[7], outcome),
    )


def apply_delivery(
    frozen_trace,
    *,
    presentation=None,
    renderer=None,
    outcome=None,
):
    """Apply the selected renderer without recomputing upstream semantics."""

    decision = dict(frozen_trace)
    route_resolution = decision[STAGES[4]]
    selected = (
        decision[STAGES[5]],
        decision[STAGES[6]],
        decision[STAGES[7]],
    )
    requested = (
        selected[0] if presentation is None else presentation,
        selected[1] if renderer is None else renderer,
        selected[2] if outcome is None else outcome,
    )
    if requested != selected:
        raise ValueError("application cannot replace the frozen delivery selection")

    return AppliedDelivery(
        presentation=selected[0],
        renderer=selected[1],
        outcome=selected[2],
        diagnostics=route_resolution.diagnostics,
    )


def evaluate_and_apply(case):
    trace = decision_trace(case)
    return trace, apply_delivery(trace)


def decision_trace(case):
    """Evaluate the documented stages from already-resolved semantics."""

    production = "prompt-produced" if case.produces_prompt else "no-prompt"
    if production == "no-prompt":
        return ((STAGES[0], production),)

    classification = (
        "complete-executable" if case.complete_executable else "conceptual-fragment"
    )

    return (
        (STAGES[0], production),
        (STAGES[1], classification),
        (STAGES[2], case.operator_viewer),
        (
            STAGES[3],
            f"{case.execution_recipient}:{case.recipient_class}",
        ),
        *decision_tail(case, classification),
    )


def reroute_after_capability_failure(case, original_trace, failure_count, **changes):
    """Re-evaluate only transport and downstream stages after route failure."""

    updated = replace(case, **changes)
    if not updated.route_disqualified:
        raise ValueError("capability re-entry requires route-disqualified state")
    classification = dict(original_trace)[STAGES[1]]
    return (
        *original_trace[:4],
        *decision_tail(updated, classification, capability_failure_count=failure_count),
    )


class PromptDeliveryDecisionModelTests(unittest.TestCase):
    def test_docs_define_one_ordered_model_with_explicit_stage_outputs(self):
        prompts = PROMPTS.read_text(encoding="utf-8")
        section = prompts[
            prompts.index("## Prompt Delivery Decision Model") : prompts.index(
                "## Cross-Executor Prompt Presentation"
            )
        ]
        normalized_section = " ".join(section.split())

        positions = [section.index(f"`{stage}`") for stage in STAGES]
        self.assertEqual(positions, sorted(positions))
        for output in (
            "`no-prompt`",
            "`complete-executable`",
            "`machine-executor`",
            "`unresolved`",
            "`qualified-file-route`",
            "`inline-route`",
            "`file-backed`",
            "`canonical-inline-two-block`",
            "`blocked`",
            "`qualified-with-known-limitation`",
            "`route-disqualified`",
        ):
            self.assertIn(output, section)
        self.assertIn(
            "must not re-read conversational wording to replace that output",
            normalized_section,
        )
        self.assertIn(
            "operator or viewer separate from the executable prompt's execution recipient",
            normalized_section,
        )
        self.assertIn(
            "same delivery attempt may perform exactly one capability re-evaluation",
            normalized_section,
        )
        self.assertIn(
            "Preserve the stage 1 through 4 outputs unchanged",
            normalized_section,
        )
        self.assertIn(
            "executes the selected action",
            normalized_section,
        )
        self.assertIn(
            "must not inspect diagnostic state to substitute the canonical inline renderer",
            normalized_section,
        )
        self.assertIn(
            "Route selection: `qualified-file-route`, `inline-route`, "
            "`inline-fallback-permitted`, or `blocked`; separate qualification:",
            normalized_section,
        )
        self.assertIn(
            "Stage 4 `unresolved` means the execution recipient was not resolved; "
            "stage 5 `unresolved` means capability or transport never qualified",
            normalized_section,
        )
        self.assertIn(
            "classify the observed failure as route-disqualifying under its owning "
            "contract, perform the one downstream-only re-evaluation, then apply "
            "the terminal mapping from the new stage 5 state",
            normalized_section,
        )
        for mapping in (
            "`complete-executable` plus a `machine-executor` and "
            "`qualified-file-route` selects `file-backed` presentation",
            "`complete-executable` plus a human execution recipient resolves "
            "`inline-route`, then selects `inline` presentation",
            "`complete-executable` plus `inline-fallback-permitted` selects "
            "`inline` presentation",
            "An `unresolved` execution recipient resolves transport to `blocked`",
        ):
            self.assertIn(mapping, normalized_section)

    def test_cold_start_variants_share_resolved_codex_semantics(self):
        base = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
            qualified_file_capability=True,
            permitted_file_destination=True,
        )
        expected = (
            ("artifact-production", "prompt-produced"),
            ("artifact-classification", "complete-executable"),
            ("operator-viewer-resolution", "human-operator"),
            ("execution-recipient-resolution", "Codex:machine-executor"),
            (
                "capability-and-transport-resolution",
                CapabilityRouteResolution("qualified-file-route", "qualified"),
            ),
            ("presentation-selection", "file-backed"),
            ("renderer-selection", "thin-handoff"),
            ("delivery-outcome", "dropbox-backed-thin-handoff"),
        )

        variants = (
            "Prompt me for CAK-194.",
            "Show me the Codex handoff for CAK-194.",
            "Give me the prompt for CAK-194.",
        )
        self.assertNotIn("request_text", {field.name for field in fields(DeliveryCase)})
        for wording in variants:
            with self.subTest(wording=wording):
                trace, applied = evaluate_and_apply(base)
                self.assertEqual(trace, expected)
                self.assertEqual(applied.renderer, "thin-handoff")
                self.assertNotIn(
                    "canonical-inline-two-block",
                    [output for _, output in trace],
                )

        human = dict(
            decision_trace(
                replace(
                    base,
                    execution_recipient="human",
                    recipient_class="human",
                    qualified_file_capability=False,
                    permitted_file_destination=False,
                )
            )
        )
        self.assertEqual(
            human["capability-and-transport-resolution"].route,
            "inline-route",
        )
        self.assertEqual(human["renderer-selection"], "canonical-inline-two-block")

    def test_conceptual_human_fragment_remains_lightweight(self):
        case = DeliveryCase(
            produces_prompt=True,
            complete_executable=False,
            operator_viewer="human-operator",
            execution_recipient="human",
            recipient_class="human",
        )

        trace = dict(decision_trace(case))
        self.assertEqual(trace["artifact-classification"], "conceptual-fragment")
        self.assertEqual(trace["presentation-selection"], "lightweight")
        self.assertEqual(trace["renderer-selection"], "lightweight")
        self.assertEqual(trace["delivery-outcome"], "lightweight-response")

    def test_inline_renderer_requires_selected_inline_fallback(self):
        base = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
        )

        fallback = dict(
            decision_trace(replace(base, inline_fallback_permitted=True))
        )
        self.assertEqual(
            fallback["capability-and-transport-resolution"].route,
            "inline-fallback-permitted",
        )
        self.assertEqual(
            fallback["capability-and-transport-resolution"].qualification,
            "unresolved",
        )
        self.assertEqual(fallback["presentation-selection"], "inline")
        self.assertEqual(
            fallback["renderer-selection"], "canonical-inline-two-block"
        )

        blocked = dict(
            decision_trace(replace(base, capability_resolved=False))
        )
        self.assertEqual(
            blocked["capability-and-transport-resolution"].route, "blocked"
        )
        self.assertEqual(blocked["presentation-selection"], "blocked")
        self.assertEqual(blocked["renderer-selection"], "none")
        self.assertEqual(blocked["delivery-outcome"], "blocked-no-renderer")

    def test_never_qualified_file_capability_is_not_route_disqualified(self):
        case = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
        )

        resolution = dict(decision_trace(case))[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(resolution.route, "blocked")
        self.assertEqual(resolution.qualification, "unresolved")

    def test_no_prompt_stops_after_artifact_production(self):
        case = DeliveryCase(
            produces_prompt=False,
            complete_executable=False,
            operator_viewer="human-operator",
            execution_recipient="unresolved",
            recipient_class="unresolved",
        )
        self.assertEqual(
            decision_trace(case),
            (("artifact-production", "no-prompt"),),
        )

    def test_unresolved_recipient_blocks_without_renderer(self):
        case = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="unresolved",
            recipient_class="unresolved",
            inline_fallback_permitted=True,
        )
        trace = dict(decision_trace(case))
        self.assertEqual(trace["capability-and-transport-resolution"].route, "blocked")
        self.assertEqual(trace["presentation-selection"], "blocked")
        self.assertEqual(trace["renderer-selection"], "none")

    def test_capability_reentry_freezes_semantics_and_is_bounded(self):
        case = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
            qualified_file_capability=True,
            permitted_file_destination=True,
        )
        initial = decision_trace(case)
        fallback = reroute_after_capability_failure(
            case,
            initial,
            1,
            qualified_file_capability=False,
            permitted_file_destination=False,
            inline_fallback_permitted=True,
            route_disqualified=True,
        )
        self.assertEqual(fallback[:4], initial[:4])
        self.assertEqual(
            dict(fallback)["capability-and-transport-resolution"].qualification,
            "route-disqualified",
        )
        self.assertEqual(dict(fallback)["renderer-selection"], "canonical-inline-two-block")

        second_failure = reroute_after_capability_failure(
            case,
            fallback,
            2,
            qualified_file_capability=False,
            permitted_file_destination=False,
            inline_fallback_permitted=True,
            route_disqualified=True,
        )
        self.assertEqual(second_failure[:4], initial[:4])
        self.assertEqual(dict(second_failure)["presentation-selection"], "blocked")
        self.assertEqual(dict(second_failure)["renderer-selection"], "none")

    def test_capability_reentry_requires_explicit_route_disqualification(self):
        case = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
            qualified_file_capability=True,
            permitted_file_destination=True,
        )
        initial = decision_trace(case)

        with self.assertRaisesRegex(ValueError, "route-disqualified"):
            reroute_after_capability_failure(
                case,
                initial,
                1,
                qualified_file_capability=False,
                permitted_file_destination=False,
                inline_fallback_permitted=True,
            )

    def test_known_limitation_is_retained_without_mutating_frozen_application(self):
        case = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
            qualified_file_capability=True,
            permitted_file_destination=True,
            known_route_limitations=(
                "controller post-write raw-byte SHA verification unavailable",
            ),
        )

        trace, applied = evaluate_and_apply(case)
        resolution = dict(trace)["capability-and-transport-resolution"]
        self.assertEqual(resolution.route, "qualified-file-route")
        self.assertEqual(
            resolution.qualification,
            "qualified-with-known-limitation",
        )
        self.assertEqual(applied.presentation, "file-backed")
        self.assertEqual(applied.renderer, "thin-handoff")
        self.assertEqual(applied.outcome, "dropbox-backed-thin-handoff")
        self.assertEqual(applied.diagnostics, resolution.diagnostics)

        with self.assertRaisesRegex(ValueError, "frozen delivery selection"):
            apply_delivery(
                trace,
                presentation="inline",
                renderer="canonical-inline-two-block",
                outcome="inline-complete-prompt",
            )

    def test_route_disqualifying_failure_uses_owned_fallback_or_block(self):
        base = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
            route_disqualified=True,
        )

        blocked = dict(decision_trace(base))
        self.assertEqual(
            blocked["capability-and-transport-resolution"].qualification,
            "route-disqualified",
        )
        self.assertEqual(blocked["presentation-selection"], "blocked")

        fallback = dict(
            decision_trace(replace(base, inline_fallback_permitted=True))
        )
        self.assertEqual(
            fallback["capability-and-transport-resolution"].route,
            "inline-fallback-permitted",
        )
        self.assertEqual(fallback["presentation-selection"], "inline")


if __name__ == "__main__":
    unittest.main()
