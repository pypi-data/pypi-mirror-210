# 9.20 Overlaps https://cql.hl7.org/09-b-cqlreference.html#overlaps


from cqlpy._internal.operators.interval.included_in import included_in
from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.types.interval import Interval


def overlaps(left: Interval, right: Interval) -> bool:
    return (
        (not is_null(left))
        and (not is_null(right))
        and (
            included_in(left, right)
            or included_in(right, left)
            or included_in(left.low, right)
            or included_in(left.high, right)
        )
    )
