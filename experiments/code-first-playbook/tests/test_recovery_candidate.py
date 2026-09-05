import copy
import unittest
from unittest.mock import patch
from pathlib import Path

from common import ROOT
from compiler.model import Invalid
from compiler.provenance import read_json
import recovery_candidate as candidate


class RecoveryCandidateTests(unittest.TestCase):
    def setUp(self):
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
        self.assertEqual(report['candidate_effects'][0]['effect'], 'body_changed')

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

    def test_generation_is_stable_and_does_not_read_live_prose(self):
        before = candidate.generate()
        original = Path.read_bytes
        def guarded(path):
            if path == ROOT.parents[1] / candidate.OWNER:
                raise AssertionError('compile read hand-maintained prose')
            return original(path)
        with patch.object(Path, 'read_bytes', guarded):
            self.assertEqual(before, candidate.generate())

    def test_committed_output_hand_edit_is_rejected(self):
        outputs = candidate.generate()
        original = Path.read_bytes
        directory = ROOT / 'recovery/generated'
        def edited(path):
            raw = original(path)
            return raw + b'Hand edit.\n' if path == directory / candidate.OUTPUT else raw
        with patch.object(Path, 'read_bytes', edited):
            with self.assertRaisesRegex(Invalid, 'stale_or_hand_edited'):
                candidate.compare(directory, outputs)

    def test_section_spacing_preserves_list_boundaries_and_all_tokens(self):
        section = candidate.section(self.records)
        self.assertEqual(section.split(), self.records[candidate.ACTION]['does'].split())
        self.assertIn('includes:\n\n- ', section)
        self.assertIn('repair:\n\n1. ', section)
