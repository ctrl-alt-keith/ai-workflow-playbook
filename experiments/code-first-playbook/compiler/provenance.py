"""Exact local inputs and output-set checks, without acquisition or adoption."""

import json
from pathlib import Path
from .load import safe_path
from .model import canonical, digest, require, shape
from .recovery_section import READER, RULE, ACTION, OWNERSHIP, surrounding

OUTPUTS = ('index.md', 'ai/startup-retrieval.json', 'operator-sre/startup-retrieval.md',
           'support/startup-retrieval.md', 'coverage.json', 'provenance.json')


def read_json(root, path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, f'duplicate JSON key: {k}')
            result[k] = v
        return result
    raw = safe_path(root, path).read_bytes()
    require(len(raw) <= 2097152, 'JSON input size limit')
    return json.loads(raw, object_pairs_hook=unique)


def inputs(root, bundle_path, bundle):
    paths = [bundle_path, bundle['profile'], 'provenance/sources.json',
             'provenance/predecessor.json', 'requirements.txt', 'pilot.py'] + bundle['semantics']
    paths += [str(p.relative_to(root)) for folder in ('compiler', 'renderers')
              for p in sorted((root/folder).glob('*.py'))]
    paths += [x['path'] for x in bundle['acquisitions']]
    paths += [x['artifact_path'] for x in bundle['acquisitions']]
    return {p: {'sha256': digest(safe_path(root, p).read_bytes()),
                'bytes': safe_path(root, p).stat().st_size} for p in sorted(paths)}


def binding(root, manifest, records=None, current_repo=None):
    """Frozen accounting is separate from freshness of current operational prose."""
    changes = []
    require(sum(u['unit'] == RULE for u in manifest['units']) == 1,
            'exactly one Recovery ownership binding required')
    for unit in manifest['units']:
        if unit['unit'] == RULE:
            require(unit.get('canonical_body') == OWNERSHIP and unit['blocks'] == [],
                    'Recovery must bind to its semantic action, not historical prose parity')
            if records is not None:
                require(records[RULE]['effect']['action'] == ACTION,
                        'Recovery owning rule no longer selects its canonical action')
        if current_repo is not None:
            raw = safe_path(current_repo, unit['path']).read_bytes()
            if unit['path'] == READER:
                actual, expected = digest(surrounding(raw)), unit['outside_recovery_sha256']
                code = 'surrounding_source_drift'
            else:
                actual, expected = digest(raw), unit['sha256']
                code = 'whole_source_drift'
            if actual != expected:
                changes.append({'unit': unit['unit'], 'code': code, 'path': unit['path']})
        for block in unit['blocks']:
            require(digest(block['text'].encode()) == block['sha256'], 'frozen block hash mismatch')
            if records is not None and block['disposition'] == 'mapped':
                rid, field = block['clause'].split('/')
                require(block['text'].rstrip('\n') in records[rid][field],
                        f"unrepresented bound clause: {unit['unit']} block {block['index']}")
            require(block['disposition'] in ('mapped', 'external', 'supporting'), 'unaccounted block')
            require(block['disposition'] != 'external' or block['external_source'], 'missing external owner')
    return {'status': 'drift' if changes else 'bound', 'current_source_check': current_repo is not None,
            'complete_execution_contract': False, 'changes': changes}


def identity(root, bundle_path, bundle, records, locations):
    bound = read_json(root, 'provenance/input-commit.json')
    shape(bound, {'input_commit', 'files', 'binding_method'})
    require(len(bound['input_commit']) == 40 and all(c in '0123456789abcdef' for c in bound['input_commit']),
            'explicit immutable input commit required')
    actual = inputs(root, bundle_path, bundle)
    require(all(bound['files'].get(p)==v for p,v in actual.items()), 'working input differs from exact input-commit binding; rebind explicitly')
    semantic = {i:r for i,r in records.items() if r['kind'] != 'context'}
    context = {i:r for i,r in records.items() if r['kind'] == 'context'}
    return {'input_commit': bound['input_commit'], 'raw_inputs': actual,
            'source_fidelity':'hypothetical evaluation edit; not baseline parity' if bundle['evaluation_only'] else 'frozen mapped baseline',
            'semantic_sha256': digest(canonical(semantic)), 'context_sha256': digest(canonical(context)),
            'profile_sha256': actual[bundle['profile']]['sha256'],
            'compiler_sha256': digest(canonical({p:v for p,v in actual.items() if p.startswith('compiler/') or p=='pilot.py'})),
            'renderer_sha256': digest(canonical({p:v for p,v in actual.items() if p.startswith('renderers/')})),
            'locations': locations, 'authority_transferred': False}


def compare(root, expected):
    require(set(expected) == set(OUTPUTS), 'renderer output set differs from fixed contract')
    root = Path(root)
    require(not root.is_symlink(), 'symlink output root')
    actual = set()
    if root.exists():
        for p in root.rglob('*'):
            require(not p.is_symlink(), 'symlink output rejected')
            if p.is_file(): actual.add(str(p.relative_to(root)))
    errors = [{'path':p,'code':'missing'} for p in sorted(set(OUTPUTS)-actual)]
    errors += [{'path':p,'code':'extra'} for p in sorted(actual-set(OUTPUTS))]
    errors += [{'path':p,'code':'stale_or_hand_edited'} for p in sorted(actual & set(OUTPUTS))
               if safe_path(root,p).read_bytes() != expected[p]]
    return errors


def write_outputs(root, outputs):
    root = Path(root)
    require(not root.is_symlink(), 'symlink output root')
    for name, raw in outputs.items():
        path = safe_path(root, name)
        require(raw.endswith(b'\n') and b'\r' not in raw and not raw.startswith(b'\xef\xbb\xbf'), 'output encoding')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
