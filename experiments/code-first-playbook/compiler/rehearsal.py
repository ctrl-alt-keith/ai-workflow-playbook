"""One fixed synthetic transition ledger; never a runtime authority controller."""

from .model import canonical,digest,reference_sites,require,shape
from .provenance import read_json


def unit_body(records, selected, normative):
    """Use the real shared clauses, retaining other rule owners as external."""
    unit='pb.retrieval-recovery'
    required={unit};todo=[unit];external=set()
    while todo:
        for _,target in reference_sites(records[todo.pop()]):
            if records[target]['kind']=='rule' and target != unit:
                external.add(target)
            elif target not in required:
                required.add(target);todo.append(target)
    fields=[c for c in normative if c['record_id'] in required]
    require(any(c['id']=='action.retrieval-recovery/does' for c in fields),'complete recovery definition missing')
    text='\n\n'.join(c['id']+'\n\n'+c['text'] for c in fields)
    return (text+'\n\nExternal rule owners: '+', '.join(sorted(external))+'\n').encode(),fields


def verify_fixture(fixture,bodies):
    """Validate only the named rehearsal steps and atomic before/after snapshots."""
    shape(fixture,{'simulation_only','unit','steps'})
    require(fixture['simulation_only'] is True and fixture['unit']=='pb.retrieval-recovery','simulation scope')
    expected=['shadow','forward','compiler-rollback','content-rollback','language-inadequacy','reverse',
              'stale-rejected','restore-old-policy','new-body-reverse']
    require([s['step'] for s in fixture['steps']]==expected,'fixed rehearsal coverage')
    ledger=[]
    for s in fixture['steps']:
        shape(s,{'step','simulation_only','before','after','decision','body','body_sha256','compatible','blocked','impact'})
        require(s['simulation_only'] is True,'live rehearsal input')
        for snap in (s['before'],s['after']):
            shape(snap,{'simulation_only','owner','routing','semantic_status','body_status','other_owner'})
            require(snap['simulation_only'] is True,'live snapshot')
            require(snap['owner'] in ('prose:P0','semantic:S0','semantic:S1','prose:G0','prose:G1'),'unknown mock owner')
            require(snap['routing']==snap['owner'],'partial/mixed routing')
            require(snap['other_owner']=='unchanged:startup','unrelated owner changed')
            if snap['owner'].startswith('semantic:'):
                require(snap['body_status']=='derivative' and snap['semantic_status']=='active','dual owner')
            else:
                require(snap['semantic_status'] in ('shadow','retired') and snap['body_status']=='hand-maintained','dual owner')
        changed=s['before']['owner']!=s['after']['owner']
        if s['blocked']:
            require(s['before']==s['after'],'blocked transition changed owner')
        if changed:
            d=s['decision'];shape(d,{'simulation_only','actor','transition','previous_owner','next_owner','unit','body_sha256','retirement','routing_change'})
            require(d['simulation_only'] is True and d['actor']=='mock-human','missing independent mock human')
            require(d['transition']=='simulation:'+s['step'] and d['previous_owner']==s['before']['owner'] and
                    d['next_owner']==s['after']['owner'] and d['unit']==fixture['unit'],'decision scope mismatch')
            require(d['routing_change']==s['after']['routing'],'decision routing mismatch')
        body=s['body']
        require(body in bodies and s['body_sha256']==digest(bodies[body]),'stale/incomplete body identity')
        if changed:require(s['decision']['body_sha256']==s['body_sha256'],'decision body mismatch')
        if s['step']=='forward':
            require(s['before']['owner']=='prose:P0' and s['after']['owner']=='semantic:S0' and body=='G0','forward ownership')
        elif s['step']=='compiler-rollback':
            require(s['compatible'] is True and s['before']==s['after'] and s['after']['owner']=='semantic:S0','compiler rollback may not change semantics')
        elif s['step']=='content-rollback':
            require(s['before']['owner']=='semantic:S1' and s['after']['owner']=='semantic:S0' and s['compatible'] is True,'content rollback ownership')
        elif s['step']=='language-inadequacy':
            require(s['blocked'] is True and s['after']['owner']=='semantic:S1','inadequacy cannot promote prose')
        elif s['step']=='stale-rejected':
            require(s['blocked'] is True and s['after']['owner']=='semantic:S1' and body=='G0','stale reversal must stay blocked')
        elif s['step'] in ('reverse','restore-old-policy','new-body-reverse'):
            require(s['after']['owner']=='prose:'+body and s['after']['semantic_status']=='retired','reverse retirement')
            require(s['decision']['retirement']=='tombstone:pb.retrieval-recovery','reverse tombstone missing')
            if s['step']=='new-body-reverse':require(body=='G1' and s['before']['owner']=='semantic:S1','new body under current semantic owner')
            if s['step']=='restore-old-policy':require(body=='G0' and s['impact']=='explicitly reviewed restoration of old policy','old policy impact undisclosed')
        ledger.append({'simulation_only':True,'step':s['step'],'before':s['before']['owner'],'after':s['after']['owner'],
                       'blocked':s['blocked'],'body_sha256':s['body_sha256'],'decision':s['decision'],'authority_transferred':False})
    return {'simulation_only':True,'status':'rehearsed_fixture_only','owner_gaps':0,'dual_owners':0,'derivative_promotions':0,'ledger':ledger}


def rehearse(root,bundle_path):
    from pilot import compile_bundle,generate
    from renderers.clauses import clauses
    _,records,_,selected,_=compile_bundle(root,bundle_path)
    # Generate through the exact bound source/renderer path first.
    outputs=generate(root,bundle_path)
    g0,fields=unit_body(records,selected,clauses(selected))
    sources=read_json(root,'provenance/sources.json')
    recovery=next(s for s in sources['units'] if s['unit']=='pb.retrieval-recovery')
    for block in recovery['blocks']:
        if block['disposition']=='mapped':
            require(block['text'].rstrip('\n').encode() in g0,'incomplete recovery body')
    # One hypothetical S1 definition edit, not a real policy edit or authoring round.
    import copy
    modified=copy.deepcopy(selected)
    modified['vocabulary']['action.retrieval-recovery']['does']+='\nSIMULATION S1: Record the correction location for mock review.\n'
    g1,_=unit_body(records,modified,clauses(modified))
    fixture=read_json(root,'cases/authority-rehearsal.json')
    result=verify_fixture(fixture,{'G0':g0,'G1':g1})
    result.update(body_hashes={'G0':digest(g0),'G1':digest(g1)},clause_ids=[c['id'] for c in fields],
                  producing_provenance_sha256=digest(outputs['provenance.json']),
                  ambiguity='Only a mock single-unit ledger. No real consumer, routing edit or authority transition.')
    return result
