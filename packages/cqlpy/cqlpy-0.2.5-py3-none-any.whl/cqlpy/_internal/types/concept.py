from typing import Optional, Type

from cqlpy._internal.types.any import CqlAny
from cqlpy._internal.types.code import Code


class Concept(CqlAny[dict[str, list[dict[str, str]]], list[Code]]):
    """
    Concept represents a FHIR codeable concept as a list of Code
    The FHIR codeable concept will be represented in json following the pattern of the following example:

    {
        'coding': [
                    {
                        'system': 'http://anthem.com/codes/Facets/DiagnosisCode',
                        'code': '78099',
                        'display': 'Other general symptoms',
                        'userSelected': True
                    },
                    {
                        'system': 'http://fhir.carevolution.com/codes/z-ICD9-DONOTUSE/DiagnosisCode',
                        'version': 'LEGACY',
                        'code': '78099',
                        'display': 'Other general symptoms',
                        'userSelected': False
                    },
                    {
                        'system': 'http://hl7.org/fhir/sid/icd-9-cm',
                        'code': '780.99',
                        'display':
                        'Other general symptoms',
                        'userSelected': False
                    },
                    {
                        'system': 'http://fhir.carevolution.com/codes/ICD9/DiagnosisCode',
                        'code': '78099',
                        'display': 'Other general symptoms',
                        'userSelected': False
                    }
                ]
    }
    """

    def __init__(self, codes: list = []):
        self.codes = codes
        self.display = ""

    def __str__(self) -> str:
        return "display= , codes = " + str([str(code) for code in self.codes])

    @property
    def value(self) -> list[Code]:
        return self.codes

    @classmethod
    def parse_cql(cls, cql: str, subtype: Optional[Type[CqlAny]] = None) -> "Concept":
        return cls(codes=[])

    @classmethod
    def parse_fhir_json(
        cls,
        fhir_json: dict[str, list[dict[str, str]]],
        subtype: Optional[Type["CqlAny"]] = None,
    ) -> "Concept":
        if "coding" in fhir_json:
            codes = [
                Code().parse_fhir_json(fhir_code) for fhir_code in fhir_json["coding"]
            ]
        else:
            codes = []
        display = ""

        return cls(codes=codes)
