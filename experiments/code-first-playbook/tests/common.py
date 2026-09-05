import copy
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pilot import compile_bundle
from compiler.select import select


def corpus():
    return compile_bundle(ROOT,'cases/baseline.json')


def observation(b, fid='fact.repository_work', value=False, state='known', **changes):
    result={'fact_id':fid,'state':state,'value':value,'evaluator':'controller',
            'resolution_class':'external_judgment','basis':None,'scope':copy.deepcopy(b['context']),
            'freshness':{'observed_at':b['as_of']},'rationale':'Synthetic controller assertion; judgment remains unresolved.',
            'diagnostics':[] if state=='known' else ['synthetic-'+state]}
    result.update(changes)
    return result


def proof(b,value=False):
    raw=b'Explicitly synthetic source-read observation fixture.\n'
    from compiler.model import digest
    a={'id':'synthetic:exact-read','source':'source.start','fact_id':'fact.exact-source-read',
       'value':value,'evaluator':'fixture-acquirer','scope':copy.deepcopy(b['context']),
       'observed_at':b['as_of'],'checked_claim':'Only exact-source-read; no adequacy/application claim',
       'verified':True,'artifact_id':'synthetic:fixture-bytes','sha256':digest(raw)}
    o=observation(b,a['fact_id'],value,evaluator=a['evaluator'],resolution_class='observed_evidence',basis=a['id'])
    return o,{a['id']:a}


def choose(records, observations=(), acquisitions=None):
    b=corpus()[0]
    return select(records,list(observations),b['context'],b['as_of'],acquisitions or {})


def by_id(s): return {r['id']:r for r in s['rules']}
