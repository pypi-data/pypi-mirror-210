from typing import Optional, Type
from cqlpy._internal.types.any import CqlAny


class Quantity(CqlAny[object, Optional[float]]):
    def __init__(self, value: Optional[float] = None, unit: Optional[str] = None):
        self._value = value
        self._unit = unit

    def __str__(self) -> str:
        if self._value is None:
            return self._unit or ""
        return str(self._value) + " " + (self._unit or "")

    @property
    def value(self) -> Optional[float]:
        return self._value

    @property
    def unit(self) -> Optional[str]:
        return self._unit

    @classmethod
    def parse_cql(cls, cql: str, subtype: Optional[Type[CqlAny]] = None) -> "Quantity":
        return cls()

    @classmethod
    def parse_fhir_json(
        cls,
        fhir_json: object,
        subtype: Optional[Type["CqlAny"]] = None,
    ) -> "Quantity":
        return cls()
