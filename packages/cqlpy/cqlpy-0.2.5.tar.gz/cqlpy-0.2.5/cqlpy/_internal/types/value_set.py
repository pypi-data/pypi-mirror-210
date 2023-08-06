from typing import Any, Optional, Type
from cqlpy._internal.types.any import CqlAny
from cqlpy._internal.types.code import Code


class ValueSet(CqlAny[dict[str, Any], list[Code]]):
    def __init__(
        self,
        value_set_id: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        use_context: Optional[str] = None,
        codes: Optional[list[Code]] = None,
    ):
        self.id = value_set_id
        self.name = name
        self.version = version
        self.use_context = use_context
        self.codes: list[Code] = codes or []

    def __str__(self) -> str:
        return (
            "id:"
            + (self.id or "")
            + ", version:"
            + (self.version or "")
            + ", codes:"
            + str([str(code) for code in self.codes])
        )

    @property
    def value(self) -> list[Code]:
        return self.codes

    @classmethod
    def parse_cql(cls, cql: str, subtype: Optional[Type[CqlAny]] = None) -> "ValueSet":
        value_set_id = ""
        version = ""
        name = ""

        return cls(
            value_set_id=value_set_id,
            name=name,
            version=version,
        )

    @classmethod
    def parse_fhir_json(
        cls,
        fhir_json: dict[str, Any],
        subtype: Optional[Type["CqlAny"]] = None,
    ) -> "ValueSet":
        version: str = fhir_json["version"]
        name: str = fhir_json["name"]
        includes: list[dict[str, Any]] = fhir_json["compose"]["include"]

        codes = [
            Code(
                system=include.get("system", ""),
                code=concept["code"],
                display=concept.get("display", ""),
                version=include.get("version", ""),
            )
            for include in includes
            for concept in include["concept"]
        ]

        return cls(
            value_set_id="",
            name=name,
            version=version,
            codes=codes,
        )
