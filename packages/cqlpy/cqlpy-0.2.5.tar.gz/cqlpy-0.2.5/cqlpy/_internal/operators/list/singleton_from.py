# 10.21 Singleton From https://cql.hl7.org/09-b-cqlreference.html#singleton-from

from typing import TypeVar

from cqlpy._internal.types.null import Some


_SingletonFromType = TypeVar("_SingletonFromType")


def singleton_from(
    argument: list[Some[_SingletonFromType]],
) -> Some[_SingletonFromType]:
    # todo: handle situations where there is 0 or 2+ instances in the list
    return argument[0]
