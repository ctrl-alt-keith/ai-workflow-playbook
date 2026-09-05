"""The single operational section boundary; not a general document framework."""

import re

from .model import require

READER = 'docs/source-first-retrieval.md'
RULE = 'pb.retrieval-recovery'
ACTION = 'action.retrieval-recovery'
SOURCE = 'semantics/source-retrieval.yaml'
OWNERSHIP = {'clause': ACTION + '/does', 'source': SOURCE,
             'reader': READER + '#recovery', 'rule': RULE}
BEGIN = b'<!-- generated: pb.retrieval-recovery -->\n'
END = b'<!-- /generated: pb.retrieval-recovery -->\n'


def reader_mappings(contract, records):
    """Validate the renderer's complete, explicit clause-to-reader contract."""
    mappings = contract.get('reader_mappings')
    require(type(mappings) is list and len(mappings) == 1,
            'Recovery requires exactly one explicit reader mapping')
    mapping, = mappings
    require(mapping == {'clause': OWNERSHIP['clause'], 'reader': OWNERSHIP['reader']},
            'stale or malformed Recovery reader mapping')
    record, field = mapping['clause'].split('/')
    require(record in records and field in records[record],
            'stale Recovery reader mapping clause: ' + mapping['clause'])
    return mappings


def parts(document):
    """Keep the stable heading and every byte outside its body with the reader."""
    heading = b'\n## Recovery\n\n'
    require(document.count(heading) == 1
            and len(re.findall(rb'^##[ \t]+Recovery[ \t]*$', document, re.MULTILINE)) == 1,
            'expected exactly one ## Recovery heading')
    before, rest = document.split(heading)
    require(b'\n## ' in rest, 'missing following Recovery section boundary')
    body, after = rest.split(b'\n## ', 1)
    return before + heading, body, b'\n## ' + after


def surrounding(document):
    before, _, after = parts(document)
    return before + after


def replace(document, generated):
    before, body, after = parts(document)
    require(document.count(BEGIN) == document.count(END) == 1
            and body.startswith(BEGIN) and body.endswith(END),
            'Recovery generation boundaries missing or changed; restore the owned section markers')
    return before + generated + after
