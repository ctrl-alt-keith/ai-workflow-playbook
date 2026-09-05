"""Experimental, read-only projection checks; never a startup or authority engine."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re

KINDS = {"invariant", "trigger", "requirement", "prohibition", "authority", "fallback", "completion_boundary"}
RELATIONS = {"requires", "activates", "before", "overrides", "refers_to"}
EFFECTS = {"obligation", "prohibition", "routing", "authority_source", "completion_condition", "retention"}
CAPABILITIES = {"three-valued", "typed-effects", "canonical-reads", "external-authority", *KINDS, *RELATIONS,
                "eq", "in", "present", "all", "any", "not"}
UNKNOWN = None
MAX_ASSIGNMENTS = 4096


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def index(records, name):
    require(isinstance(records, list), f"{name}: expected list")
    result = {}
    for record in records:
        require(isinstance(record, dict) and isinstance(record.get("id"), str), f"{name}: missing ID")
        require(record["id"] not in result, f"duplicate ID: {record['id']}")
        result[record["id"]] = record
    return result


def typed(value, term):
    return type(value) is (bool if term["type"] == "boolean" else str) and value in term["values"]


def expression(expr, terms):
    """Validate the entire AST, including unreachable branches; return used facts."""
    require(isinstance(expr, dict) and len(expr) == 1, "condition must have one operator")
    op, arg = next(iter(expr.items()))
    if op in {"all", "any"}:
        require(isinstance(arg, list) and arg, f"{op}: nonempty list required")
        return set().union(*(expression(child, terms) for child in arg))
    if op == "not":
        return expression(arg, terms)
    require(op in {"eq", "in", "present"}, f"unsupported condition operator: {op}")
    if op == "present":
        name = arg
    else:
        require(isinstance(arg, list) and len(arg) == 2, f"{op}: expected [term, value]")
        name = arg[0]
    require(isinstance(name, str) and name in terms and terms[name]["role"] == "fact", f"undefined fact: {name}")
    if op != "present":
        values = arg[1] if op == "in" else [arg[1]]
        require(isinstance(values, list) and values, "membership must be nonempty")
        require(all(typed(v, terms[name]) for v in values), f"invalid typed operand: {name}")
    return {name}


def evaluate(expr, facts):
    op, arg = next(iter(expr.items()))
    if op == "not":
        value = evaluate(arg, facts)
        return None if value is None else not value
    if op in {"all", "any"}:
        values = [evaluate(child, facts) for child in arg]
        decisive = False if op == "all" else True
        if decisive in values:
            return decisive
        return None if None in values else not decisive
    name = arg if op == "present" else arg[0]
    if name not in facts:
        return None
    value = facts[name]
    if op == "present":
        return value is not None
    if value is None:
        return False
    return value == arg[1] if op == "eq" else value in arg[1]


def assignments(expressions, terms):
    names = sorted(set().union(*(expression(e, terms) for e in expressions)))
    domains = [terms[n]["values"] + [None] for n in names]
    size = 1
    for domain in domains:
        size *= len(domain)
    require(size <= MAX_ASSIGNMENTS, "predicate proof exceeds bounded capability; simplify or leave unqualified")
    return (dict(zip(names, values)) for values in itertools.product(*domains))


def has_cycle(edges):
    active, done = set(), set()

    def visit(node):
        if node in active:
            return True
        if node in done:
            return False
        active.add(node)
        if any(visit(other) for other in edges.get(node, ())):
            return True
        active.remove(node)
        done.add(node)
        return False

    return any(visit(node) for node in edges)


def source_bytes(root, source):
    path = Path(source["path"])
    require(not path.is_absolute() and ".." not in path.parts, "source path must be repository-relative")
    resolved = (root / path).resolve(strict=True)
    require(resolved.is_relative_to(root.resolve()), "source path escapes repository")
    return resolved.read_bytes()


def blocks(raw, heading):
    """Closed pilot grammar: exact unique ATX heading, ending at the next heading."""
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == heading]
    require(len(matches) == 1, f"missing or ambiguous coverage heading: {heading}")
    start = matches[0]
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"^#{1,6} ", lines[i])), len(lines))
    section = "".join(lines[start:end])
    require("```" not in section and "~~~" not in section, "fenced pilot sections require a reviewed parser extension")
    paragraphs = re.split(r"\n[ \t]*\n", section.strip("\n"))
    return section, [chunk for p in paragraphs for chunk in re.split(r"\n(?=- |[0-9]+\. )", p) if chunk]


def coverage_diff(model, root):
    """Compare ALL blocks in each declared pilot section, including unbound additions."""
    changes = []
    for source in model["sources"]:
        try:
            raw = source_bytes(root, source)
            if digest(raw) != source["sha256"]:
                changes.append({"source": source["id"], "change": "document_drift"})
            if "coverage" not in source:
                continue
            section, current = blocks(raw, source["heading"])
            expected = source["coverage"]
            current_hashes = [digest(c.encode("utf-8")) for c in current]
            old_hashes = [c["sha256"] for c in expected]
            source_text = raw.decode("utf-8")
            offset = source_text.index(section)
            current_lines = []
            for block in current:
                offset = source_text.index(block, offset)
                line = source_text[:offset].count("\n") + 1
                current_lines.append([line, line + block.count("\n")])
                offset += len(block)
            if (current_hashes != old_hashes or digest(section.encode()) != source["section_sha256"] or
                    current_lines != [c["lines"] for c in expected]):
                changes.append({"source": source["id"], "change": "coverage_drift",
                                "expected_blocks": old_hashes, "current_blocks": current_hashes,
                                "current_lines": current_lines, "current_text": current})
        except (OSError, UnicodeError, ContractError) as error:
            changes.append({"source": source["id"], "change": "unavailable", "detail": str(error)})
    return changes


def validate(model, root=None):
    require(type(model.get("schema_version")) is int and model["schema_version"] == 1, "unsupported schema version")
    require(model.get("status") == "experimental" and model.get("complete") is False,
            "pilot cannot claim complete startup coverage")
    sources = index(model.get("sources"), "sources")
    terms = index(model.get("terms"), "terms")
    rules = index(model.get("rules"), "rules")
    cases = index(model.get("evaluation_cases"), "evaluation cases")
    require(len(set(sources) | set(terms) | set(rules)) == len(sources) + len(terms) + len(rules), "duplicate cross-class ID")
    for source in sources.values():
        require(isinstance(source.get("path"), str) and re.fullmatch(r"[a-f0-9]{64}", source.get("sha256", "")), "invalid source binding")
    for term in terms.values():
        require(term.get("role") in {"fact", "effect"}, "term needs fact/effect role")
        require(term.get("type") in {"boolean", "enum"}, "unsupported term type")
        require(isinstance(term.get("values"), list) and term["values"], "term needs finite domain")
        require(all(typed(v, term) for v in term["values"]), "term domain type mismatch")
        require(len({json.dumps(v) for v in term["values"]}) == len(term["values"]), "duplicate domain value")
        require(term["type"] != "boolean" or set(term["values"]) == {False, True}, "Boolean domain must include both values")
        require(term.get("source") in sources and term.get("definition"), "undefined term owner/meaning")
    consumer = model.get("consumer", {})
    require(consumer.get("mode") == "read_only_design" and consumer.get("live_consumption") is False,
            "unsupported consumer: only read-only design, no live consumption")
    require(consumer.get("schema_version") == 1, "consumer schema incompatibility")
    capabilities = set(consumer.get("capabilities", []))
    require(capabilities <= CAPABILITIES, "unsupported consumer capability")
    used = {"three-valued", "typed-effects", "canonical-reads", "external-authority"}
    prerequisite = {rid: [] for rid in rules}
    precedence = {rid: [] for rid in rules}
    failures = {}
    warnings = []
    for rule in rules.values():
        rid = rule["id"]
        require(rule.get("kind") in KINDS, f"unknown rule kind: {rid}")
        used.add(rule["kind"])
        require(rule.get("status") in {"candidate", "retired"}, "invalid rule status")
        require(rule.get("source") in sources, f"missing source: {rid}")
        owner = rule.get("owner", {})
        require(owner.get("source") in sources and owner.get("question"), f"missing scoped owner: {rid}")
        require(isinstance(rule.get("execution_qualified"), bool), "qualification must be explicit")
        expressions = [rule["when"], rule["persistence"]["terminates_when"]]
        require(rule["persistence"].get("starts") and rule["persistence"].get("retains"), "persistence meaning missing")
        require(rule.get("validation") and all(c in cases for c in rule["validation"]) and rule.get("interpretation"),
                f"review linkage missing: {rid}")
        for reference in rule.get("supporting_sources", []):
            require(reference in sources, "missing supporting reference")
        effect = rule["consequence"]
        require(effect.get("kind") in EFFECTS and effect.get("meaning"), "invalid consequence")
        term = terms.get(effect.get("term"))
        require(term and term["role"] == "effect" and typed(effect.get("value"), term), "undefined or mistyped consequence")
        if rule["kind"] == "authority":
            require(effect["kind"] == "authority_source" and rule.get("authority", {}).get("source") in sources
                    and rule["authority"].get("checks"), "authority must identify external source and checks, never permission")
        replacement = rule.get("superseded_by")
        if replacement is not None:
            require(rule["status"] == "retired" and replacement in rules and replacement != rid,
                    "supersession must retire a distinct known ID")
        failure = rule.get("failure", {})
        mode = failure.get("mode")
        require(mode in {"defined", "inherited", "not_applicable", "unresolved"}, "invalid failure mode")
        if mode == "defined":
            require(failure.get("operation") and failure.get("response"), "defined failure needs operation and response")
            expressions.append(failure["when"])
            require(all(s in sources for s in failure.get("fallback_sources", [])), "missing fallback source")
        elif mode == "inherited":
            require(failure.get("from") in rules and failure.get("operation"), "invalid failure inheritance target")
            failures[rid] = [failure["from"]]
        else:
            require(failure.get("reason"), "failure state needs reason")
        for edge in rule["dependencies"]:
            relation, target = edge.get("relation"), edge.get("target")
            require(relation in RELATIONS, "invalid dependency relation")
            require(target in rules or target in sources, f"invalid dependency target: {target}")
            used.add(relation)
            if relation in {"before", "overrides"}:
                require(target in rules, "ordering/precedence target must be a rule")
            if target in rules:
                require(rules[target]["status"] != "retired" or relation == "refers_to", "active dependency on retired ID")
                if relation == "requires":
                    prerequisite[rid].append(target)
                if relation == "before":
                    prerequisite[target].append(rid)
            if relation == "overrides":
                require(edge.get("question") == owner["question"] == rules[target]["owner"]["question"],
                        "precedence is outside its bounded question")
                require(edge.get("source") in sources and edge.get("justification"), "precedence needs source-backed scope justification")
                expressions.append(edge["when"])
                precedence[rid].append(target)
            elif "when" in edge:
                require(relation == "activates", "only activates/overrides edges have conditions")
                expressions.append(edge["when"])
        for expr in expressions:
            expression(expr, terms)
            def operators(node):
                op, arg = next(iter(node.items()))
                return {op} | (set().union(*(operators(c) for c in arg)) if op in {"all", "any"}
                               else operators(arg) if op == "not" else set())
            used |= operators(expr)
        require(any(evaluate(rule["when"], a) is True for a in assignments([rule["when"]], terms)),
                f"impossible predicate: {rid}")
    require(used <= capabilities, f"consumer lacks required capabilities: {sorted(used - capabilities)}")
    require(not has_cycle(prerequisite), "prerequisite/before cycle")
    require(not has_cycle(precedence), "precedence cycle")
    require(not has_cycle(failures), "failure inheritance cycle")
    require(not has_cycle({rid: [r['superseded_by']] for rid, r in rules.items() if r.get('superseded_by')}),
            "supersession cycle")
    require(all(s in sources for s in consumer.get("canonical_reads", [])), "missing consumer canonical read")
    for case in cases.values():
        require(case.get("scenario") and case.get("expected") and case.get("forbidden") and
                case.get("sources") and all(s in sources for s in case["sources"]), "invalid evaluation case")
    for rule in rules.values():
        failure = rule["failure"]
        while failure["mode"] == "inherited":
            failure = rules[failure["from"]]["failure"]
        require(not rule["execution_qualified"] or failure["mode"] == "defined",
                "execution-qualified rule lacks resolved required failure behavior")
        if failure["mode"] == "unresolved":
            warnings.append({"rule": rule["id"], "diagnostic": "unresolved_failure"})
    for left, right in itertools.combinations([r for r in rules.values() if r["status"] != "retired"], 2):
        a, b = left["consequence"], right["consequence"]
        if a["term"] != b["term"]:
            continue
        if a["value"] == b["value"] and a["kind"] == b["kind"]:
            warnings.append({"rules": [left["id"], right["id"]], "diagnostic": "possible_semantic_duplicate_never_auto_merge"})
            continue
        edges = [e for r, other in [(left, right), (right, left)] for e in r["dependencies"]
                 if e["relation"] == "overrides" and e["target"] == other["id"]]
        expressions = [left["when"], right["when"], *(e["when"] for e in edges)]
        for facts in assignments(expressions, terms):
            overlap = evaluate(left["when"], facts) is True and evaluate(right["when"], facts) is True
            require(not overlap or any(evaluate(e["when"], facts) is True for e in edges),
                    f"incompatible overlapping consequences: {left['id']}, {right['id']}")
    for source in sources.values():
        if "coverage" not in source:
            continue
        require(source.get("heading") and re.fullmatch(r"[a-f0-9]{64}", source.get("section_sha256", "")), "missing section binding")
        require(source["coverage"], "missing block inventory")
        for block in source["coverage"]:
            require(block.get("class") in {"normative", "supporting", "unresolved"}, "unknown coverage classification")
            require(re.fullmatch(r"[a-f0-9]{64}", block.get("sha256", "")) and
                    isinstance(block.get("lines"), list) and len(block["lines"]) == 2 and
                    all(type(n) is int and n > 0 for n in block["lines"]) and
                    block["lines"][0] <= block["lines"][1], "invalid block identity")
            require(all(r in rules and rules[r]["source"] == source["id"] for r in block.get("rules", [])), "invalid block mapping")
            require(all(s in sources for s in block.get("canonical_reads", [])), "invalid unprojected dependency")
            require(not block.get("rules") or block["class"] == "normative", "supporting/unresolved text cannot supply normative rules")
            if block["class"] == "normative":
                require(block.get("rules") or block.get("canonical_reads"), "normative clause omitted from coverage")
            if block["class"] == "unresolved":
                require(block.get("canonical_reads"), "unresolved coverage must retain a canonical read")
    if root is not None:
        changes = coverage_diff(model, root)
        require(not changes, "source-binding drift: " + json.dumps(changes))
    return warnings


def select(model, facts):
    """Return a conservative analysis bundle. Nothing here performs or permits actions."""
    warnings = validate(model)
    terms = index(model["terms"], "terms")
    for key, value in facts.items():
        require(key in terms and terms[key]["role"] == "fact", f"unsupported context fact: {key}")
        require(value is None or typed(value, terms[key]), f"invalid context fact type: {key}")
    rules = {r["id"]: r for r in model["rules"] if r["status"] != "retired"}
    states = {rid: evaluate(r["when"], facts) for rid, r in rules.items()}
    selected = {rid for rid, state in states.items() if state is not False}
    reasons = {rid: ["applicable" if states[rid] else "unknown activation retained"] for rid in selected}
    reads = set(model["consumer"]["canonical_reads"])
    for source in model["sources"]:
        for block in source.get("coverage", []):
            reads.update(block.get("canonical_reads", []))
    pending = list(sorted(selected))
    while pending:
        rid = pending.pop()
        rule = rules[rid]
        reads.add(rule["source"])
        reads.add(rule["owner"]["source"])
        reads.update(rule["failure"].get("fallback_sources", []))
        dependencies = [e for e in rule["dependencies"] if e["relation"] != "refers_to"]
        if rule["failure"]["mode"] == "inherited":
            dependencies.append({"relation": "failure", "target": rule["failure"]["from"]})
        for edge in dependencies:
            if "when" in edge and evaluate(edge["when"], facts) is False:
                continue
            target = edge["target"]
            if target not in rules:
                reads.add(target)
            elif target not in selected:
                selected.add(target)
                reasons[target] = [f"{rid}: {edge['relation']}; independent activation={states[target]}"]
                pending.append(target)
    missing = set()
    for rid in selected:
        r = rules[rid]
        exprs = [r["when"], r["persistence"]["terminates_when"]]
        if r["failure"]["mode"] == "defined":
            exprs.append(r["failure"]["when"])
        exprs += [e["when"] for e in r["dependencies"] if "when" in e]
        missing.update(set().union(*(expression(e, terms) for e in exprs)) - facts.keys())
    return {"status": "experimental_analysis_only", "complete": False, "permission": "not_evaluated",
            "rules": [{"rule": rules[rid], "activation": states[rid], "selection": reasons[rid]} for rid in sorted(selected)],
            "unknown_facts": sorted(missing), "canonical_reads": sorted(reads), "diagnostics": warnings,
            "sources": model["sources"], "consumer": model["consumer"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "coverage-diff", "render"])
    parser.add_argument("--input", type=Path, default=Path("docs/experimental-projection/pilot.json"))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--facts", type=Path)
    args = parser.parse_args()
    try:
        raw = args.input.read_bytes()
        model = json.loads(raw)
        if args.command == "coverage-diff":
            validate(model)
            output = {"changes": coverage_diff(model, args.root)}
        else:
            warnings = validate(model, args.root)
            output = {"status": "structurally_valid_not_semantic_equivalence", "diagnostics": warnings}
            if args.command == "render":
                facts = json.loads(args.facts.read_bytes()) if args.facts else {}
                output = select(model, facts)
                output["manifest"] = {"input_sha256": digest(raw), "validator_sha256": digest(Path(__file__).read_bytes()),
                                      "facts_sha256": digest(canonical(facts)), "schema_version": 1,
                                      "selection_sha256": digest(canonical(output))}
        print(canonical(output).decode(), end="")
        return 0
    except (ContractError, OSError, KeyError, TypeError, ValueError) as error:
        print(canonical({"status": "invalid_projection", "error": str(error)}).decode(), end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
