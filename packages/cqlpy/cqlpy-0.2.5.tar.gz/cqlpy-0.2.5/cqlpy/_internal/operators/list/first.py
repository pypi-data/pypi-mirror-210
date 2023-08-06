# 10.8 First https://cql.hl7.org/09-b-cqlreference.html#first

from typing import TypeVar

from cqlpy._internal.types.null import Null, Some

_FirstType = TypeVar("_FirstType")


def first(argument: list[_FirstType]) -> Some[_FirstType]:
    if len(argument) == 0:
        return Null()
    else:
        return argument[0]
