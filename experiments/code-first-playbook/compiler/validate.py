"""Bounded consistency checks. Structural success does not prove fidelity."""

from .model import (COMMON, FIELDS, UNITS, assignments, condition, evaluate,
                    expression, expressions, reference_sites, require, shape, strings, typed)


def acyclic(edges, label):
    active, done = set(), set()
    def visit(node, trail):
        require(node not in active, f"{label} cycle: {' -> '.join(trail + [node])}")
        if node in done:
            return
        active.add(node)
        for child in edges.get(node, []):
            visit(child, trail + [node])
        active.remove(node)
        done.add(node)
    for node in sorted(edges):
        visit(node, [])


def validate(modules, locations, enforce_scope=True):
    records = {r["id"]: r for m in modules.values() for r in m["records"]}
    rules = {i: r for i, r in records.items() if r.get("kind") == "rule"}
    if enforce_scope:
        require(1 <= len(rules) <= 12, "rule count outside pilot bound")
        require({r.get("unit") for r in rules.values()} <= UNITS, "excluded semantic unit")
        for rid, r in rules.items():
            require(rid == r["unit"], "decomposition needs documented human scope review")
    diagnostics = []
    for module in modules.values():
        strings(module["imports"])
        require(set(module["imports"]) <= modules.keys(), "undeclared imported module")
        require(module["owner"] in records and records[module["owner"]]["kind"] == "source",
                "module owner must be source")
    for rid, r in records.items():
        kind = r.get("kind")
        require(kind in FIELDS, f"unsupported record kind: {kind}")
        shape(r, COMMON | FIELDS[kind])
        require(r['owner'] == modules[locations[rid]['module']]['owner'], 'record outside semantic module owner')
        for field in ('definition','path','question','does','body'):
            if field in r:
                require(type(r[field]) is str and bool(r[field].strip()), f'{rid}.{field}: nonempty text required')
        require(r["status"] in ("active", "deprecated", "retired"), "invalid status")
        strings(r["references"])
        require(r["owner"] in records and records[r["owner"]]["kind"] == "source", "owner required")
        if kind in ("term", "fact"):
            require(r["type"] in ("boolean", "enum"), "unsupported finite type")
            require(type(r["values"]) is list and bool(r["values"]), "finite domain required")
            require(all(typed(v, r) for v in r["values"]), "mistyped domain")
            require(len(r["values"]) == len(set(r["values"])), "duplicate domain")
            require(r["type"] != "boolean" or set(r["values"]) == {False, True},
                    "Boolean domain must be complete")
        if kind == "fact":
            require(r["resolution_class"] in ("external_judgment", "observed_evidence"),
                    "unknown resolution class")
            strings(r["evaluators"]); strings(r["sources"])
            require(r["evaluators"] and r["sources"], "fact qualification owner required")
            shape(r["freshness"], {"mode"}, {"max_age_seconds"})
            require(r["freshness"]["mode"] in ("context", "time"), "freshness mode")
            if r["freshness"]["mode"] == "time":
                age = r["freshness"].get("max_age_seconds")
                require(type(age) is int and age >= 0, "freshness interval")
        if kind == "action":
            require(r["action_kind"] in ("behavior", "boundary", "evidence"), "action kind")
            strings(r["does_not_establish"])
            require(type(r["parameters"]) is list, "typed parameters required")
            names = []
            for p in r["parameters"]:
                shape(p, {"name", "type", "required"})
                require(type(p["required"]) is bool and type(p["name"]) is str, "parameter type")
                require(p['type'] in records and records[p['type']]['kind']=='term', 'parameter domain must be term')
                names.append(p["name"])
            require(len(names) == len(set(names)), "duplicate parameter")
        if kind == "rule":
            shape(r["effect"], {"actor", "modality", "action", "parameters"})
            require(r["effect"]["modality"] in ("must", "should", "must_not"), "modality")
            require(type(r["effect"]["actor"]) is str and r["effect"]["actor"], "actor")
            for key in ("requires", "before", "context"):
                strings(r[key])
            require(type(r['activates']) is list and type(r['overrides']) is list, 'edge list required')
            for edge in r["activates"]:
                shape(edge, {"target", "when"})
            for edge in r["overrides"]:
                shape(edge, {"target", "when", "question", "source", "justification"})
                require(edge["question"] and edge["justification"], "scoped override justification")
            shape(r["lifetime"], {"starts", "persists_within", "ends_when"})
            failure = r["failure"]
            if "inherits" in failure:
                shape(failure, {"inherits", "scope"})
            else:
                shape(failure, {"when", "action", "alternatives", "scope"})
                strings(failure["alternatives"])
            shape(r["completion"], {"evidence", "boundary", "question"}, {"when"})
            shape(r["authority_ref"], {"source", "question", "check_at"})
            require(r["authority_ref"]["check_at"] == "immediately-before-action",
                    "authority must remain a live outside check")
            for _, expr in expressions(r):
                expression(expr, records)
        for site, target in reference_sites(r):
            require(target in records, f"{rid}.{site}: missing reference {target}")
            target_module = locations[target]["module"]
            here = locations[rid]["module"]
            require(target_module == here or target_module in modules[here]["imports"],
                    f"undeclared import at {rid}.{site}")
            require(records[target]["status"] != "retired" or site.startswith("references."),
                    f"active dependency on retired ID at {rid}.{site}")
    prerequisites, precedence, failures = {}, {}, {}
    for rid, r in rules.items():
        require(all(records[x]['kind'] in ('source','rule') for x in r['requires']), 'requires source or rule')
        require(all(records[x['target']]['kind'] in ('source','rule') for x in r['activates']), 'activates source or rule')
        action = records[r["effect"]["action"]]
        require(action["kind"] == "action" and action["action_kind"] == "behavior", "effect action")
        shape(r["effect"]["parameters"], {p["name"] for p in action["parameters"] if p["required"]},
              {p["name"] for p in action["parameters"]})
        for param in action["parameters"]:
            term = records[param["type"]]
            require(term["kind"] == "term", "parameter domain must be term")
            if param["name"] in r["effect"]["parameters"]:
                require(typed(r["effect"]["parameters"][param["name"]], term), "effect parameter value")
        for aid in r["before"] + [r["completion"]["boundary"]]:
            a = records[aid]
            require(a["kind"] == "action" and a["action_kind"] == "boundary" and
                    bool(a["parameters"]), "ordering target must be concrete typed boundary")
        require(records[r["completion"]["evidence"]]["kind"] == "action" and
                records[r["completion"]["evidence"]]["action_kind"] == "evidence", "completion evidence")
        require(all(records[c]["kind"] == "context" for c in r["context"]), "context references")
        require(records[r["authority_ref"]["source"]]["kind"] == "source", "authority source")
        prerequisites[rid] = [t for t in r["requires"] if t in rules]
        precedence[rid] = [e["target"] for e in r["overrides"]]
        for edge in r["overrides"]:
            require(edge["target"] in rules and records[edge["source"]]["kind"] == "source",
                    "override target/source")
            target=rules[edge['target']]
            require(edge['question']==r['authority_ref']['question']==target['authority_ref']['question'],
                    'override question outside bounded owner scope')
        if "inherits" in r["failure"]:
            target = r["failure"]["inherits"]
            require(target in rules, "failure inheritance rule required")
            failures[rid] = [target]
        else:
            require(all(records[a]["kind"] == "action" for a in
                        [r["failure"]["action"]] + r["failure"]["alternatives"]), "failure action")
        state = condition(r["when"], records)
        require(state["state"] != "false", f"impossible activation: {rid}")
        if state["analysis"] == "incomplete":
            diagnostics.append({"id": rid, "code": "analysis_incomplete"})
    for graph, label in ((prerequisites, "prerequisite"), (precedence, "precedence"),
                         (failures, "failure inheritance")):
        acyclic(graph, label)
    for rid,r in records.items():
        if r['kind']=='fact':
            require(all(records[s]['kind']=='source' for s in r['sources']), 'fact sources must be sources')
    # Action ordering is checked separately from rule prerequisite semantics.
    ordering = {}
    for r in rules.values():
        ordering.setdefault(r["effect"]["action"], []).extend(r["before"])
    acyclic(ordering, "ordering")
    rows = list(rules.values())
    for i, left in enumerate(rows):
        for right in rows[i + 1:]:
            a, b = left["effect"], right["effect"]
            if (a["actor"], a["action"], a["parameters"]) != (b["actor"], b["action"], b["parameters"]):
                continue
            if (a["modality"] == "must_not") == (b["modality"] == "must_not"):
                continue
            edges = [e for r, other in ((left, right), (right, left))
                     for e in r["overrides"] if e["target"] == other["id"]]
            conditions = [left["when"], right["when"]] + [e["when"] for e in edges]
            space = assignments(conditions, records)
            if space is None:
                diagnostics.append({"id": left["id"], "code": "analysis_incomplete"})
            else:
                require(not any(evaluate(left["when"], row) and evaluate(right["when"], row)
                                and not any(evaluate(e["when"], row) for e in edges)
                                for row in space), "contradictory overlapping modalities")
    return records, sorted(diagnostics, key=lambda d: (d["id"], d["code"]))
