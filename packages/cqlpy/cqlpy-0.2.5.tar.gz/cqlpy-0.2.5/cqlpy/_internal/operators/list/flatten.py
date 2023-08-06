# 10.7 Flatten https://cql.hl7.org/09-b-cqlreference.html#flatten

from typing import TypeVar


_FlattenType = TypeVar("_FlattenType")


def flatten(argument: list[list[_FlattenType]]) -> list[_FlattenType]:
    result = []
    for item in argument:
        result += item
    return result
