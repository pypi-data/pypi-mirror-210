from typing import Optional, Type
from cqlpy._internal.types.any import CqlAny


class String(CqlAny[str, str], str):
    def __init__(self, value: str):
        self.__value = value

    def __hash__(self) -> int:
        return hash(self.value)

    def __new__(cls, value: str):
        return str.__new__(cls, value)

    def __repr__(self) -> str:
        return f"String({self.value})"

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, String):
            return self.value == other.value

        if isinstance(other, str):
            return self.value == other

        return False

    @property
    def value(self) -> str:
        return self.__value

    @classmethod
    def parse_fhir_json(
        cls,
        fhir_json: str,
        subtype: Optional[Type["CqlAny"]] = None,
    ) -> "String":
        return cls(fhir_json)

    @classmethod
    def parse_cql(cls, cql: str, subtype: Optional[Type[CqlAny]] = None) -> "String":
        return cls(cql)
