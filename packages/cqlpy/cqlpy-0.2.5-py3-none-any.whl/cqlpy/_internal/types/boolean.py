from typing import Optional, Type
from cqlpy._internal.exceptions import CqlParseError
from cqlpy._internal.types.any import CqlAny


class Boolean(CqlAny[str, bool], int):
    def __init__(self, value: bool):
        self.__value = value

    @property
    def value(self) -> bool:
        return self.__value

    def __int__(self) -> int:
        return int(self.value)

    @classmethod
    def parse_fhir_json(
        cls,
        fhir_json: str,
        subtype: Optional[Type["CqlAny"]] = None,
    ) -> "Boolean":
        return cls(
            str(fhir_json).lower().replace('"', "").replace("'", "").strip() == "true"
        )

    @classmethod
    def parse_cql(cls, cql: str, subtype: Optional[Type[CqlAny]] = None) -> "Boolean":
        cql = cql.lower().replace('"', "").replace("'", "").strip()
        if cql == "true":
            return cls(True)
        if cql == "false":
            return cls(False)
        raise CqlParseError(f"Invalid CQL for Boolean: {cql}")
