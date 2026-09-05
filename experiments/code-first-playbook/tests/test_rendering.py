import copy
import json
import tempfile
import unittest
from pathlib import Path
from common import ROOT,corpus
from compiler.model import Invalid,canonical
from compiler.provenance import binding,compare,write_outputs,read_json,OUTPUTS
from compiler.load import safe_path
from renderers import ai,operator_sre,support
from renderers.clauses import clauses,audit


class Rendering(unittest.TestCase):
    def setUp(self):
        self.b,self.r,self.l,self.s,self.p=corpus()
        self.c=clauses(self.s)
        self.prov={'input_commit':'1'*40}
        (ROOT/'.build').mkdir(exist_ok=True)

    def test_three_views_and_independent_source_literals(self):
        byid={c['id']:c for c in self.c}
        for rid in ('startup-floor','conditional-activation','mode-persistence','retrieval-triggers','claim-verification','retrieval-recovery'):
            self.assertEqual(byid['action.'+rid+'/does']['value'],self.r['action.'+rid]['does'])
            self.assertEqual(byid['pb.'+rid+'/effect']['value']['modality'],'must')
            self.assertEqual(byid['pb.'+rid+'/failure']['value']['alternatives'],[])
        structured=json.loads(ai.render(self.s,self.c,self.prov))
        self.assertEqual(structured['clauses'],self.c)
        for renderer in (operator_sre,support):
            body=renderer.render(self.s,self.c,self.prov,self.l,self.p).decode()
            for c in self.c:
                self.assertIn('### '+c['id']+'\n',body)
                self.assertIn(c['text'],body)
            self.assertIn('Incomplete executor contract',body)
            self.assertIn('"permission": "not_evaluated"',body)
        support_body=support.render(self.s,self.c,self.prov,self.l,self.p).decode()
        self.assertIn('A source lookup was rejected or never performed',support_body)
        self.assertIn('Escalation question:',support_body)

    def test_23_each_audience_semantic_mutation(self):
        outputs={'ai':ai.render(self.s,self.c,self.prov),
                 'operator':operator_sre.render(self.s,self.c,self.prov,self.l,self.p),
                 'support':support.render(self.s,self.c,self.prov,self.l,self.p)}
        # Independent literal oracle checks the authored exceptions, modality and
        # explicit empty fallback list through each actual renderer path.
        for audience,raw in outputs.items():
            for needle,replacement in [(b'not premature failure',b'premature failure is allowed'),
                                        (b'must',b'should'),(b'Authority from failure or fallback',b'Permission granted by fallback')]:
                with self.subTest(audience=audience,seed=needle):
                    self.assertIn(needle,raw)
                    mutated=raw.replace(needle,replacement)
                    with self.assertRaises(Invalid):audit(mutated,audience,self.c)
            # New fallback appended to an otherwise unchanged output still fails
            # the actual full-set regeneration comparator below.

    def test_output_set_hand_edit_manifest_edit_and_symlink(self):
        expected={p:b'fixture output\n' for p in OUTPUTS}
        with tempfile.TemporaryDirectory(dir=ROOT/'.build') as d:
            destination=Path(d)/'outputs';write_outputs(destination,expected)
            self.assertEqual(compare(destination,expected),[])
            (destination/'index.md').write_bytes(b'invented fallback\n')
            (destination/'provenance.json').write_bytes(b'edited manifest too\n')
            self.assertEqual(len(compare(destination,expected)),2)
            (destination/'index.md').unlink()
            (destination/'extra.md').write_bytes(b'extra\n')
            errors=compare(destination,expected)
            self.assertIn({'path':'index.md','code':'missing'},errors)
            self.assertIn({'path':'extra.md','code':'extra'},errors)
            (destination/'index.md').symlink_to(destination/'extra.md')
            with self.assertRaisesRegex(Invalid,'symlink'):compare(destination,expected)

    def test_source_binding_add_change_remove_and_unmapped(self):
        manifest=read_json(ROOT,'provenance/sources.json')
        self.assertEqual(binding(ROOT,manifest,self.r)['status'],'bound')
        with tempfile.TemporaryDirectory(dir=ROOT/'.build') as d:
            root=Path(d)
            for unit in manifest['units']:
                path=root/unit['path'];path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes((ROOT.parents[1]/unit['path']).read_bytes())
            self.assertEqual(binding(ROOT,manifest,self.r,root)['status'],'bound')
            p=root/'docs/start-here.md';raw=p.read_bytes()
            for changed in (raw+b'\nNew unprojected block.\n',raw.replace(b'Purpose',b'Changed purpose'),raw[:-20]):
                p.write_bytes(changed)
                self.assertEqual(binding(ROOT,manifest,self.r,root)['status'],'drift')
        invalid=copy.deepcopy(manifest);invalid['units'][0]['blocks'][1]['text']='missing\n'
        with self.assertRaisesRegex(Invalid,'block hash'):binding(ROOT,invalid,self.r)

    def test_complete_contract_request_rejected(self):
        from pilot import compile_bundle
        with tempfile.TemporaryDirectory(dir=ROOT/'.build') as d:
            p=Path(d)/'complete.json';b=copy.deepcopy(self.b);b['request_complete_contract']=True
            p.write_bytes(canonical(b))
            with self.assertRaisesRegex(Invalid,'complete executor'):compile_bundle(ROOT,str(p.relative_to(ROOT)))
