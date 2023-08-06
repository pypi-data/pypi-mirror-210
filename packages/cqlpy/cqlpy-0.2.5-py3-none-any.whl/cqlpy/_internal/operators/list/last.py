# 10.15 Last https://cql.hl7.org/09-b-cqlreference.html#last

from typing import TypeVar

from cqlpy._internal.types.null import Null, Some


_LastType = TypeVar("_LastType")


def last(argument: list[_LastType]) -> Some[_LastType]:
    if len(argument) == 0:
        return Null()
    return argument[-1]
