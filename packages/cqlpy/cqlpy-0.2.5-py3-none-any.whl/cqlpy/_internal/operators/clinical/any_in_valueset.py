# 12.8 In (ValueSet) https://cql.hl7.org/09-b-cqlreference.html#in-valueset


from typing import Union
from cqlpy._internal.operators.clinical.in_valueset import in_valueset
from cqlpy._internal.operators.nullological.is_null import is_null

from cqlpy._internal.types.code import Code
from cqlpy._internal.types.concept import Concept
from cqlpy._internal.types.null import Some
from cqlpy._internal.types.value_set import ValueSet


def any_in_valueset(
    argument: list[Some[Union[str, Code, Concept]]], value_set: ValueSet
) -> bool:
    if not is_null(argument):
        for item in argument:
            if in_valueset(item, value_set):
                return True

    return False
