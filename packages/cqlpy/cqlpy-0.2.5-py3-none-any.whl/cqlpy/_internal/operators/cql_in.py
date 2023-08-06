from typing import TypeVar, Union
from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.types.interval import Interval
from cqlpy._internal.operators.comparison.in_list import in_list
from cqlpy._internal.operators.interval.in_interval import in_interval
from cqlpy._internal.types.null import Some

_InType = TypeVar("_InType")
_ArgumentType = Some[Union[list[Some[_InType]], Interval]]


def cql_in(item: Some[_InType], argument: _ArgumentType) -> bool:
    if is_null(item) or is_null(argument):
        return False
    if isinstance(argument, Interval):
        return in_interval(item, argument)
    return in_list(item, argument)
