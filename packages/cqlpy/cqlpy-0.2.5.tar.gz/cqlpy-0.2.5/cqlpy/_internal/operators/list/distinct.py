# 10.2 Distinct https://cql.hl7.org/09-b-cqlreference.html#distinct

from typing import TypeVar


_DistinctType = TypeVar("_DistinctType", bound=object)


def distinct(argument: list[_DistinctType]) -> list[_DistinctType]:
    result = []
    for item in argument:
        if not (item in result):
            result.append(item)
    return result
