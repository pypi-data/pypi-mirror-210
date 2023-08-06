from typing import TypeVar


_ListType = TypeVar("_ListType")


def to_list(*args: _ListType) -> list[_ListType]:
    return [item for item in args]
