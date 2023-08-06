from typing import Optional
from cqlpy._internal.parameter import Parameter
from cqlpy._internal.context.type_factory import TypeFactory
from cqlpy._internal.types.any import CqlAny


class ParameterProvider:
    def __init__(self, parameters: Optional[dict]) -> None:
        self.__parameters = parameters if parameters else {}

    def __getitem__(self, parameter: Parameter) -> Optional[CqlAny]:
        parameter_value = self.__parameters.get(parameter.name, parameter.default_value)

        if not parameter_value:
            return None

        cql_type, subtype = TypeFactory.get_type(parameter.type_name)
        return cql_type.parse_cql(cql=parameter_value, subtype=subtype)
