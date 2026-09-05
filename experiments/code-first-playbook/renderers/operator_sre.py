from .clauses import human


def render(selection, clauses, provenance, locations, profile):
    return human("operator-sre", selection, clauses, provenance, locations, profile)
