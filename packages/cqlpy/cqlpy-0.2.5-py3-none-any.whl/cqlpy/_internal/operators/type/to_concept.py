from cqlpy._internal.types.code import Code
from cqlpy._internal.types.concept import Concept


def to_concept(code: Code) -> Concept:
    return Concept([code])
