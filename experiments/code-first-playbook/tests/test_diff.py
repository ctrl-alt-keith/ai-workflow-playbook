import copy
import unittest
from common import corpus
from compiler.diff import semantic_diff


class Diff(unittest.TestCase):
    def setUp(self):self.b,self.r,self.l,self.s,self.p=corpus()

    def change(self,rid,field,value):
        n=copy.deepcopy(self.r);n[rid][field]=value
        return semantic_diff(self.r,n,self.l,self.l)['events'][0]

    def test_20_action_definition_with_unchanged_rule(self):
        e=self.change('action.startup-floor','does','Read start-here only.')
        self.assertEqual(e['category'],'action_definition_changed')
        self.assertEqual(e['dimensions'],['does'])
        self.assertEqual(e['affected_rules'],['pb.mode-persistence','pb.startup-floor'])
        self.assertIn({'id':'pb.startup-floor','site':'effect.action'},e['direct_reference_sites'])
        self.assertEqual(e['impact'],'unresolved_semantic_impact')

    def test_21_imported_term_and_boundary(self):
        e=self.change('term.operation','definition','Changed definition without renamed ID.')
        self.assertEqual(e['category'],'term_definition_changed')
        self.assertEqual(len(e['affected_rules']),6)
        self.assertIn('pb.retrieval-recovery',e['affected_rules'])
        for rid in ('boundary.claim-verification','evidence.claim-verification'):
            e=self.change(rid,'does','Hypothetical stricter claim boundary.')
            self.assertEqual(e['category'],'boundary_completion_definition_changed')
            self.assertIn('pb.claim-verification',e['affected_rules'])
            self.assertNotIn('pb.startup-floor',e['affected_rules'])

    def test_22_context_move_and_removed_reference(self):
        e=self.change('context.startup-floor','body','Different supporting explanation.')
        self.assertEqual(e['category'],'supporting_context_only')
        n=copy.deepcopy(self.r);a=n['action.startup-floor']
        n[a['id']]={k:v for k,v in a.items() if k in ('id','owner','status','references')}
        n[a['id']].update(kind='context',body=a['does'])
        e=semantic_diff(self.r,n)['events'][0]
        self.assertEqual(e['category'],'normative_removed_to_context')
        self.assertIn('pb.startup-floor',e['affected_rules'])
        n=copy.deepcopy(self.r)
        n['pb.startup-floor']['effect']['action']='action.conditional-activation'
        n['action.startup-floor']['does']='Changed after edge removed.'
        e=semantic_diff(self.r,n)['events'][0]
        self.assertIn({'id':'pb.startup-floor','site':'effect.action'},e['direct_reference_sites'])

    def test_location_and_serialization_changes_distinct(self):
        n={k:dict(reversed(list(v.items()))) for k,v in reversed(list(self.r.items()))}
        self.assertEqual(semantic_diff(self.r,n)['events'],[])
        newloc=copy.deepcopy(self.l);newloc['action.startup-floor']['path']='semantics/moved.yaml'
        e=semantic_diff(self.r,self.r,self.l,newloc)['events'][0]
        self.assertEqual(e['category'],'source_location_changed')
        self.assertEqual(e['dimensions'],[])
        e=self.change('action.startup-floor','does',self.r['action.startup-floor']['does']+' ')
        self.assertEqual(e['category'],'action_definition_changed')
