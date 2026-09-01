from dataclasses import dataclass, replace
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
    qualified_file_route_id: str | None = None
    inline_fallback_permitted: bool = False
    known_route_limitations: tuple[str, ...] = ()
    initial_route_disqualification: "RouteDisqualification | None" = None


@dataclass(frozen=True)
class RouteDisqualification:
    route: str
    route_id: str
    reason: str

    def __post_init__(self):
        if (
            self.route != "qualified-file-route"
            or not self.route_id
            or not self.reason
        ):
            raise ValueError(
                "route disqualification requires a qualified file route, "
                "route identity, and reason"
            )


@dataclass(frozen=True)
class CapabilityRouteResolution:
    route: str
    qualification: str
    route_id: str | None = None
    diagnostics: tuple[str, ...] = ()
    current_route_disqualification: RouteDisqualification | None = None
    prior_route_disqualification: RouteDisqualification | None = None
    capability_reentry_count: int = 0


@dataclass(frozen=True)
class AppliedDelivery:
    presentation: str
    renderer: str
    outcome: str
    diagnostics: tuple[str, ...] = ()


def decision_tail(
    case,
    classification,
    *,
    route_disqualification=None,
    terminal_failure=False,
    capability_reentry_count=0,
):
    route_id = None
    current_route_disqualification = None
    prior_route_disqualification = None
    if classification == "conceptual-fragment":
        route = "not-applicable"
        qualification = "not-applicable"
    elif case.recipient_class == "unresolved":
        route = "blocked"
        qualification = "unresolved"
    elif case.recipient_class == "human":
        route = "inline-route"
        qualification = "qualified"
    elif terminal_failure:
        route = "blocked"
        qualification = "route-disqualified"
        current_route_disqualification = route_disqualification
    elif not case.capability_resolved:
        route = "blocked"
        qualification = "unresolved"
        prior_route_disqualification = route_disqualification
    elif (
        case.qualified_file_capability
        and case.permitted_file_destination
        and case.qualified_file_route_id
        and (
            route_disqualification is None
            or case.qualified_file_route_id != route_disqualification.route_id
        )
    ):
        route = "qualified-file-route"
        route_id = case.qualified_file_route_id
        qualification = (
            "qualified-with-known-limitation"
            if case.known_route_limitations
            else "qualified"
        )
        prior_route_disqualification = route_disqualification
    elif (
        route_disqualification
        and case.qualified_file_capability
        and case.permitted_file_destination
        and case.qualified_file_route_id == route_disqualification.route_id
    ):
        route = (
            "inline-fallback-permitted"
            if case.inline_fallback_permitted
            else "blocked"
        )
        qualification = "route-disqualified"
        current_route_disqualification = route_disqualification
    elif case.inline_fallback_permitted:
        route = "inline-fallback-permitted"
        qualification = (
            "route-disqualified" if route_disqualification else "unresolved"
        )
        current_route_disqualification = route_disqualification
    elif route_disqualification:
        route = "blocked"
        qualification = "route-disqualified"
        current_route_disqualification = route_disqualification
    else:
        route = "blocked"
        qualification = "unresolved"

    route_resolution = CapabilityRouteResolution(
        route=route,
        qualification=qualification,
        route_id=route_id,
        diagnostics=case.known_route_limitations,
        current_route_disqualification=current_route_disqualification,
        prior_route_disqualification=prior_route_disqualification,
        capability_reentry_count=capability_reentry_count,
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
        *decision_tail(
            case,
            classification,
            route_disqualification=case.initial_route_disqualification,
        ),
    )


def reroute_after_capability_failure(
    case,
    original_trace,
    route_disqualification,
    **changes,
):
    """Re-evaluate only transport and downstream stages after route failure."""

    if route_disqualification is None:
        raise ValueError("capability re-entry requires owning route disqualification")
    original_resolution = dict(original_trace)[STAGES[4]]
    if (
        original_resolution.route != route_disqualification.route
        or original_resolution.route_id != route_disqualification.route_id
        or original_resolution.qualification
        not in ("qualified", "qualified-with-known-limitation")
    ):
        raise ValueError(
            "capability re-entry requires a previously selected qualified route"
        )
    updated = replace(case, initial_route_disqualification=None, **changes)
    classification = dict(original_trace)[STAGES[1]]
    terminal_failure = original_resolution.capability_reentry_count >= 1
    return (
        *original_trace[:4],
        *decision_tail(
            updated,
            classification,
            route_disqualification=route_disqualification,
            terminal_failure=terminal_failure,
            capability_reentry_count=1,
        ),
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
            "Route selection and exact identity when applicable: "
            "`qualified-file-route`, `inline-route`, "
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
            "contract against the same route class and exact identity selected in "
            "the frozen stage 5 record",
            normalized_section,
        )
        self.assertIn(
            "prior route failure does not preempt a file route with a different "
            "exact identity",
            normalized_section,
        )
        self.assertIn(
            "superseded failure only as a prior route-disqualification record",
            normalized_section,
        )
        self.assertIn(
            "Record in the new stage 5 output that the bounded re-evaluation was "
            "consumed",
            normalized_section,
        )
        self.assertIn(
            "terminate as `blocked` with that newly observed `route-disqualified` "
            "reason",
            normalized_section,
        )
        self.assertIn(
            "Every later application failure consumes the current stage 5 record",
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

    def test_resolved_codex_semantics_exclude_request_wording(self):
        prompts = PROMPTS.read_text(encoding="utf-8")
        decision_section = prompts[
            prompts.index("## Prompt Delivery Decision Model") : prompts.index(
                "## Cross-Executor Prompt Presentation"
            )
        ]
        for representative_request in (
            "`prompt me`",
            "`show me the machine handoff`",
            "`give me the prompt`",
        ):
            self.assertIn(representative_request, decision_section)

        base = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
            qualified_file_capability=True,
            permitted_file_destination=True,
            qualified_file_route_id="dropbox:primary",
        )
        expected = (
            ("artifact-production", "prompt-produced"),
            ("artifact-classification", "complete-executable"),
            ("operator-viewer-resolution", "human-operator"),
            ("execution-recipient-resolution", "Codex:machine-executor"),
            (
                "capability-and-transport-resolution",
                CapabilityRouteResolution(
                    "qualified-file-route",
                    "qualified",
                    route_id="dropbox:primary",
                ),
            ),
            ("presentation-selection", "file-backed"),
            ("renderer-selection", "thin-handoff"),
            ("delivery-outcome", "dropbox-backed-thin-handoff"),
        )

        self.assertEqual(
            set(DeliveryCase.__dataclass_fields__),
            {
                "produces_prompt",
                "complete_executable",
                "operator_viewer",
                "execution_recipient",
                "recipient_class",
                "capability_resolved",
                "qualified_file_capability",
                "permitted_file_destination",
                "qualified_file_route_id",
                "inline_fallback_permitted",
                "known_route_limitations",
                "initial_route_disqualification",
            },
        )

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
            qualified_file_route_id="dropbox:primary",
        )
        initial = decision_trace(case)
        fallback = reroute_after_capability_failure(
            case,
            initial,
            RouteDisqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="selected Dropbox write was rejected by its owning contract",
            ),
            qualified_file_capability=False,
            permitted_file_destination=False,
            inline_fallback_permitted=True,
        )
        self.assertEqual(fallback[:4], initial[:4])
        fallback_resolution = dict(fallback)[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(fallback_resolution.qualification, "route-disqualified")
        self.assertEqual(fallback_resolution.capability_reentry_count, 1)
        self.assertIsNone(fallback_resolution.prior_route_disqualification)
        self.assertEqual(
            fallback_resolution.current_route_disqualification.reason,
            "selected Dropbox write was rejected by its owning contract",
        )
        self.assertEqual(dict(fallback)["renderer-selection"], "canonical-inline-two-block")

        unresolved = reroute_after_capability_failure(
            case,
            initial,
            RouteDisqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="selected Dropbox route failed during application",
            ),
            capability_resolved=False,
            qualified_file_capability=False,
            permitted_file_destination=False,
        )
        unresolved_resolution = dict(unresolved)[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(unresolved_resolution.qualification, "unresolved")
        self.assertIsNone(unresolved_resolution.current_route_disqualification)
        self.assertEqual(
            unresolved_resolution.prior_route_disqualification.reason,
            "selected Dropbox route failed during application",
        )
        self.assertEqual(dict(unresolved)["presentation-selection"], "blocked")

        same_route = reroute_after_capability_failure(
            case,
            initial,
            RouteDisqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="selected Dropbox destination became unavailable",
            ),
            qualified_file_capability=True,
            permitted_file_destination=True,
            qualified_file_route_id="dropbox:primary",
        )
        same_route_resolution = dict(same_route)[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(same_route_resolution.route, "blocked")
        self.assertEqual(
            same_route_resolution.current_route_disqualification.route_id,
            "dropbox:primary",
        )
        self.assertEqual(dict(same_route)["presentation-selection"], "blocked")

        alternate = reroute_after_capability_failure(
            case,
            initial,
            RouteDisqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="selected Dropbox destination became unavailable",
            ),
            qualified_file_capability=True,
            permitted_file_destination=True,
            qualified_file_route_id="dropbox:alternate",
        )
        alternate_resolution = dict(alternate)[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(alternate[:4], initial[:4])
        self.assertEqual(alternate_resolution.route, "qualified-file-route")
        self.assertEqual(alternate_resolution.route_id, "dropbox:alternate")
        self.assertEqual(alternate_resolution.qualification, "qualified")
        self.assertEqual(alternate_resolution.capability_reentry_count, 1)
        self.assertIsNone(alternate_resolution.current_route_disqualification)
        self.assertEqual(
            alternate_resolution.prior_route_disqualification.route_id,
            "dropbox:primary",
        )
        self.assertEqual(dict(alternate)["renderer-selection"], "thin-handoff")

        second_failure = reroute_after_capability_failure(
            case,
            alternate,
            RouteDisqualification(
                route="qualified-file-route",
                route_id="dropbox:alternate",
                reason="re-evaluated file route also failed",
            ),
            qualified_file_capability=False,
            permitted_file_destination=False,
            inline_fallback_permitted=True,
        )
        self.assertEqual(second_failure[:4], initial[:4])
        second_resolution = dict(second_failure)[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(second_resolution.qualification, "route-disqualified")
        self.assertEqual(second_resolution.capability_reentry_count, 1)
        self.assertIsNone(second_resolution.prior_route_disqualification)
        self.assertEqual(
            second_resolution.current_route_disqualification.reason,
            "re-evaluated file route also failed",
        )
        self.assertEqual(dict(second_failure)["presentation-selection"], "blocked")
        self.assertEqual(dict(second_failure)["renderer-selection"], "none")

    def test_capability_reentry_requires_explicit_route_disqualification(self):
        with self.assertRaisesRegex(
            ValueError,
            "qualified file route, route identity, and reason",
        ):
            RouteDisqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="",
            )

        case = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
            qualified_file_capability=True,
            permitted_file_destination=True,
            qualified_file_route_id="dropbox:primary",
        )
        initial = decision_trace(case)

        with self.assertRaisesRegex(ValueError, "owning route disqualification"):
            reroute_after_capability_failure(
                case,
                initial,
                None,
                qualified_file_capability=False,
                permitted_file_destination=False,
                inline_fallback_permitted=True,
            )

        never_qualified = replace(
            case,
            qualified_file_capability=False,
            permitted_file_destination=False,
            qualified_file_route_id=None,
        )
        with self.assertRaisesRegex(ValueError, "previously selected qualified route"):
            reroute_after_capability_failure(
                never_qualified,
                decision_trace(never_qualified),
                RouteDisqualification(
                    route="qualified-file-route",
                    route_id="dropbox:primary",
                    reason="caller asserted a failure without a selected route",
                ),
                inline_fallback_permitted=True,
            )

        missing_route_identity = replace(case, qualified_file_route_id=None)
        missing_identity_resolution = dict(decision_trace(missing_route_identity))[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(missing_identity_resolution.route, "blocked")
        self.assertEqual(missing_identity_resolution.qualification, "unresolved")

    def test_known_limitation_is_retained_without_mutating_frozen_application(self):
        case = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
            qualified_file_capability=True,
            permitted_file_destination=True,
            qualified_file_route_id="dropbox:primary",
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
            initial_route_disqualification=RouteDisqualification(
                route="qualified-file-route",
                route_id="dropbox:candidate",
                reason="owning contract rejected the candidate Dropbox route",
            ),
        )

        blocked = dict(decision_trace(base))
        self.assertEqual(
            blocked["capability-and-transport-resolution"].qualification,
            "route-disqualified",
        )
        self.assertEqual(blocked["presentation-selection"], "blocked")
        self.assertEqual(
            blocked[
                "capability-and-transport-resolution"
            ].current_route_disqualification.reason,
            "owning contract rejected the candidate Dropbox route",
        )

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
