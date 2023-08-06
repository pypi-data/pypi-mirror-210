# 8.2 After https://cql.hl7.org/09-b-cqlreference.html#after


from cqlpy._internal.operators.date_time.date_time_precision import DateTimePrecision
from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.types.datetime import DateTime
from cqlpy._internal.types.null import Null, Some


def after(
    left: DateTime,
    right: DateTime,
    precision: DateTimePrecision = DateTimePrecision.Millisecond,
) -> Some[bool]:
    if is_null(left) or is_null(right):
        return Null()
    return left > right
