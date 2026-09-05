import copy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from compiler.model import Invalid, evaluate
from compiler.provenance import read_json
import recovery as candidate
import shutil
import tempfile
from compiler.diff import semantic_diff
from compiler.provenance import binding
from compiler.recovery_section import (BEGIN, END, READER, SOURCE, surrounding,
                                       replace, reader_mappings)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.build').mkdir(exist_ok=True)
        self.records, self.locations = candidate.corpus()
        self.contract = read_json(ROOT, 'recovery/contract.json')

    def test_definition_edit_changes_document_and_shared_diff(self):
        edited = copy.deepcopy(self.records)
        edited[candidate.ACTION]['does'] += '\nA hypothetical new recovery obligation.\n'
        before = candidate.render(self.records, self.contract)
        after = candidate.render(edited, self.contract)
        self.assertNotEqual(before, after)
        self.assertIn(b'A hypothetical new recovery obligation.', after)
        report = candidate.definition_probe(self.records, self.locations)
        event, = report['shared_semantic_diff']['events']
        self.assertEqual(event['category'], 'action_definition_changed')
        self.assertIn(candidate.RULE, event['affected_rules'])
        self.assertEqual(event['affected_reader_outputs'], [READER + '#recovery'])
        self.assertEqual(report['reader_effects'][0]['effect'], 'body_changed')

    def test_reader_mapping_is_bounded_and_stale_mappings_fail(self):
        changed = copy.deepcopy(self.records)
        changed[candidate.ACTION]['does'] += '\nA hypothetical reader change.\n'
        event, = semantic_diff(self.records, changed, self.locations, self.locations,
                               reader_mappings(self.contract, self.records))['events']
        self.assertEqual(event['affected_reader_outputs'], [READER + '#recovery'])

        nonreader = copy.deepcopy(self.records)
        nonreader['action.startup-floor']['does'] += ' Reader unaffected.\n'
        event, = semantic_diff(self.records, nonreader, self.locations, self.locations,
                               reader_mappings(self.contract, self.records))['events']
        self.assertEqual(event['affected_reader_outputs'], [])
        self.assertEqual(event['reader_mapping_status'], 'no_direct_reader_clause')

        for mutate in (
            lambda c: c.pop('reader_mappings'),
            lambda c: c['reader_mappings'][0].update(clause='action.missing/does'),
            lambda c: c['reader_mappings'].append(copy.deepcopy(c['reader_mappings'][0])),
        ):
            with self.subTest(mutate=mutate):
                broken = copy.deepcopy(self.contract)
                mutate(broken)
                with self.assertRaisesRegex(Invalid, 'reader mapping'):
                    candidate.render(self.records, broken)

    def test_unrendered_normative_changes_fail_closed(self):
        changes = [
            (candidate.RULE, 'overrides', ['hypothetical']),
            (candidate.RULE, 'authority_ref', {}),
            ('action.retrieval-recovery-failure', 'does', 'Continue without a source.'),
            ('fact.source_available', 'resolution_class', 'observed_evidence'),
            ('source.retrieval', 'path', 'another-owner.md'),
        ]
        for rid, field, value in changes:
            with self.subTest(rid=rid, field=field):
                edited = copy.deepcopy(self.records)
                edited[rid][field] = value
                with self.assertRaises((Invalid, TypeError, KeyError)):
                    candidate.render(edited, self.contract)

    def local_repo(self, destination):
        root = Path(destination) / 'experiments/code-first-playbook'
        root.mkdir(parents=True)
        for name in ('semantics', 'compiler', 'provenance', 'recovery'):
            shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('recovery.py', 'requirements.txt'):
            shutil.copyfile(ROOT / name, root / name)
        reader = root.parents[1] / READER
        reader.parent.mkdir()
        shutil.copyfile(ROOT.parents[1] / READER, reader)
        return root, reader

    def test_hand_edit_detection_is_read_only_and_explicit_generation_repairs(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.build') as directory:
            root, reader = self.local_repo(directory)
            original = reader.read_bytes()
            edited = original.replace(b'Halt continuity reasoning.', b'Skip retrieval.')
            reader.write_bytes(edited)
            with self.assertRaisesRegex(Invalid, 'stale_or_hand_edited:.*semantic.*source-retrieval.yaml'):
                candidate.check(root)
            self.assertEqual(reader.read_bytes(), edited)
            candidate.write(root)
            self.assertEqual(reader.read_bytes(), original)
            self.assertEqual(candidate.check(root)['status'], 'byte_identical')
            (root / candidate.PROVENANCE).write_bytes(b'{}\n')
            with self.assertRaisesRegex(Invalid, 'stale_or_hand_edited:.*provenance'):
                candidate.check(root)

    def test_semantic_edit_requires_no_old_prose_parity_and_preserves_surroundings(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.build') as directory:
            root, reader = self.local_repo(directory)
            original = reader.read_bytes()
            source = root / SOURCE
            source.write_text(source.read_text().replace('Halt continuity reasoning.',
                              'Halt continuity reasoning and record the correction location.'))
            changed, locations = candidate.corpus(root)
            self.assertEqual(binding(root, read_json(root, 'provenance/sources.json'), changed)['status'], 'bound')
            event, = semantic_diff(self.records, changed, self.locations, locations,
                                   reader_mappings(self.contract, self.records))['events']
            self.assertIn(READER + '#recovery', event['affected_reader_outputs'])
            with self.assertRaisesRegex(Invalid, 'stale_or_hand_edited'):
                candidate.check(root)
            candidate.write(root)
            self.assertIn(b'record the correction location.', reader.read_bytes())
            self.assertEqual(surrounding(original), surrounding(reader.read_bytes()))
            first = reader.read_bytes(), (root / candidate.PROVENANCE).read_bytes()
            candidate.write(root)
            self.assertEqual(first, (reader.read_bytes(), (root / candidate.PROVENANCE).read_bytes()))
            self.assertEqual(candidate.check(root)['status'], 'byte_identical')

    def test_document_boundaries_cannot_expand_generation(self):
        raw = (ROOT.parents[1] / READER).read_bytes()
        generated = candidate.render(self.records, self.contract)
        for edited in (raw.replace(BEGIN, b''), raw.replace(END, b''),
                       raw + BEGIN, raw + b'\n## Recovery\n\nDuplicate.\n'):
            with self.subTest(edited=edited[-60:]):
                with self.assertRaises(Invalid):
                    replace(edited, generated)
        changed = copy.deepcopy(self.records)
        changed[candidate.ACTION]['does'] += '\n## New owned section\n'
        with self.assertRaisesRegex(Invalid, 'section boundary'):
            candidate.render(changed, self.contract)

    def test_incoming_edge_remains_visible_in_shared_review_outside_focused_guard(self):
        changed = copy.deepcopy(self.records)
        changed['pb.mode-persistence']['references'].append(candidate.RULE)
        self.assertEqual(candidate.envelope(changed), candidate.envelope(self.records))
        event, = semantic_diff(self.records, changed, reader_mappings=reader_mappings(self.contract, self.records))['events']
        self.assertEqual(event['id'], 'pb.mode-persistence')
        self.assertIn(candidate.RULE, event['new']['references'])
        self.assertEqual(event['impact'], 'unresolved_semantic_impact')
        self.assertEqual(event['affected_reader_outputs'], [])

    def test_section_spacing_preserves_list_boundaries_and_all_tokens(self):
        section = candidate.section(self.records)
        self.assertEqual(section.split(), self.records[candidate.ACTION]['does'].split())
        self.assertIn('includes:\n\n- ', section)
        self.assertIn('repair:\n\n1. ', section)

    def test_failure_gate_requires_aggregate_source_unavailability(self):
        availability = self.records['fact.source_available']
        self.assertEqual(availability['resolution_class'], 'external_judgment')
        self.assertEqual(availability['evaluators'], ['controller'])
        self.assertEqual(availability['sources'], ['source.retrieval'])

        failure = self.records[candidate.RULE]['failure']
        self.assertEqual(failure['when'], {'is': ['fact.source_available', False]})
        self.assertEqual(failure['action'], 'action.retrieval-recovery-failure')
        self.assertEqual(failure['alternatives'], [])
        self.assertFalse(evaluate(failure['when'], {'fact.source_available': True}))
        self.assertTrue(evaluate(failure['when'], {'fact.source_available': False}))
