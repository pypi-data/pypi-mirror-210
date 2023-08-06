from typing import Optional, Any, Union, Type

from cqlpy._internal.types.any import CqlAny
from cqlpy._internal.types.code_system import CodeSystem


class Code(
    CqlAny[
        dict[str, Any],
        tuple[Union[str, CodeSystem, None], Optional[str], Optional[str]],
    ]
):
    def __init__(
        self,
        system: Union[str, CodeSystem, None] = None,
        code: Optional[str] = None,
        display: Optional[str] = None,
        version: Optional[str] = None,
    ):
        self.code = code
        self.display = display
        self.system = system
        self.version = version

    def __str__(self) -> str:
        return (
            "code:"
            + str(self.code)
            + ", display:"
            + str(self.display)
            + ", system:"
            + str(self.system)
        )

    @property
    def value(
        self,
    ) -> tuple[Union[str, CodeSystem, None], Optional[str], Optional[str]]:
        return self.system, self.code, self.version

    @classmethod
    def parse_cql(cls, cql: str, subtype: Optional[Type[CqlAny]] = None) -> "Code":
        return cls()

    @classmethod
    def parse_fhir_json(
        cls,
        fhir_json: dict[str, Any],
        subtype: Optional[Type["CqlAny"]] = None,
    ) -> "Code":
        code = fhir_json["code"] if "code" in fhir_json else ""
        display = fhir_json["display"] if "display" in fhir_json else ""
        system = fhir_json["system"] if "system" in fhir_json else ""
        version = fhir_json["version"] if "version" in fhir_json else ""

        return cls(
            system=system,
            code=code,
            display=display,
            version=version,
        )
