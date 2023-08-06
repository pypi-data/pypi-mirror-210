from abc import ABCMeta, abstractmethod
from typing import Generic, Optional, Type, TypeVar


_FhirJsonType = TypeVar("_FhirJsonType", bound=object)
_CqlAnyType = TypeVar("_CqlAnyType")


class CqlAny(Generic[_FhirJsonType, _CqlAnyType], metaclass=ABCMeta):
    """
    All Cql types inherit from the CqlAny base class.
    """

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    def __bool__(self) -> bool:
        return bool(self.value)

    def __lt__(self, other: object) -> bool:
        if isinstance(other, CqlAny):
            return self.value < other.value

        if (
            isinstance(other, type(self.value))
            and hasattr(other, "__lt__")
            and hasattr(self.value, "__lt__")
        ):
            return self.value < other

        return False

    def __le__(self, other: object) -> bool:
        if isinstance(other, CqlAny):
            return self.value <= other.value

        if (
            isinstance(other, type(self.value))
            and hasattr(other, "__le__")
            and hasattr(self.value, "__le__")
        ):
            return self.value <= other

        return False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CqlAny):
            return self.value == other.value

        if isinstance(other, type(self.value)):
            return self.value == other

        return False

    @property
    @abstractmethod
    def value(self) -> _CqlAnyType:
        """
        A representation of the Cql type as a python type that is useful for comparison operations.
        """
        pass

    @classmethod
    @abstractmethod
    def parse_fhir_json(
        self,
        fhir_json: _FhirJsonType,
        subtype: Optional[Type["CqlAny"]] = None,
    ) -> "CqlAny":
        """
        This method will instatiate the instance with the appropriate state based on snippet of FHIR represented as an object.
        The object should be in the format that would appear in FHIR json.
        This method returns a reference to the instance to support one line syntax such as: return my_cql_string.parse_fhir_json("foo")
        """
        pass

    @classmethod
    @abstractmethod
    def parse_cql(
        self,
        cql: str,
        subtype: Optional[Type["CqlAny"]] = None,
    ) -> "CqlAny":
        """
        This method will instatiate the instance with the appropriate state based on snippet of CQL represented as a string.
        This method returns a reference to the instance to support one line syntax such as: return my_cql_string.parse_cql("foo")
        This method will generally be called from the constructor so that the type can be instantiated in one line: return CqlString("foo")
        """
        pass
