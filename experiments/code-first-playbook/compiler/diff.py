"""First-class normative definition changes and old/new reference fan-out."""

from collections import defaultdict
from .model import canonical, reference_sites, require


def semantic_diff(old, new, old_locations=None, new_locations=None, reader_mappings=()):
    """Report semantic fan-out and explicitly declared generated-reader effects."""
    readers = {}
    records = old | new
    for mapping in reader_mappings:
        require(type(mapping) is dict and set(mapping) == {'clause', 'reader'},
                'malformed reader mapping')
        clause, reader = mapping['clause'], mapping['reader']
        require(type(clause) is str and clause.count('/') == 1, 'malformed reader mapping clause')
        require(type(reader) is str and '#' in reader, 'malformed reader mapping reader')
        record_id, field = clause.split('/')
        require(record_id in records and field in records[record_id], 'stale reader mapping clause: ' + clause)
        require(clause not in readers, 'duplicate reader mapping clause: ' + clause)
        readers[clause] = reader
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
        changed_clauses = [rid + '/' + field for field in dimensions
                           if rid + '/' + field in readers]
        events.append({"id": rid, "owner": record["owner"], "category": category,
                       "dimensions": dimensions, "old": a, "new": b,
                       "old_location": old_location, "new_location": new_location,
                       "impact": "context_only" if category == "supporting_context_only"
                       else "unresolved_semantic_impact",
                       "direct_reference_sites": [{"id": i, "site": s} for i, s in sorted(sites[rid])],
                       "affected_ids": sorted(impacted), "affected_rules": rules,
                       "affected_reader_outputs": sorted({readers[clause] for clause in changed_clauses}),
                       "reader_mapping_status": "mapped" if changed_clauses else "no_direct_reader_clause"})
        if category == 'source_location_changed':
            # A copied evaluation bundle moves every file. Preserve relocation
            # evidence without mislabeling that noise as normative fan-out.
            events[-1].update(old=None,new=None,impact='source_provenance_only',affected_ids=[],
                              affected_rules=[],affected_reader_outputs=[],direct_reference_sites=[],
                              reader_mapping_status='not_applicable')
    return {"status": "evidence_only", "events": events, "permission": "not_evaluated"}
