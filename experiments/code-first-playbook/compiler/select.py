"""Evidence envelopes qualify coverage, never permission or external truth."""

from datetime import datetime
from .model import canonical, condition, expressions, reference_sites, require, shape, typed

STATES = {"known", "unknown", "stale", "unavailable", "conflicting"}


def timestamp(value):
    require(type(value) is str and value.endswith("Z"), "explicit UTC timestamp required")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def qualify(records, observations, context, as_of, acquisitions):
    """The outside acquisition layer owns truth/authentication; inputs bind its record."""
    require(type(observations) is list, "observations list required")
    now = timestamp(as_of)
    grouped, fixed, reports = {}, {}, {}
    for obs in observations:
        shape(obs, {"fact_id", "state", "value", "evaluator", "resolution_class",
                    "basis", "scope", "freshness", "rationale", "diagnostics"})
        fid = obs["fact_id"]
        require(fid in records and records[fid]["kind"] == "fact", "undefined observation fact")
        fact = records[fid]
        require(obs["state"] in STATES, "unknown observation state")
        require(obs["resolution_class"] == fact["resolution_class"], "forged resolution upgrade")
        require(obs["evaluator"] in fact["evaluators"], "unpermitted evaluator claim")
        require(obs["state"] != "known" or typed(obs["value"], fact), "mistyped observation")
        require(type(obs["diagnostics"]) is list, "observation diagnostics")
        require(obs["state"] == "known" or bool(obs["diagnostics"]), "state reason required")
        require(type(obs["rationale"]) is str, "observation rationale")
        shape(obs["freshness"], {"observed_at"})
        observed = timestamp(obs["freshness"]["observed_at"])
        require(observed <= now, "future observation")
        state = obs["state"]
        if obs["scope"] != context:
            state = "stale"
        freshness = fact["freshness"]
        if freshness["mode"] == "time" and (now - observed).total_seconds() > freshness["max_age_seconds"]:
            state = "stale"
        qualified = False
        if fact["resolution_class"] == "external_judgment":
            require(bool(obs["rationale"]), "judgment rationale required")
            require(obs["basis"] is None, "judgment cannot claim observed qualification")
        elif obs["basis"] is not None:
            require(type(obs["basis"]) is str and obs["basis"] in acquisitions,
                    "unverified qualification claim")
            evidence = acquisitions[obs["basis"]]
            shape(evidence, {"id", "source", "fact_id", "value", "evaluator", "scope",
                             "observed_at", "checked_claim", "verified", "artifact_id", "sha256"})
            require(evidence["source"] in fact["sources"] and evidence["fact_id"] == fid
                    and evidence["evaluator"] == obs["evaluator"]
                    and evidence["value"] == obs["value"] and type(evidence["value"]) is type(obs["value"])
                    and evidence["scope"] == obs["scope"]
                    and evidence["observed_at"] == obs["freshness"]["observed_at"]
                    and evidence["verified"] is True and bool(evidence["checked_claim"])
                    and bool(evidence["artifact_id"]) and len(evidence["sha256"]) == 64,
                    "evidence qualification mismatch")
            qualified = state == "known"
        grouped.setdefault(fid, []).append({"observation": obs, "state": state, "qualified": qualified})
    for fid, fact in records.items():
        if fact["kind"] != "fact":
            continue
        group = grouped.get(fid, [])
        signatures = {canonical({"state": x["state"], "value": x["observation"]["value"]})
                      for x in group}
        conflict = len(signatures) > 1
        state = "conflicting" if conflict else group[0]["state"] if group else "unknown"
        can_fix = bool(group) and not conflict and all(x["qualified"] for x in group)
        if can_fix:
            fixed[fid] = group[0]["observation"]["value"]
        reports[fid] = {"question": fact["question"], "owner": fact["owner"],
                        "resolution_class": fact["resolution_class"], "state": state,
                        "pruning_qualified": can_fix, "observations": group}
    return fixed, reports


def select(records, observations, context, as_of, acquisitions, diagnostics=()):
    fixed, reports = qualify(records, observations, context, as_of, acquisitions)
    rules = {i: r for i, r in records.items() if r["kind"] == "rule" and r["status"] != "retired"}
    activation = {i: condition(r["when"], records, fixed) for i, r in rules.items()}
    selected = {i for i, state in activation.items() if state["state"] != "false"}
    reasons = {i: ["applicable" if activation[i]["state"] == "true" else "conditional"] for i in selected}
    excluded = {}

    def exclusion(key, expr):
        from .model import expression
        facts = sorted(expression(expr, records) & fixed.keys())
        excluded[key] = {"expression": expr, "qualified_facts": facts,
                         "evidence_ids": sorted({x["observation"]["basis"] for f in facts
                                                 for x in reports[f]["observations"]}),
                         "scope": context, "as_of": as_of,
                         "reason": "false for all remaining assignments"}
    for i, r in rules.items():
        if activation[i]["state"] == "false":
            exclusion(i, r["when"])
    pending = sorted(selected)
    while pending:
        rid = pending.pop()
        rule = rules[rid]
        edges = [("requires", target, None) for target in rule["requires"]]
        edges += [("activates", e["target"], e["when"]) for e in rule["activates"]]
        edges += [("overrides", e["target"], e["when"]) for e in rule["overrides"]]
        if "inherits" in rule["failure"]:
            edges.append(("failure", rule["failure"]["inherits"], None))
        for relation, target, expr in edges:
            if expr is not None and condition(expr, records, fixed)["state"] == "false":
                exclusion(f"{rid}:{relation}:{target}", expr)
                continue
            if target in rules:
                reason = f"{rid}:{relation}"
                reasons.setdefault(target, [])
                if reason not in reasons[target]:
                    reasons[target].append(reason)
                if target not in selected:
                    selected.add(target); pending.append(target)
    # Retain vocabulary and external boundaries transitively. Reference-only edges
    # do not activate rules: an unselected referenced rule is an explicit boundary.
    included, external_rules = set(selected), set()
    todo = list(sorted(selected))
    while todo:
        rid = todo.pop()
        for site, target in reference_sites(records[rid]):
            if target in rules and target not in selected:
                external_rules.add(target)
                continue
            if target not in included:
                included.add(target); todo.append(target)
    clauses = []
    for rid in sorted(selected):
        evaluated = {path: condition(expr, records, fixed) for path, expr in expressions(rules[rid])}
        clauses.append({"id": rid, "activation": activation[rid],
                        "selection_reasons": sorted(reasons[rid]),
                        "conditions": evaluated, "record": rules[rid]})
    return {"status": "experimental_shadow", "operational_owner": "existing_playbook_prose",
            "complete_execution_contract": False, "permission": "not_evaluated",
            "completion_grants_authority": False, "rules": clauses,
            "vocabulary": {i: records[i] for i in sorted(included) if i not in rules},
            "external_rule_boundaries": sorted(external_rules),
            "external_sources": sorted(i for i in included if records[i]["kind"] == "source"),
            "fact_reports": {i: reports[i] for i in sorted(included) if i in reports},
            "exclusions": dict(sorted(excluded.items())),
            "diagnostics": list(diagnostics)}
