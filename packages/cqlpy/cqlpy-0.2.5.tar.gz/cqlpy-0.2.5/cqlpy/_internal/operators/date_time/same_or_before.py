# 8.14 Same Or Before https://cql.hl7.org/09-b-cqlreference.html#same-or-before-1


from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.types.datetime import DateTime


def same_or_before(left: DateTime, right: DateTime) -> bool:
    if is_null(left) or is_null(right):
        return False
    else:
        return left.value <= right.value
