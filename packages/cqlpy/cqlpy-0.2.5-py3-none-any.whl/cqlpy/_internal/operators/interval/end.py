from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.types.datetime import DateTime
from cqlpy._internal.types.interval import Interval
from cqlpy._internal.types.null import Null, Some


def end(argument: Interval[DateTime]) -> Some[DateTime]:
    if not is_null(argument):
        return argument.high or Null()
    else:
        return Null()
