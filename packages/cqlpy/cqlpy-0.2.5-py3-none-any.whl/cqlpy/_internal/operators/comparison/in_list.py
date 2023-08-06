# 10.9 In https://cql.hl7.org/09-b-cqlreference.html#in-1

from typing import TypeVar

from cqlpy._internal.types.code import Code


_InListType = TypeVar("_InListType")


def in_list(element: _InListType, argument: list[_InListType]) -> bool:
    for item in argument:
        if (
            isinstance(element, Code)
            and isinstance(item, Code)
            and element.code == item.code
        ):
            return True
        if element == item:
            return True

    return False
