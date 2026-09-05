import copy
import unittest
from pathlib import Path
from compiler.load import parse,load_modules,safe_path
from compiler.validate import validate
from compiler.model import Invalid,condition


class Language(unittest.TestCase):
    def test_restricted_parser(self):
        bad=[b'a: 1\na: 2\n',b'a: &x true\nb: *x\n',b'a: !!str x\n',b'<<: x\n',
             b'a: yes\n',b'a: ${HOME}\n',b'1: value\n',b'a: true\n---\nb: false\n',
             b'\xef\xbb\xbfa: true\n',b'a: true\r\n',b'a: [\n']
        for raw in bad:
            with self.subTest(raw=raw),self.assertRaises(Invalid):parse(raw)
        self.assertEqual(parse(b'a: true\nb: "no"\nc: |\n  exact text\n'),{'a':True,'b':'no','c':'exact text\n'})
        for path in ('../outside','/absolute'):
            with self.assertRaises(Invalid):safe_path(self.root,path)

    def baseline(self):
        return load_modules(self.root, ['semantics/startup.yaml', 'semantics/source-retrieval.yaml'])

    @property
    def root(self):
        return Path(__file__).resolve().parents[1]

    def mutate(self, edit):
        m,l=self.baseline();r={x['id']:x for module in m.values() for x in module['records']};edit(m,r)
        return validate(m,l)

    def test_19_retirement_and_typed_graphs(self):
        def retired(m,r):
            r['pb.retrieval-triggers']['status']='retired'
            r['pb.claim-verification']['failure']={'inherits':'pb.retrieval-triggers','scope':'current-operation'}
        with self.assertRaisesRegex(Invalid,'retired'):self.mutate(retired)
        def cycle(m,r):
            r['pb.startup-floor']['requires'].append('pb.mode-persistence')
        with self.assertRaisesRegex(Invalid,'prerequisite cycle'):self.mutate(cycle)
        def benign(m,r):
            r['pb.startup-floor']['references']=['pb.mode-persistence']
            r['pb.mode-persistence']['references']=['pb.startup-floor']
        self.mutate(benign)
        def precedence(m,r):
            for a,b in [('pb.startup-floor','pb.mode-persistence'),('pb.mode-persistence','pb.startup-floor')]:
                r[a]['overrides']=[{'target':b,'when':r[a]['when'],'source':'source.start','question':r[a]['authority_ref']['question'],'justification':'Synthetic conflict seed'}]
        with self.assertRaisesRegex(Invalid,'precedence cycle'):self.mutate(precedence)

    def test_missing_import_owner_and_fields(self):
        edits=[lambda m,r:m['source-retrieval'].update(imports=[]),
               lambda m,r:r['pb.startup-floor'].update(grants_authority=True),
               lambda m,r:r['pb.startup-floor'].update(owner='source.retrieval'),
               lambda m,r:r['pb.startup-floor']['requires'].append('missing'),
               lambda m,r:r['pb.startup-floor']['effect'].update(parameters={'operation':True}),
               lambda m,r:r['pb.startup-floor'].update(before=['source.start']),
               lambda m,r:r['pb.startup-floor'].update(unit='pb.action-latch'),
               lambda m,r:r['pb.startup-floor']['when'].update(any=[{'is':['undefined',True]}])]
        for edit in edits:
            with self.subTest(edit=edit),self.assertRaises(Invalid):self.mutate(edit)

    def test_impossible_and_opposing_consequence(self):
        def impossible(m,r):r['pb.startup-floor']['when']={'all':[{'is':['fact.repository_work',True]},{'is':['fact.repository_work',False]}]}
        with self.assertRaisesRegex(Invalid,'impossible'):self.mutate(impossible)
        def opposing(m,r):
            r['pb.conditional-activation']['effect']=copy.deepcopy(r['pb.startup-floor']['effect'])
            r['pb.conditional-activation']['effect']['modality']='must_not'
        with self.assertRaisesRegex(Invalid,'contradictory'):self.mutate(opposing)

    def test_analysis_bound_is_incomplete_not_consistent(self):
        m,l=self.baseline(); r={x['id']:x for module in m.values() for x in module['records']}
        facts=sorted(i for i,x in r.items() if x['kind']=='fact')[:13]
        self.assertEqual(len(facts),13)
        expr={'all':[{'is':[f,True]} for f in facts]}
        self.assertEqual(condition(expr,r),{'state':'conditional','analysis':'incomplete'})
        r['pb.startup-floor']['when']=expr
        _,diagnostics=validate(m,l)
        self.assertIn({'id':'pb.startup-floor','code':'analysis_incomplete'},diagnostics)
