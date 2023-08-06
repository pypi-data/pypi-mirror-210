from cqlpy._internal.operators.nullological.is_null import is_null

from cqlpy._internal.types.any import CqlAny
from cqlpy._internal.types.null import Null, Some

# 4.1 Coalese https://cql.hl7.org/09-b-cqlreference.html#coalesce


def coalesce(*args: Some[CqlAny]) -> Some[CqlAny]:
    for arg in args:
        if not is_null(arg):
            assert arg is not None
            return arg
    return Null()
