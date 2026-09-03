from dataclasses import dataclass, replace
from enum import Enum
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
    delegated_task_target_capabilities: tuple[str, ...] = ()
    initial_route_disqualification: "RouteDisqualification | None" = None


class QualificationEvidenceSource(str, Enum):
    CURRENT_RUNTIME_ROUTE = "current-runtime-route-observation"
    DELEGATED_TASK_TARGET = "delegated-task-target"


@dataclass(frozen=True)
class RouteDisqualification:
    route: str
    route_id: str
    reason: str
    evidence_source: QualificationEvidenceSource
    owning_contract: str

    def __post_init__(self):
        if (
            self.route != "qualified-file-route"
            or not self.route_id
            or not self.reason
            or not self.owning_contract
        ):
            raise ValueError(
                "route disqualification requires a qualified file route, "
                "route identity, and reason, plus an owning qualification contract"
            )
        if self.evidence_source is not QualificationEvidenceSource.CURRENT_RUNTIME_ROUTE:
            raise ValueError(
                "route disqualification requires current runtime route evidence; "
                "delegated task target state is excluded from stage 5 qualification"
            )


def owned_current_route_disqualification(*, route, route_id, reason):
    return RouteDisqualification(
        route=route,
        route_id=route_id,
        reason=reason,
        evidence_source=QualificationEvidenceSource.CURRENT_RUNTIME_ROUTE,
        owning_contract="test-current-route-qualification-contract",
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


@dataclass(frozen=True)
class FrozenDeliveryDecisionRecord:
    """Test-only materialization of the resolved stage 1 through 7 outputs."""

    stage_outputs: tuple[tuple[str, object], ...]
    record_revision: int = 0
    supersedes_record_revision: int | None = None

    def __post_init__(self):
        if tuple(stage for stage, _ in self.stage_outputs) != STAGES[:7]:
            raise ValueError(
                "complete frozen decision record requires every ordered stage 1 "
                "through 7 output"
            )
        if any(output is None for _, output in self.stage_outputs):
            raise ValueError("complete frozen decision record has no missing output")
        if self.record_revision < 0 or (
            self.record_revision == 0
            and self.supersedes_record_revision is not None
        ) or (
            self.record_revision > 0
            and self.supersedes_record_revision != self.record_revision - 1
        ):
            raise ValueError("frozen decision record lineage is incomplete or mismatched")

        decision = dict(self.stage_outputs)
        classification = decision[STAGES[1]]
        resolution = decision[STAGES[4]]
        if not isinstance(resolution, CapabilityRouteResolution):
            raise ValueError("complete frozen decision record requires stage 5 state")

        if classification == "conceptual-fragment":
            expected_presentation = "lightweight"
        elif resolution.route == "qualified-file-route":
            expected_presentation = "file-backed"
        elif resolution.route in ("inline-route", "inline-fallback-permitted"):
            expected_presentation = "inline"
        else:
            expected_presentation = "blocked"
        expected_renderer = {
            "lightweight": "lightweight",
            "file-backed": "thin-handoff",
            "inline": "canonical-inline-two-block",
            "blocked": "none",
        }[expected_presentation]
        if decision[STAGES[5]] != expected_presentation:
            raise ValueError(
                "frozen decision record presentation mismatches stage 5 resolution"
            )
        if decision[STAGES[6]] != expected_renderer:
            raise ValueError(
                "frozen decision record renderer mismatches frozen presentation"
            )

    @property
    def decision(self):
        return dict(self.stage_outputs)


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


def freeze_delivery_decision(
    trace,
    *,
    record_revision=0,
    supersedes_record_revision=None,
):
    """Materialize and validate one complete stage 1 through 7 record."""

    if tuple(stage for stage, _ in trace) != STAGES:
        raise ValueError("complete frozen decision record requires the ordered trace")
    return FrozenDeliveryDecisionRecord(
        stage_outputs=tuple(trace[:7]),
        record_revision=record_revision,
        supersedes_record_revision=supersedes_record_revision,
    )


def apply_delivery(frozen_record, *, current_record=None):
    """Apply only the current complete frozen decision record."""

    if not isinstance(frozen_record, FrozenDeliveryDecisionRecord):
        raise ValueError(
            "complete frozen decision record is required before delivery application"
        )
    if not isinstance(current_record, FrozenDeliveryDecisionRecord):
        raise ValueError(
            "current complete frozen decision record is required before application"
        )
    if frozen_record != current_record:
        raise ValueError("stale or superseded decision record cannot be consumed")

    decision = frozen_record.decision
    route_resolution = decision[STAGES[4]]
    presentation = decision[STAGES[5]]
    renderer = decision[STAGES[6]]
    outcome = {
        "lightweight": "lightweight-response",
        "file-backed": "dropbox-backed-thin-handoff",
        "inline": "inline-complete-prompt",
        "blocked": "blocked-no-renderer",
    }[presentation]

    return AppliedDelivery(
        presentation=presentation,
        renderer=renderer,
        outcome=outcome,
        diagnostics=route_resolution.diagnostics,
    )


def evaluate_and_apply(case):
    trace = decision_trace(case)
    record = freeze_delivery_decision(trace)
    return trace, apply_delivery(record, current_record=record)


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
    original_record,
    route_disqualification,
    *,
    current_record,
    **changes,
):
    """Re-evaluate only transport and downstream stages after route failure."""

    if not isinstance(original_record, FrozenDeliveryDecisionRecord):
        raise ValueError("capability re-entry requires a complete frozen decision record")
    if original_record != current_record:
        raise ValueError("stale or superseded decision record cannot restart re-entry")
    if route_disqualification is None:
        raise ValueError("capability re-entry requires owning route disqualification")
    original_resolution = original_record.decision[STAGES[4]]
    if (
        original_resolution.route != route_disqualification.route
        or original_resolution.route_id != route_disqualification.route_id
        or original_resolution.qualification
        not in ("qualified", "qualified-with-known-limitation")
    ):
        raise ValueError(
            "capability re-entry requires a previously selected qualified route"
        )
    if case.qualified_file_route_id != original_resolution.route_id:
        raise ValueError(
            "capability re-entry case must match the current frozen route identity"
        )
    updated = replace(case, initial_route_disqualification=None, **changes)
    classification = original_record.decision[STAGES[1]]
    terminal_failure = original_resolution.capability_reentry_count >= 1
    trace = (
        *original_record.stage_outputs[:4],
        *decision_tail(
            updated,
            classification,
            route_disqualification=route_disqualification,
            terminal_failure=terminal_failure,
            capability_reentry_count=1,
        ),
    )
    return freeze_delivery_decision(
        trace,
        record_revision=original_record.record_revision + 1,
        supersedes_record_revision=original_record.record_revision,
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
            "Stage 5 has a closed evidence-provenance boundary",
            normalized_section,
        )
        self.assertIn(
            "accepts only observations about the current runtime route, classified "
            "by the current owning route-qualification contract",
            normalized_section,
        )
        self.assertIn(
            "desired future capability, implementation intent, prompt body, or "
            "explanatory rationale is not current-route evidence",
            normalized_section,
        )
        self.assertIn(
            "Only that owning-contract classification may create route "
            "disqualification",
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
            "Every later application failure consumes only that current record",
            normalized_section,
        )
        self.assertIn(
            "stages 5 through 7 must be materially realized as one complete frozen "
            "decision record",
            normalized_section,
        )
        self.assertIn(
            "must not accept loose stage fields or reconstruct them from task prose, "
            "diagnostics, rationale, or conversational context",
            normalized_section,
        )
        self.assertIn(
            "An absent, incomplete, stale, mismatched, or superseded record fails "
            "closed with no complete-prompt renderer",
            normalized_section,
        )
        self.assertIn(
            "A caller cannot bypass the record and request a complete-prompt renderer "
            "directly",
            normalized_section,
        )
        self.assertIn(
            "A stale or superseded record cannot restart application or bounded re-entry",
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

    def test_docs_define_bounded_issue_owned_codex_handoff_pilot(self):
        prompts = PROMPTS.read_text(encoding="utf-8")
        heading = "### Issue-Owned File-Backed Handoff Prose-DAG Pilot"
        pilot = prompts[
            prompts.index(heading) : prompts.index(
                "## Cross-Executor Prompt Presentation"
            )
        ]
        opening = pilot[: pilot.index("Once explicitly activated")]
        normalized_pilot = " ".join(pilot.split())
        normalized_opening = " ".join(opening.split())

        states = (
            "PROMPT_READY",
            "ROUTE_QUALIFIED",
            "PROMPT_STORED",
            "ARTIFACT_VERIFIED",
            "HANDOFF_EMITTED",
        )
        positions = [pilot.index(state) for state in states]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Any unmet prerequisite -> BLOCKED", pilot)
        self.assertIn("Human correction -> new revision", pilot)
        self.assertIn("[from] -> [to] | [succeeded | blocked]", pilot)
        self.assertIn("Ineligible:", pilot)
        self.assertIn("Correction:", pilot)
        self.assertIn(
            "does not replace, repeat, or recompute any of the eight stages",
            normalized_pilot,
        )
        for relationship in (
            "`PROMPT_READY` prerequisites hold",
            "`PROMPT_READY -> ROUTE_QUALIFIED`",
            "already-frozen stages 5 through 7 decision record",
            "qualified file route",
            "`file-backed` presentation",
            "`thin-handoff` renderer",
        ):
            self.assertIn(relationship, normalized_opening)

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
                "delegated_task_target_capabilities",
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

        human_trace = decision_trace(
            replace(
                base,
                execution_recipient="human",
                recipient_class="human",
                qualified_file_capability=False,
                permitted_file_destination=False,
            )
        )
        human = dict(human_trace)
        self.assertEqual(
            human["capability-and-transport-resolution"].route,
            "inline-route",
        )
        self.assertEqual(human["renderer-selection"], "canonical-inline-two-block")
        human_record = freeze_delivery_decision(human_trace)
        human_applied = apply_delivery(
            human_record,
            current_record=human_record,
        )
        self.assertEqual(human_applied.presentation, "inline")
        self.assertEqual(human_applied.renderer, "canonical-inline-two-block")

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
        initial = freeze_delivery_decision(decision_trace(case))
        fallback = reroute_after_capability_failure(
            case,
            initial,
            owned_current_route_disqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="selected Dropbox write was rejected by its owning contract",
            ),
            current_record=initial,
            qualified_file_capability=False,
            permitted_file_destination=False,
            inline_fallback_permitted=True,
        )
        self.assertEqual(fallback.stage_outputs[:4], initial.stage_outputs[:4])
        fallback_resolution = fallback.decision[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(fallback_resolution.qualification, "route-disqualified")
        self.assertEqual(fallback_resolution.capability_reentry_count, 1)
        self.assertIsNone(fallback_resolution.prior_route_disqualification)
        self.assertEqual(
            fallback_resolution.current_route_disqualification.reason,
            "selected Dropbox write was rejected by its owning contract",
        )
        self.assertEqual(
            fallback.decision["renderer-selection"],
            "canonical-inline-two-block",
        )

        unresolved = reroute_after_capability_failure(
            case,
            initial,
            owned_current_route_disqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="selected Dropbox route failed during application",
            ),
            current_record=initial,
            capability_resolved=False,
            qualified_file_capability=False,
            permitted_file_destination=False,
        )
        unresolved_resolution = unresolved.decision[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(unresolved_resolution.qualification, "unresolved")
        self.assertIsNone(unresolved_resolution.current_route_disqualification)
        self.assertEqual(
            unresolved_resolution.prior_route_disqualification.reason,
            "selected Dropbox route failed during application",
        )
        self.assertEqual(unresolved.decision["presentation-selection"], "blocked")

        same_route = reroute_after_capability_failure(
            case,
            initial,
            owned_current_route_disqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="selected Dropbox destination became unavailable",
            ),
            current_record=initial,
            qualified_file_capability=True,
            permitted_file_destination=True,
            qualified_file_route_id="dropbox:primary",
        )
        same_route_resolution = same_route.decision[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(same_route_resolution.route, "blocked")
        self.assertEqual(
            same_route_resolution.current_route_disqualification.route_id,
            "dropbox:primary",
        )
        self.assertEqual(same_route.decision["presentation-selection"], "blocked")

        alternate = reroute_after_capability_failure(
            case,
            initial,
            owned_current_route_disqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="selected Dropbox destination became unavailable",
            ),
            current_record=initial,
            qualified_file_capability=True,
            permitted_file_destination=True,
            qualified_file_route_id="dropbox:alternate",
        )
        alternate_resolution = alternate.decision[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(alternate.stage_outputs[:4], initial.stage_outputs[:4])
        self.assertEqual(alternate_resolution.route, "qualified-file-route")
        self.assertEqual(alternate_resolution.route_id, "dropbox:alternate")
        self.assertEqual(alternate_resolution.qualification, "qualified")
        self.assertEqual(alternate_resolution.capability_reentry_count, 1)
        self.assertIsNone(alternate_resolution.current_route_disqualification)
        self.assertEqual(
            alternate_resolution.prior_route_disqualification.route_id,
            "dropbox:primary",
        )
        self.assertEqual(alternate.decision["renderer-selection"], "thin-handoff")

        alternate_case = replace(
            case,
            qualified_file_route_id="dropbox:alternate",
        )
        second_disqualification = owned_current_route_disqualification(
            route="qualified-file-route",
            route_id="dropbox:alternate",
            reason="re-evaluated file route also failed",
        )
        with self.assertRaisesRegex(ValueError, "current frozen route identity"):
            reroute_after_capability_failure(
                case,
                alternate,
                second_disqualification,
                current_record=alternate,
            )

        second_failure = reroute_after_capability_failure(
            alternate_case,
            alternate,
            second_disqualification,
            current_record=alternate,
            qualified_file_capability=False,
            permitted_file_destination=False,
            inline_fallback_permitted=True,
        )
        self.assertEqual(
            second_failure.stage_outputs[:4],
            initial.stage_outputs[:4],
        )
        second_resolution = second_failure.decision[
            "capability-and-transport-resolution"
        ]
        self.assertEqual(second_resolution.qualification, "route-disqualified")
        self.assertEqual(second_resolution.capability_reentry_count, 1)
        self.assertIsNone(second_resolution.prior_route_disqualification)
        self.assertEqual(
            second_resolution.current_route_disqualification.reason,
            "re-evaluated file route also failed",
        )
        self.assertEqual(second_failure.decision["presentation-selection"], "blocked")
        self.assertEqual(second_failure.decision["renderer-selection"], "none")

    def test_capability_reentry_requires_explicit_route_disqualification(self):
        with self.assertRaisesRegex(
            ValueError,
            "qualified file route, route identity, and reason",
        ):
            RouteDisqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="",
                evidence_source=QualificationEvidenceSource.CURRENT_RUNTIME_ROUTE,
                owning_contract="test-current-route-qualification-contract",
            )
        with self.assertRaisesRegex(ValueError, "owning qualification contract"):
            RouteDisqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="owning contract rejected the route",
                evidence_source=QualificationEvidenceSource.CURRENT_RUNTIME_ROUTE,
                owning_contract="",
            )
        with self.assertRaisesRegex(
            ValueError,
            "qualified file route, route identity, and reason",
        ):
            RouteDisqualification(
                route="qualified-file-route",
                route_id="",
                reason="owning contract rejected the route",
                evidence_source=QualificationEvidenceSource.CURRENT_RUNTIME_ROUTE,
                owning_contract="test-current-route-qualification-contract",
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
        initial = freeze_delivery_decision(decision_trace(case))

        with self.assertRaisesRegex(ValueError, "owning route disqualification"):
            reroute_after_capability_failure(
                case,
                initial,
                None,
                current_record=initial,
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
            never_qualified_record = freeze_delivery_decision(
                decision_trace(never_qualified)
            )
            reroute_after_capability_failure(
                never_qualified,
                never_qualified_record,
                owned_current_route_disqualification(
                    route="qualified-file-route",
                    route_id="dropbox:primary",
                    reason="caller asserted a failure without a selected route",
                ),
                current_record=never_qualified_record,
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

        record = freeze_delivery_decision(trace)
        with self.assertRaisesRegex(ValueError, "complete frozen decision record"):
            apply_delivery(
                "canonical-inline-two-block",
                current_record=record,
            )

    def test_narrative_direct_render_without_frozen_record_fails_closed(self):
        narrative_inline_substitution = (
            (
                "capability-and-transport-resolution",
                CapabilityRouteResolution(
                    route="qualified-file-route",
                    qualification="qualified-with-known-limitation",
                    route_id="dropbox:primary",
                    diagnostics=(
                        "controller post-write raw-byte SHA verification unavailable",
                    ),
                ),
            ),
            ("presentation-selection", "inline"),
            ("renderer-selection", "canonical-inline-two-block"),
            ("delivery-outcome", "inline-complete-prompt"),
        )

        with self.assertRaisesRegex(ValueError, "complete frozen decision record"):
            apply_delivery(narrative_inline_substitution, current_record=None)

    def test_missing_incomplete_or_mismatched_record_fails_closed(self):
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
        trace = decision_trace(case)
        record = freeze_delivery_decision(trace)

        with self.assertRaisesRegex(ValueError, "complete frozen decision record"):
            apply_delivery(None, current_record=record)
        with self.assertRaisesRegex(ValueError, "every ordered stage 1 through 7"):
            FrozenDeliveryDecisionRecord(stage_outputs=record.stage_outputs[:-1])

        mismatched_outputs = tuple(
            (stage, "inline") if stage == "presentation-selection" else (stage, output)
            for stage, output in record.stage_outputs
        )
        with self.assertRaisesRegex(ValueError, "presentation mismatches stage 5"):
            FrozenDeliveryDecisionRecord(stage_outputs=mismatched_outputs)

    def test_superseded_record_cannot_restart_application_or_reentry(self):
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
        initial = freeze_delivery_decision(decision_trace(case))
        disqualification = owned_current_route_disqualification(
            route="qualified-file-route",
            route_id="dropbox:primary",
            reason="selected Dropbox destination became unavailable",
        )
        current = reroute_after_capability_failure(
            case,
            initial,
            disqualification,
            current_record=initial,
            qualified_file_route_id="dropbox:alternate",
        )

        with self.assertRaisesRegex(ValueError, "stale or superseded"):
            apply_delivery(initial, current_record=current)
        with self.assertRaisesRegex(ValueError, "stale or superseded"):
            reroute_after_capability_failure(
                case,
                initial,
                disqualification,
                current_record=current,
                qualified_file_capability=False,
                permitted_file_destination=False,
            )
        applied = apply_delivery(current, current_record=current)
        self.assertEqual(applied.presentation, "file-backed")
        self.assertEqual(applied.renderer, "thin-handoff")

    def test_task_target_capability_cannot_disqualify_current_file_route(self):
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
            delegated_task_target_capabilities=(
                "stronger controller-side exact-byte verification",
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
        self.assertEqual(resolution.diagnostics, case.known_route_limitations)

        without_target = replace(case, delegated_task_target_capabilities=())
        frozen_without_target = freeze_delivery_decision(
            decision_trace(without_target)
        )
        frozen_with_target = freeze_delivery_decision(trace)
        self.assertEqual(
            frozen_with_target.stage_outputs,
            frozen_without_target.stage_outputs,
        )
        self.assertEqual(
            apply_delivery(
                frozen_without_target,
                current_record=frozen_without_target,
            ).renderer,
            "thin-handoff",
        )

        with self.assertRaisesRegex(
            ValueError,
            "delegated task target state is excluded from stage 5 qualification",
        ):
            RouteDisqualification(
                route="qualified-file-route",
                route_id="dropbox:primary",
                reason="task target requests a stronger capability",
                evidence_source=QualificationEvidenceSource.DELEGATED_TASK_TARGET,
                owning_contract="test-current-route-qualification-contract",
            )

    def test_route_disqualifying_failure_uses_owned_fallback_or_block(self):
        base = DeliveryCase(
            produces_prompt=True,
            complete_executable=True,
            operator_viewer="human-operator",
            execution_recipient="Codex",
            recipient_class="machine-executor",
            initial_route_disqualification=owned_current_route_disqualification(
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
