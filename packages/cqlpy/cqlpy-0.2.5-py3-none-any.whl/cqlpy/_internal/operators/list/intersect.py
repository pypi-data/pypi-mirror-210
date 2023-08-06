# 10.4 Intersect https://cql.hl7.org/09-b-cqlreference.html#intersect-1


from typing import TypeVar, Union
from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.operators.interval.overlaps import overlaps
from cqlpy._internal.types.any import CqlAny
from cqlpy._internal.types.code import Code
from cqlpy._internal.types.date import Date
from cqlpy._internal.types.datetime import DateTime
from cqlpy._internal.types.decimal import Decimal
from cqlpy._internal.types.integer import Integer
from cqlpy._internal.types.interval import Interval
from cqlpy._internal.types.null import Null

_IntersectType = TypeVar(
    "_IntersectType", bound=Union[DateTime, Date, Integer, Decimal]
)


def intersect(
    left: Union[list[_IntersectType], Interval[_IntersectType]],
    right: Union[list[_IntersectType], Interval[_IntersectType]],
) -> Union[list, Interval, Null]:
    if (not is_null(left)) and (not is_null(right)):
        if isinstance(left, Interval) and isinstance(right, Interval):
            if not (
                isinstance(left.low, DateTime)
                and isinstance(right.low, DateTime)
                and isinstance(left.high, DateTime)
                and isinstance(right.high, DateTime)
            ):
                return Null()
            if overlaps(left, right):
                return Interval(
                    DateTime.parse_datetime(max(left.low.value, right.low.value)),
                    False,
                    DateTime.parse_datetime(min(left.high.value, right.high.value)),
                    False,
                )
            return Null()

        elif isinstance(left, list) and isinstance(right, list):
            return_list = []
            for left_item in left:
                for right_item in right:
                    if isinstance(left_item, Code) and isinstance(right_item, Code):
                        if left_item.code == right_item.code:
                            return_list.append(left_item)

                    else:
                        if left_item == right_item:
                            return_list.append(left_item)

            return return_list

    return Null()
