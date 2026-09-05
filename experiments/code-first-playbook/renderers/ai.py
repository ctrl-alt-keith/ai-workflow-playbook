from compiler.model import canonical
from .clauses import header


def render(selection, clauses, provenance):
    return canonical({**header("ai", provenance), "contract": selection, "clauses": clauses})
