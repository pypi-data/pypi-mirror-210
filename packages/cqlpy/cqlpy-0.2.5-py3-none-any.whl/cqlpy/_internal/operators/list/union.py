# 10.25 Union https://cql.hl7.org/09-b-cqlreference.html#union-1

from typing import TypeVar


_UnionType = TypeVar("_UnionType")


def union(left: list[_UnionType], right: list[_UnionType]) -> list[_UnionType]:
    return left + right
