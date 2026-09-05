"""Closed pilot vocabulary, typed expressions and declared reference sites."""

import hashlib
import itertools
import json

LANGUAGE = "playbook-semantics/0"
MAX_ASSIGNMENTS = 4096
UNITS = {
    "pb.startup-floor", "pb.conditional-activation", "pb.mode-persistence",
    "pb.retrieval-triggers", "pb.claim-verification", "pb.retrieval-recovery",
}
COMMON = {"id", "kind", "owner", "status", "references"}
FIELDS = {
    "source": {"definition", "path"},
    "term": {"definition", "type", "values"},
    "fact": {"question", "type", "values", "resolution_class", "evaluators",
             "sources", "freshness"},
    "action": {"does", "parameters", "does_not_establish", "action_kind"},
    "rule": {"unit", "when", "effect", "requires", "activates", "before",
             "overrides", "lifetime", "failure", "authority_ref", "completion", "context"},
    "context": {"body"},
}


class Invalid(ValueError):
    """Invalid input, never a universal policy prohibition."""


def require(ok, message):
    if not ok:
        raise Invalid(message)


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def shape(obj, required, optional=()):
    require(type(obj) is dict, "expected mapping")
    require(set(required) <= obj.keys(), f"missing fields: {sorted(set(required) - obj.keys())}")
    require(obj.keys() <= set(required) | set(optional),
            f"unsupported fields: {sorted(obj.keys() - set(required) - set(optional))}")


def strings(values):
    require(type(values) is list and all(type(v) is str and v for v in values),
            "expected string list")
    require(len(values) == len(set(values)), "duplicate list value")


def typed(value, declaration):
    return (type(value) is (bool if declaration["type"] == "boolean" else str)
            and value in declaration["values"])


def expression(expr, records, depth=0):
    require(depth <= 24, "expression depth limit")
    require(type(expr) is dict and len(expr) == 1, "one expression operator required")
    op, arg = next(iter(expr.items()))
    if op in ("all", "any"):
        require(type(arg) is list and bool(arg), "empty Boolean expression")
        return set().union(*(expression(e, records, depth + 1) for e in arg))
    if op == "not":
        return expression(arg, records, depth + 1)
    require(op in ("is", "in"), f"unsupported operator: {op}")
    require(type(arg) is list and len(arg) == 2, "expected fact and operand")
    fid, value = arg
    require(type(fid) is str and fid in records and records[fid]["kind"] == "fact",
            f"undefined fact: {fid}")
    values = value if op == "in" else [value]
    require(type(values) is list and bool(values), "empty domain")
    require(all(typed(v, records[fid]) for v in values), f"mistyped operand: {fid}")
    return {fid}


def evaluate(expr, assignment):
    op, arg = next(iter(expr.items()))
    if op == "all":
        return all(evaluate(e, assignment) for e in arg)
    if op == "any":
        return any(evaluate(e, assignment) for e in arg)
    if op == "not":
        return not evaluate(arg, assignment)
    return assignment[arg[0]] == arg[1] if op == "is" else assignment[arg[0]] in arg[1]


def assignments(expressions, records, fixed=None):
    fixed = fixed or {}
    names = sorted(set().union(*(expression(e, records) for e in expressions)) - fixed.keys())
    domains = [records[n]["values"] for n in names]
    size = 1
    for domain in domains:
        size *= len(domain)
    if size > MAX_ASSIGNMENTS:
        return None
    return ({**fixed, **dict(zip(names, row))} for row in itertools.product(*domains))


def condition(expr, records, fixed=None):
    rows = assignments([expr], records, fixed)
    if rows is None:
        return {"state": "conditional", "analysis": "incomplete"}
    results = {evaluate(expr, row) for row in rows}
    state = "true" if results == {True} else "false" if results == {False} else "conditional"
    return {"state": state, "analysis": "complete"}


def expressions(record):
    if record["kind"] != "rule":
        return []
    result = [("when", record["when"]), ("lifetime.ends_when", record["lifetime"]["ends_when"])]
    for key in ("activates", "overrides"):
        result.extend((f"{key}.{i}.when", edge["when"]) for i, edge in enumerate(record[key]))
    if "when" in record["failure"]:
        result.append(("failure.when", record["failure"]["when"]))
    if "when" in record["completion"]:
        result.append(("completion.when", record["completion"]["when"]))
    return result


def reference_sites(record):
    """Only declared semantic references; no guesses from natural-language words."""
    sites = [("owner", record["owner"])]
    sites += [(f"references.{i}", x) for i, x in enumerate(record["references"])]
    if record["kind"] == "fact":
        sites += [(f"sources.{i}", x) for i, x in enumerate(record["sources"])]
    if record["kind"] == "action":
        sites += [(f"parameters.{i}.type", p["type"]) for i, p in enumerate(record["parameters"])]
    if record["kind"] == "rule":
        sites.append(("effect.action", record["effect"]["action"]))
        for key in ("requires", "before", "context"):
            sites += [(f"{key}.{i}", x) for i, x in enumerate(record[key])]
        for key in ("activates", "overrides"):
            for i, edge in enumerate(record[key]):
                sites.append((f"{key}.{i}.target", edge["target"]))
                if key == "overrides":
                    sites.append((f"{key}.{i}.source", edge["source"]))
        failure = record["failure"]
        if "inherits" in failure:
            sites.append(("failure.inherits", failure["inherits"]))
        else:
            sites.append(("failure.action", failure["action"]))
            sites += [(f"failure.alternatives.{i}", x) for i, x in enumerate(failure["alternatives"])]
        for key in ("evidence", "boundary"):
            sites.append((f"completion.{key}", record["completion"][key]))
        sites.append(("authority_ref.source", record["authority_ref"]["source"]))
        for path, expr in expressions(record):
            def walk(node, prefix):
                op, arg = next(iter(node.items()))
                if op in ("all", "any"):
                    for i, child in enumerate(arg):
                        yield from walk(child, f"{prefix}.{op}.{i}")
                elif op == "not":
                    yield from walk(arg, prefix + ".not")
                else:
                    yield (prefix + "." + op, arg[0])
            sites.extend(walk(expr, path))
    return sorted(sites)
