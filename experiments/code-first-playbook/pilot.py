"""Thin, explicit, local CAK-233 shadow compiler interface."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from compiler.load import load_modules, safe_path
from compiler.model import Invalid, canonical, digest, require, shape
from compiler.validate import validate
from compiler.select import select
from compiler.diff import semantic_diff
from compiler.provenance import (read_json, inputs, binding, identity, compare, write_outputs)
from renderers import ai, operator_sre, support
from renderers.clauses import clauses,audit

ROOT = Path(__file__).resolve().parent


def compile_bundle(root, bundle_path):
    bundle = read_json(root, bundle_path)
    shape(bundle, {'semantics','profile','as_of','context','observations','acquisitions','request_complete_contract','evaluation_only'})
    require(type(bundle['evaluation_only']) is bool,'explicit evaluation status')
    require(bundle['request_complete_contract'] is False, 'pilot cannot provide complete executor contract')
    shape(bundle['context'], {'task','attempt','repository','context'})
    require(all(type(v) is str and v for v in bundle['context'].values()), 'exact context required')
    modules, locations = load_modules(root, bundle['semantics'])
    records, diagnostics = validate(modules, locations)
    acquisitions = {}
    for entry in bundle['acquisitions']:
        shape(entry, {'path','sha256','artifact_path'})
        raw = safe_path(root,entry['path']).read_bytes()
        require(digest(raw) == entry['sha256'], 'acquisition raw-byte mismatch')
        evidence = read_json(root,entry['path'])
        artifact=safe_path(root,entry['artifact_path']).read_bytes()
        require(evidence['artifact_id']=='synthetic:'+entry['artifact_path'] and
                evidence['sha256']==digest(artifact),'synthetic acquisition artifact mismatch')
        require(evidence['id'] not in acquisitions, 'duplicate acquisition ID')
        acquisitions[evidence['id']] = evidence
    selected = select(records,bundle['observations'],bundle['context'],bundle['as_of'],acquisitions,diagnostics)
    selected['source_revisions']={u['path']:u['revision'] for u in read_json(root,'provenance/sources.json')['units']}
    profile = read_json(root,bundle['profile'])
    shape(profile, {'operator-sre','support'})
    for layout in profile.values():
        require(type(layout) is list, 'profile layout')
        for item in layout:
            shape(item, {'label','rule'})
            require(item['rule'] in records and records[item['rule']]['kind']=='rule', 'profile rule reference')
            require(type(item['label']) is str and '\n' not in item['label'], 'profile navigation label')
    return bundle, records, locations, selected, profile


def generate(root, bundle_path):
    bundle, records, locations, selected, profile = compile_bundle(root,bundle_path)
    sources = read_json(root,'provenance/sources.json')
    binding(root,sources,None if bundle['evaluation_only'] else records)
    provenance = identity(root,bundle_path,bundle,records,locations)
    normative = clauses(selected)
    outputs = {'ai/startup-retrieval.json': ai.render(selected,normative,provenance),
               'operator-sre/startup-retrieval.md': operator_sre.render(selected,normative,provenance,locations,profile),
               'support/startup-retrieval.md': support.render(selected,normative,provenance,locations,profile),
               'coverage.json':canonical({'status':'mapped_only_external_reads_required','source_bindings':sources,
                                           'selection':selected,'clause_ids':[c['id'] for c in normative]})}
    outputs['index.md'] = (f"# CAK-233 generated shadow previews\n\nEvidence-only persona previews. Recovery alone uses its semantic-authored reader section; all surrounding prose owners remain canonical. No execution or adoption by these previews.\n\nInput commit: `{provenance['input_commit']}`.\n\n- [AI structured clauses](ai/startup-retrieval.json)\n- [Operator/SRE cards](operator-sre/startup-retrieval.md)\n- [Support triage](support/startup-retrieval.md)\n- [Coverage and external owners](coverage.json)\n- [Exact producing identities](provenance.json)\n- [Semantic source](../semantics/startup.yaml)\n\nIncomplete executor contract. Completion grants no authority; permission is not evaluated.\n").encode()
    for audience,path in [('ai','ai/startup-retrieval.json'),('operator-sre','operator-sre/startup-retrieval.md'),('support','support/startup-retrieval.md')]:
        audit(outputs[path],audience,normative)
    outputs['provenance.json'] = canonical({**provenance,'outputs':{p:{'sha256':digest(raw),'bytes':len(raw)} for p,raw in sorted(outputs.items())},'self_hash':'not_recursive; final PR receipt binds this file'})
    return outputs


def bind(root,bundle_path,commit,additional=()):
    require(commit and len(commit)==40 and all(c in '0123456789abcdef' for c in commit), 'explicit commit required')
    files = {}
    for path in [bundle_path]+list(additional):
        files.update(inputs(root,path,read_json(root,path)))
    repo=root.parents[1]
    for path, item in files.items():
        raw=subprocess.run(['git','show',f'{commit}:experiments/code-first-playbook/{path}'],cwd=repo,check=True,capture_output=True).stdout
        require(digest(raw)==item['sha256'],f'input commit byte mismatch: {path}')
    safe_path(root,'provenance/input-commit.json').write_bytes(canonical({'input_commit':commit,'files':files,'binding_method':'exact git object bytes compared at explicit bind; no current HEAD substitution'}))
    return {'status':'bound','input_commit':commit,'files':len(files)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['validate','bind','render','check','source-check','diff','rehearse'])
    parser.add_argument('--bundle',default='cases/baseline.json')
    parser.add_argument('--destination',default='.build/preview')
    parser.add_argument('--input-commit')
    parser.add_argument('--additional-bundle',action='append',default=[])
    parser.add_argument('--old-bundle')
    args=parser.parse_args()
    try:
        if args.command=='bind': result=bind(ROOT,args.bundle,args.input_commit,args.additional_bundle)
        elif args.command=='validate':
            _,records,_,selected,_=compile_bundle(ROOT,args.bundle)
            result={'status':'valid_shadow','rules':len(selected['rules']),'diagnostics':selected['diagnostics'],'permission':'not_evaluated'}
        elif args.command=='source-check':
            _,records,_,_,_=compile_bundle(ROOT,args.bundle)
            result=binding(ROOT,read_json(ROOT,'provenance/sources.json'),records,ROOT.parents[1])
            require(not result['changes'],json.dumps(result))
        elif args.command=='diff':
            require(args.old_bundle,'diff requires explicit --old-bundle and --bundle')
            old=compile_bundle(ROOT,args.old_bundle); new=compile_bundle(ROOT,args.bundle)
            result=semantic_diff(old[1],new[1],old[2],new[2])
        elif args.command=='rehearse':
            from compiler.rehearsal import rehearse
            result=rehearse(ROOT,args.bundle)
        else:
            output=generate(ROOT,args.bundle)
            destination=safe_path(ROOT,args.destination)
            require(destination.is_relative_to(ROOT/'.build'), 'generation destination must be experiment .build/')
            write_outputs(destination,output)
            if args.command=='check':
                errors=compare(ROOT/'generated',output)
                require(not errors,json.dumps(errors))
            result={'status':'byte_identical' if args.command=='check' else 'generated_candidate','files':len(output)}
        print(canonical(result).decode(),end='')
        return 0
    except (Invalid, OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(json.dumps({'status':'invalid_or_unavailable','bundle':args.bundle,'diagnostic':str(error),'permission':'not_evaluated'}),file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
