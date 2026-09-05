"""Generate only Recovery from its canonical action; preserve the surrounding document."""

import argparse
import copy
import difflib
from pathlib import Path
import re
import sys

from compiler.load import load_modules, safe_path
from compiler.model import Invalid, canonical, digest, reference_sites, require
from compiler.validate import validate
from compiler.diff import semantic_diff
from compiler.provenance import binding, read_json, write_outputs
from compiler.recovery_section import (READER, RULE, ACTION, SOURCE, OWNERSHIP,
                                       BEGIN, END, replace)

ROOT = Path(__file__).resolve().parent
MODULES = ['semantics/startup.yaml', 'semantics/source-retrieval.yaml']
PROVENANCE = 'recovery/generated/provenance.json'
AUTHOR_HINT = 'edit experiments/code-first-playbook/' + SOURCE + ' (' + ACTION + '/does), then run make code-first-recovery-render'


def corpus(root=ROOT):
    modules, locations = load_modules(root, MODULES)
    records, _ = validate(modules, locations)
    require(locations[ACTION]['path'] == SOURCE, 'Recovery canonical source moved; review ownership mapping')
    return records, locations


def envelope(records):
    """Guard every dependency except the editable section body; no judgment pruning.

    Other rule owners remain external. Their records are guarded, but we do not
    traverse their execution contracts and claim to render those documents.
    """
    pending, seen = [RULE], set()
    while pending:
        rid = pending.pop()
        if rid in seen:
            continue
        seen.add(rid)
        if records[rid]['kind'] == 'rule' and rid != RULE:
            continue
        pending.extend(target for _, target in reference_sites(records[rid]))
    guarded = copy.deepcopy({rid: records[rid] for rid in sorted(seen)})
    guarded[ACTION].pop('does')
    return {rid: digest(canonical(record)) for rid, record in guarded.items()}


def section(records):
    """Only collapse blank lines separating list siblings; preserve all tokens."""
    paragraphs = records[ACTION]['does'].rstrip().split('\n\n')
    result = paragraphs[0]
    for previous, paragraph in zip(paragraphs, paragraphs[1:]):
        siblings = all(re.match(r'(?:- |[1-9][0-9]*\. )', p) for p in (previous, paragraph))
        result += ('\n' if siblings else '\n\n') + paragraph
    return result + '\n'


def render(records, contract):
    require(contract['ownership'] == OWNERSHIP, 'wrong Recovery ownership mapping')
    require(contract['envelope_sha256'] == envelope(records),
            'unrendered recovery envelope changed; review its section mapping before regeneration')
    body = section(records)
    require(not re.search(r'^#{1,2} ', body, re.MULTILINE)
            and '<!-- generated:' not in body and '<!-- /generated:' not in body,
            'Recovery body exceeds its section boundary; stop for representation review')
    return (BEGIN +
            b'> Generated section. Edit the [semantic source](../experiments/code-first-playbook/semantics/source-retrieval.yaml) (`action.retrieval-recovery/does`).\n\n'
            + body.encode() + b'\n' + END)


def generate(root=ROOT):
    records, _ = corpus(root)
    sources = read_json(root, 'provenance/sources.json')
    binding(root, sources, records)
    contract = read_json(root, 'recovery/contract.json')
    generated = render(records, contract)
    paths = MODULES + ['recovery.py', 'recovery/contract.json',
                       'requirements.txt', 'provenance/sources.json']
    paths += [str(p.relative_to(root)) for p in sorted((root / 'compiler').glob('*.py'))]
    provenance = {
        'status': 'generated_section', 'ownership': OWNERSHIP,
        'envelope_sha256': envelope(records),
        'scope': 'Only the Recovery body is semantic-authored; surrounding owners remain external.',
        'source_binding': next(u for u in sources['units'] if u['unit'] == RULE),
        'inputs': {p: {'bytes': len(raw), 'sha256': digest(raw)} for p in sorted(paths)
                   for raw in [safe_path(root, p).read_bytes()]},
        'output': {'section': OWNERSHIP['reader'], 'bytes': len(generated),
                   'sha256': digest(generated)},
        'identity': 'Section bytes exclude the unchanged hand-maintained document shell; PR binds exact commit.',
        'authority': 'Generation records the declared ownership model, never promotion or merge permission.',
    }
    return generated, canonical(provenance)


def check(root=ROOT):
    generated, provenance = generate(root)
    document = safe_path(root.parents[1], READER).read_bytes()
    require(replace(document, generated) == document,
            'stale_or_hand_edited: ' + READER + '#recovery; ' + AUTHOR_HINT)
    directory = safe_path(root, 'recovery/generated')
    require({p.name for p in directory.iterdir()} == {'provenance.json'},
            'missing or extra Recovery output; only the reader section and provenance are active')
    require(safe_path(root, PROVENANCE).read_bytes() == provenance,
            'stale_or_hand_edited: ' + PROVENANCE + '; ' + AUTHOR_HINT)
    return {'status': 'byte_identical', 'ownership': OWNERSHIP}


def write(root=ROOT):
    generated, provenance = generate(root)
    path = safe_path(root.parents[1], READER)
    # Resolve and validate both destinations before any explicit generation write.
    safe_path(root, PROVENANCE)
    document = replace(path.read_bytes(), generated)
    path.write_bytes(document)
    write_outputs(root, {PROVENANCE: provenance})
    return {'status': 'generated_section', 'ownership': OWNERSHIP}


def definition_probe(records, locations):
    """A hypothetical edit exercises the existing semantic diff, not new policy."""
    changed = copy.deepcopy(records)
    changed[ACTION]['does'] += '\nSIMULATION: Record the correction location for mock review.\n'
    report = semantic_diff(records, changed, locations, locations)
    # Exercise the real renderer as well as the shared definition-diff path.
    contract = read_json(ROOT, 'recovery/contract.json')
    prose_diff = ''.join(difflib.unified_diff(
        render(records, contract).decode().splitlines(keepends=True),
        render(changed, contract).decode().splitlines(keepends=True),
        fromfile=OWNERSHIP['reader'], tofile=OWNERSHIP['reader'] + ' (hypothetical)'))
    return {'simulation_only': True, 'shared_semantic_diff': report,
            'generated_prose_diff': prose_diff,
            'reader_effects': [
                {'event': event['id'], 'output': OWNERSHIP['reader'],
                 'effect': 'body_changed' if event['id'] == ACTION else 'envelope_review_required'}
                for event in report['events'] if RULE in event['affected_rules']]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['render', 'check', 'source-check', 'diff'])
    args = parser.parse_args()
    try:
        if args.command == 'render':
            result = write()
        elif args.command == 'check':
            result = check()
        elif args.command == 'source-check':
            records, _ = corpus()
            result = binding(ROOT, read_json(ROOT, 'provenance/sources.json'), records, ROOT.parents[1])
            require(not result['changes'], 'current external prose bindings drifted: ' + str(result['changes']))
            result['generated_recovery'] = check()['status']
        else:
            result = definition_probe(*corpus())
        print(canonical(result).decode(), end='')
        return 0
    except (Invalid, OSError, ValueError, KeyError, TypeError, IndexError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
