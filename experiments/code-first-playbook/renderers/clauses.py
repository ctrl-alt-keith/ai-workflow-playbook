"""One lossless normative clause serializer; layouts do not reinterpret facts."""

import json
from compiler.model import canonical, digest


def readable(value, indent=0):
    """Lossless field values in readable blocks, without policy paraphrasing."""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if value is None:
        return 'unspecified'
    if isinstance(value, list):
        return '\n'.join('- ' + readable(v).replace('\n','\n  ') for v in value) if value else '(explicitly empty)'
    if isinstance(value, dict):
        return '\n\n'.join(k.replace('_',' ') + ':\n\n' + readable(v) for k,v in value.items())
    return str(value)


def clauses(selection):
    result = []
    for row in selection["rules"]:
        r = row["record"]
        for field in sorted(r.keys() - {"id", "kind", "context"}):
            result.append({"id": f"{r['id']}/{field}", "record_id": r["id"], "field": field,
                           "value": r[field], "text": readable(r[field])})
    for rid, record in selection["vocabulary"].items():
        if record["kind"] == "context":
            continue
        for field in sorted(record.keys() - {"id", "kind"}):
            result.append({"id": f"{rid}/{field}", "record_id": rid, "field": field,
                           "value": record[field], "text": readable(record[field])})
    return result


def header(audience, provenance):
    return {"audience": audience, "topic": "startup-retrieval",
            "status": "experimental_shadow_not_for_execution",
            "coverage": "mapped_clauses_only_external_sources_required",
            "operational_owner": "existing_playbook_prose", "provenance": provenance}


def human(audience, selected, normative, provenance, locations, profile):
    h = header(audience, provenance)
    title = "Operator/SRE workflow cards" if audience == "operator-sre" else "Support triage guide"
    lines = [f"# {title}", "", "Experimental shadow preview. Existing Playbook prose controls.",
             "Incomplete executor contract; no live use or adoption.", "",
             f"Input commit: `{provenance['input_commit']}`.", "",
             f"Exact producing identities: `{digest(canonical(provenance))}` (see provenance.json).", "",
             "## Navigation", ""]
    for item in profile[audience]:
        lines.append(f"- {item['label']}: [view clause](#{item['rule'].replace('.', '-')})")
    if audience == 'support':
        lines += ['', '## Symptom routing', '',
                  'These entry points are navigation. Applicability and authority remain unresolved where the clauses say so.', '']
        selected_by_id = {r['id']:r for r in selected['rules']}
        for item in profile[audience]:
            if item['rule'] not in selected_by_id:
                continue
            row = selected_by_id[item['rule']]
            r = row['record']
            lines += ['### '+item['label'], '',
                      'Applicability: '+row['activation']['state']+'.', '',
                      'Escalation question: '+r['authority_ref']['question'], '',
                      f"[Failure and permitted recovery](#{r['id'].replace('.', '-') }failure) · "
                      f"[Required action](#{r['id'].replace('.', '-') }effect)", '']
    for row in selected["rules"]:
        rid = row["id"]
        lines += ["", f"## {rid}", "", f"Applicability: {row['activation']['state']}.",
                  "Selection: " + "; ".join(row["selection_reasons"]) + ".", ""]
        order = (["when", "effect", "before", "failure", "completion", "authority_ref", "lifetime"]
                 if audience == "operator-sre" else
                 ["when", "authority_ref", "failure", "effect", "completion", "lifetime", "before"])
        owned = [c for c in normative if c["record_id"] == rid]
        owned.sort(key=lambda c: (order.index(c["field"]) if c["field"] in order else 99, c["field"]))
        for c in owned:
            link = source_link(c["record_id"], provenance, locations)
            lines += [f"### {c['id']}", "", f"[Edit semantic source]({link})", "", c["text"], ""]
    lines += ["## Owned vocabulary", ""]
    for c in normative:
        if not c["record_id"].startswith("pb."):
            lines += [f"### {c['id']}", "", f"[Edit semantic source]({source_link(c['record_id'], provenance, locations)})",
                      "", c["text"], ""]
    lines += ["## Unresolved questions and external reads", "", "```json",
              canonical({"facts": selected["fact_reports"], "external_sources": selected["external_sources"],
                         "external_rule_boundaries": selected["external_rule_boundaries"],
                         "exclusions": selected["exclusions"], "diagnostics": selected["diagnostics"],
                         "permission": "not_evaluated"}).decode().rstrip(), "```", "",
              "## Supporting context (non-normative)", ""]
    lines += [r["body"] for r in selected["vocabulary"].values() if r["kind"] == "context"]
    return ("\n".join(lines).rstrip() + "\n").encode()


def source_link(rid, provenance, locations):
    return (f"https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/{provenance['input_commit']}/"
            f"experiments/code-first-playbook/{locations[rid]['path']}")
