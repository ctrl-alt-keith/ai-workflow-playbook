"""Shared source-binding and safe generated-output helpers for Recovery."""

import json
from pathlib import Path
from .load import safe_path
from .model import digest, require
from .recovery_section import READER, RULE, ACTION, OWNERSHIP, surrounding


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


def write_outputs(root, outputs):
    root = Path(root)
    require(not root.is_symlink(), 'symlink output root')
    for name, raw in outputs.items():
        path = safe_path(root, name)
        require(raw.endswith(b'\n') and b'\r' not in raw and not raw.startswith(b'\xef\xbb\xbf'), 'output encoding')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
