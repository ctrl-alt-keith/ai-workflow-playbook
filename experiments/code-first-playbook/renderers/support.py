from .clauses import human


def render(selection, clauses, provenance, locations, profile):
    return human("support", selection, clauses, provenance, locations, profile)
