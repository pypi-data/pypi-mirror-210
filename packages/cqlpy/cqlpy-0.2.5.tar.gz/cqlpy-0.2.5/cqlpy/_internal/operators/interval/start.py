# 9.28 Start https://cql.hl7.org/09-b-cqlreference.html#start


from typing import Union
from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.types.any import CqlAny
from cqlpy._internal.types.date import Date
from cqlpy._internal.types.datetime import DateTime
from cqlpy._internal.types.decimal import Decimal
from cqlpy._internal.types.integer import Integer
from cqlpy._internal.types.interval import Interval
from cqlpy._internal.types.null import Null, Some


def start(argument: Interval[DateTime]) -> Some[DateTime]:
    if not is_null(argument):
        return argument.low or Null()
    else:
        return Null()


# def overlaps(self, cql_interval) -> bool:
#     return self.low.included_in(cql_interval) or self.high.included_in(cql_interval) or cql_interval.low.included_in(self)

# def intersect(self, cql_interval): # -> CqlList:
#     # this is just a placeholder to test syntax; implementation required
#     return self
