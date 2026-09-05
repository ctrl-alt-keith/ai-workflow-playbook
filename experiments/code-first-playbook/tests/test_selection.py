import copy
import unittest
from common import corpus, observation, proof, choose, by_id
from compiler.model import Invalid


class Selection(unittest.TestCase):
    def setUp(self): self.b,self.r,self.l,self.s,self.p=corpus()

    def test_01_03_startup_continuation_change(self):
        for fid in ('repository_work','startup_succeeded','repository_changed','material_change'):
            with self.subTest(fid=fid):
                s=choose(self.r,[observation(self.b,'fact.'+fid,True)])
                self.assertEqual(set(by_id(s)),set(by_id(self.s)))
                self.assertEqual(by_id(s)['pb.startup-floor']['activation']['state'],'conditional')
                self.assertFalse(s['complete_execution_contract'])

    def test_04_06_conditional_live_partial(self):
        s=choose(self.r,[observation(self.b,'fact.verification_complete',False)])
        r=by_id(s)['pb.conditional-activation']
        self.assertTrue(all(v['state']=='conditional' for k,v in r['conditions'].items() if k.startswith('activates.')))
        self.assertEqual(by_id(s)['pb.claim-verification']['conditions']['failure.when']['state'],'conditional')
        for source in ('source.maintenance','source.lifecycle','source.ecosystem'):
            self.assertIn(source,s['external_sources'])

    def test_07_08_transport_recovery_and_bounded_stop(self):
        text=self.r['action.retrieval-recovery-failure']['does']
        self.assertIn('no permitted qualified authoritative route remains',text)
        self.assertIn('available approved connector',text)
        self.assertIn('not premature failure',text)
        s=choose(self.r,[observation(self.b,'fact.source_available',False)])
        self.assertEqual(by_id(s)['pb.retrieval-recovery']['conditions']['failure.when']['state'],'conditional')
        self.assertIn('source.codex',s['external_sources'])

    def test_09_false_judgments_never_prune(self):
        s=choose(self.r,[observation(self.b),observation(self.b,'fact.material_change',False)])
        self.assertEqual(len(s['rules']),6)
        self.assertEqual(s['exclusions'],{})
        self.assertFalse(s['fact_reports']['fact.repository_work']['pruning_qualified'])

    def test_10_12_stale_missing_unavailable_conflict(self):
        o=observation(self.b); o['scope']['context']='old'
        self.assertEqual(choose(self.r,[o])['fact_reports'][o['fact_id']]['state'],'stale')
        self.assertEqual(self.s['fact_reports'][o['fact_id']]['state'],'unknown')
        o=observation(self.b,state='unavailable',value=None)
        self.assertEqual(choose(self.r,[o])['fact_reports'][o['fact_id']]['state'],'unavailable')
        s=choose(self.r,[observation(self.b),observation(self.b,value=True)])
        self.assertEqual(s['fact_reports'][o['fact_id']]['state'],'conflicting')
        self.assertEqual(len(s['fact_reports'][o['fact_id']]['observations']),2)
        self.assertEqual(len(s['rules']),6)

    def test_13_forged_resolution_and_qualification(self):
        o=observation(self.b,resolution_class='observed_evidence')
        with self.assertRaisesRegex(Invalid,'resolution'): choose(self.r,[o])
        o,a=proof(self.b)
        with self.assertRaisesRegex(Invalid,'qualification'): choose(self.r,[o])
        a[o['basis']]['evaluator']='unpermitted'
        with self.assertRaisesRegex(Invalid,'mismatch'): choose(self.r,[o],a)
        o=observation(self.b,value=0)
        with self.assertRaisesRegex(Invalid,'mistyped'): choose(self.r,[o])

    def test_14_stale_qualified_and_unqualified_assertion(self):
        r=copy.deepcopy(self.r)
        r['pb.startup-floor']['when']={'all':[r['pb.startup-floor']['when'],{'is':['fact.exact-source-read',True]}]}
        o,a=proof(self.b)
        o['freshness']['observed_at']='2026-09-05T04:00:00Z';a[o['basis']]['observed_at']=o['freshness']['observed_at']
        s=choose(r,[o],a)
        self.assertEqual(s['fact_reports'][o['fact_id']]['state'],'stale')
        self.assertIn('pb.startup-floor',by_id(s))
        o,a=proof(self.b);o['basis']=None
        self.assertIn('pb.startup-floor',by_id(choose(r,[o])))

    def test_15_16_false_conjunct_and_required_dependency(self):
        r=copy.deepcopy(self.r)
        r['pb.retrieval-recovery']['when']={'all':[r['pb.retrieval-recovery']['when'],{'is':['fact.exact-source-read',True]}]}
        o,a=proof(self.b)
        s=choose(r,[o],a)
        self.assertNotIn('pb.retrieval-recovery',by_id(s))
        proof_record=s['exclusions']['pb.retrieval-recovery']
        self.assertEqual(proof_record['evidence_ids'],['synthetic:exact-read'])
        self.assertEqual(proof_record['scope'],self.b['context'])
        self.assertEqual(s['permission'],'not_evaluated')
        r['pb.claim-verification']['requires'].append('pb.retrieval-recovery')
        s=choose(r,[o],a)
        self.assertIn('pb.claim-verification:requires',by_id(s)['pb.retrieval-recovery']['selection_reasons'])
        self.assertTrue(s['exclusions']['pb.retrieval-recovery']['retained_as_required_dependency'])

    def test_17_judgment_in_every_condition_path(self):
        r=copy.deepcopy(self.r); rule=r['pb.startup-floor']
        expr={'all':[{'not':{'is':['fact.repository_work',False]}},{'any':[{'is':['fact.material_change',True]},{'is':['fact.startup_ready',False]}]}]}
        rule['when']=expr;rule['failure']['when']=expr;rule['lifetime']['ends_when']=expr;rule['completion']['when']=expr
        rule['activates']=[{'target':'source.maintenance','when':expr}]
        s=choose(r,[observation(self.b),observation(self.b,'fact.material_change',False),observation(self.b,'fact.startup_ready',True)])
        self.assertTrue(all(v['state']=='conditional' for v in by_id(s)['pb.startup-floor']['conditions'].values()))
        self.assertFalse(s['completion_grants_authority'])

    def test_18_external_readiness_and_all_adapters(self):
        for source in ('source.codex','source.claude','source.chatgpt','source.readiness'):
            self.assertIn(source,self.s['external_sources'])
        self.assertIn('action-latch',self.r['source.readiness']['definition'])
        self.assertNotIn('pb.action-latch',self.r)
        self.assertFalse(self.s['complete_execution_contract'])
