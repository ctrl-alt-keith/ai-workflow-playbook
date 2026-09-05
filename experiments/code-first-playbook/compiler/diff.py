"""First-class normative definition changes and old/new reference fan-out."""

from collections import defaultdict
from .model import canonical, reference_sites


def semantic_diff(old, new, old_locations=None, new_locations=None):
    reverse = defaultdict(set)
    sites = defaultdict(set)
    for records in (old, new):
        for rid, record in records.items():
            for site, target in reference_sites(record):
                reverse[target].add(rid)
                sites[target].add((rid, site))
    events = []
    for rid in sorted(old.keys() | new.keys()):
        a, b = old.get(rid), new.get(rid)
        old_location=(old_locations or {}).get(rid)
        new_location=(new_locations or {}).get(rid)
        if canonical(a) == canonical(b) and old_location == new_location:
            continue
        record = b or a
        if canonical(a) == canonical(b):
            category = "source_location_changed"
        elif a is None:
            category = "added"
        elif b is None:
            category = "removed"
        elif a["kind"] != "context" and b["kind"] == "context":
            category = "normative_removed_to_context"
        elif a["kind"] == b["kind"] == "context":
            category = "supporting_context_only"
        elif a["kind"] == "action" or b["kind"] == "action":
            category = "boundary_completion_definition_changed" if record.get("action_kind") != "behavior" else "action_definition_changed"
        elif a["kind"] == "term" or b["kind"] == "term":
            category = "term_definition_changed"
        else:
            category = "semantic_record_changed"
        impacted, pending = set(), [rid]
        while pending:
            target = pending.pop()
            for parent in sorted(reverse[target]):
                if parent not in impacted:
                    impacted.add(parent); pending.append(parent)
        impacted.add(rid)
        rules = sorted(i for i in impacted if (new.get(i) or old.get(i))["kind"] == "rule")
        dimensions = sorted(k for k in (a or {}).keys() | (b or {}).keys()
                            if canonical((a or {}).get(k)) != canonical((b or {}).get(k)))
        events.append({"id": rid, "owner": record["owner"], "category": category,
                       "dimensions": dimensions, "old": a, "new": b,
                       "old_location": old_location, "new_location": new_location,
                       "impact": "context_only" if category == "supporting_context_only"
                       else "unresolved_semantic_impact",
                       "direct_reference_sites": [{"id": i, "site": s} for i, s in sorted(sites[rid])],
                       "affected_ids": sorted(impacted), "affected_rules": rules,
                       "affected_outputs": ["ai/startup-retrieval.json", "operator-sre/startup-retrieval.md",
                                            "support/startup-retrieval.md"] if rules else []})
        if category == 'source_location_changed':
            # A copied evaluation bundle moves every file. Preserve relocation
            # evidence without mislabeling that noise as normative fan-out.
            events[-1].update(old=None,new=None,impact='source_provenance_only',affected_ids=[],
                              affected_rules=[],affected_outputs=[],direct_reference_sites=[])
        elif 'pb.retrieval-recovery' in rules:
            events[-1]['affected_outputs'].append('docs/source-first-retrieval.md#recovery')
    return {"status": "evidence_only", "events": events, "permission": "not_evaluated"}
