from typing import TypeVar, Union

from cqlpy._internal.types.any import CqlAny


class Null:
    def __eq__(self, compare: object) -> bool:
        return compare == Null

    def __getitem__(self, query: str) -> "Null":
        return Null()

    def __repr__(self) -> str:
        return "Null"

    def __str__(self) -> str:
        return "Null"


_SomeType = TypeVar("_SomeType")
Some = Union[_SomeType, Null]
