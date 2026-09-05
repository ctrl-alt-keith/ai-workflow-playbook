import copy
import unittest
from common import ROOT,corpus
from compiler.model import Invalid,digest
from compiler.provenance import read_json
from compiler.rehearsal import unit_body,verify_fixture
from renderers.clauses import clauses


class Rehearsal(unittest.TestCase):
    def setUp(self):
        _,r,_,s,_=corpus();g0,fields=unit_body(r,s,clauses(s));m=copy.deepcopy(s)
        m['vocabulary']['action.retrieval-recovery']['does']+='\nSIMULATION S1: Record the correction location for mock review.\n'
        g1,_=unit_body(r,m,clauses(m));self.bodies={'G0':g0,'G1':g1}
        self.f=read_json(ROOT,'cases/authority-rehearsal.json')

    def test_24_all_fixed_transition_branches(self):
        report=verify_fixture(self.f,self.bodies)
        self.assertEqual(len(report['ledger']),9)
        self.assertEqual(report['owner_gaps'],0)
        self.assertEqual(report['dual_owners'],0)
        self.assertTrue(all(x['authority_transferred'] is False for x in report['ledger']))
        self.assertNotEqual(digest(self.bodies['G0']),digest(self.bodies['G1']))

    def test_missing_decision_body_hash_retirement_and_partial_route(self):
        edits=[lambda f:f['steps'][1].update(decision=None),
               lambda f:f['steps'][1].update(body='missing'),
               lambda f:f['steps'][1].update(body_sha256='0'*64),
               lambda f:f['steps'][5]['decision'].update(retirement='not_retired'),
               lambda f:f['steps'][1]['after'].update(routing='prose:P0'),
               lambda f:f['steps'][1]['after'].update(body_status='hand-maintained'),
               lambda f:f['steps'][2].update(compatible=False),
               lambda f:f['steps'][7].update(impact='silently restore old policy'),
               lambda f:f['steps'][6].update(blocked=False),
               lambda f:f.update(simulation_only=False)]
        for edit in edits:
            with self.subTest(edit=edit),self.assertRaises(Invalid):
                f=copy.deepcopy(self.f);edit(f);verify_fixture(f,self.bodies)

    def test_incomplete_body_rejected_at_exact_identity(self):
        broken=dict(self.bodies);broken['G0']=broken['G0'][:100]
        with self.assertRaisesRegex(Invalid,'body identity'):verify_fixture(self.f,broken)
