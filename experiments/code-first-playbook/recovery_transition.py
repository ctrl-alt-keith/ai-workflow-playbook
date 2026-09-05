"""Rehearse the exact committed cutover/reverse using an isolated Git index."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from compiler.load import parse
from compiler.model import Invalid, canonical, digest, require
from compiler.recovery_section import READER, RULE, ACTION, SOURCE, OWNERSHIP, parts, surrounding
from recovery import ROOT, check, corpus, section

PREFIX = 'experiments/code-first-playbook/'


def git(repo, *args, data=None, env=None):
    return subprocess.run(['git', *args], cwd=repo, input=data, env=env,
                          check=True, capture_output=True).stdout


def rehearse(base_ref, head_ref):
    repo = ROOT.parents[1]
    base = git(repo, 'rev-parse', '--verify', base_ref + '^{commit}').decode().strip()
    head = git(repo, 'rev-parse', '--verify', head_ref + '^{commit}').decode().strip()
    require(base != head, 'transition requires distinct base and implementation identities')
    git(repo, 'merge-base', '--is-ancestor', base, head)
    require(git(repo, 'rev-parse', 'HEAD').decode().strip() == head, 'rehearse the checked-out head')
    git(repo, 'diff', '--exit-code', head, '--')
    require(not git(repo, 'ls-files', '--others', '--exclude-standard'), 'untracked implementation files')
    check()

    def raw(commit, path):
        return git(repo, 'show', commit + ':' + path)

    previous = raw(base, READER)
    current = raw(head, READER)
    records, _ = corpus()
    old_module = parse(raw(base, PREFIX + SOURCE))
    old_action = next(r for r in old_module['records'] if r['id'] == ACTION)
    require(old_action == records[ACTION], 'this cutover must preserve the exact semantic action')
    require(parts(previous)[1].strip() == section(records).encode().strip(),
            'base Recovery meaning differs; do not restore old policy implicitly')
    require(surrounding(previous) == surrounding(current), 'surrounding reader content changed')

    def binding_at(commit):
        sources = json.loads(raw(commit, PREFIX + 'provenance/sources.json'))
        return next(u for u in sources['units'] if u['unit'] == RULE)

    require('canonical_body' not in binding_at(base) and binding_at(base)['blocks'],
            'base is not the pre-transition prose ownership model')
    require(binding_at(head)['canonical_body'] == OWNERSHIP and not binding_at(head)['blocks'],
            'head retains a second Recovery prose binding')
    require(not git(repo, 'ls-tree', '--name-only', head, '--',
                    PREFIX + 'recovery/generated/recovery.md'), 'shadow reader still active')

    patch = git(repo, 'diff', '--binary', '--full-index', base, head, '--')
    expected_head = git(repo, 'rev-parse', head + '^{tree}').decode().strip()
    expected_base = git(repo, 'rev-parse', base + '^{tree}').decode().strip()
    # Repository-native test/index state, never a checkout or an authority change.
    build = ROOT / '.build'
    build.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='recovery-transition-', dir=build) as directory:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(directory) / 'index'))
        git(repo, 'read-tree', base, env=env)
        git(repo, 'apply', '--cached', '--check', data=patch, env=env)
        git(repo, 'apply', '--cached', data=patch, env=env)
        forward = git(repo, 'write-tree', env=env).decode().strip()
        require(forward == expected_head, 'forward tree differs from exact implementation')
        git(repo, 'apply', '--cached', '--reverse', '--check', data=patch, env=env)
        git(repo, 'apply', '--cached', '--reverse', data=patch, env=env)
        reverse = git(repo, 'write-tree', env=env).decode().strip()
        require(reverse == expected_base, 'reverse did not restore the exact base tree')
    return {
        'status': 'exact_forward_and_reverse_passed', 'base': base, 'head': head,
        'patch': {'bytes': len(patch), 'sha256': digest(patch)},
        'forward_tree': forward, 'reverse_tree': reverse,
        'previous_owner': READER + '#recovery (hand-maintained)',
        'implementation_owner': OWNERSHIP,
        'body_words': len(section(records).split()),
        'surrounding_reader_bytes': 'unchanged',
        'rollback': 'Reverse this exact base..head patch atomically in a dedicated rollback PR; '
                    'after squash merge, git revert the verified integrated transition commit. '
                    'Later semantic or overlapping changes require a fresh reverse decision and rehearsal.',
        'authority': 'Isolated Git index only; no live cutover, promotion, merge or rollback permission.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-ref', required=True)
    parser.add_argument('--head-ref', required=True)
    args = parser.parse_args()
    try:
        print(canonical(rehearse(args.base_ref, args.head_ref)).decode(), end='')
        return 0
    except (Invalid, OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(str(error))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
