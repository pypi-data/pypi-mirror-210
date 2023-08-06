# 9.13 Included In https://cql.hl7.org/09-b-cqlreference.html#included-in

from typing import Union
from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.types.date import Date
from cqlpy._internal.types.datetime import DateTime
from cqlpy._internal.types.decimal import Decimal
from cqlpy._internal.types.integer import Integer

from cqlpy._internal.types.interval import Interval
from cqlpy._internal.types.null import Null


_IncludedInType = Union[Interval, Date, DateTime, Integer, Decimal, None, Null]


def included_in(left: _IncludedInType, right: Interval) -> bool:
    if is_null(left) or is_null(right):
        return False

    if isinstance(left, Interval):
        if (
            len(
                {
                    left.low.__class__,
                    left.high.__class__,
                    right.low.__class__,
                    right.high.__class__,
                }
            )
            > 1
        ):
            raise TypeError("Cannot compare intervals of different types")
        return included_in(left.low, right) and included_in(left.high, right)

    if (
        isinstance(left, DateTime)
        and isinstance(right, Interval)
        and isinstance(right.low, DateTime)
        and isinstance(right.high, DateTime)
    ):
        return (
            (left > right.low)
            and (left < right.high)
            or (left == right.low and right.low_closed)
            or (left == right.high and right.high_closed)
        ) or False

    return False
