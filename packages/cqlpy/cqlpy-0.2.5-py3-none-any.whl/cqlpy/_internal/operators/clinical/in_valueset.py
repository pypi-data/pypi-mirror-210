# 12.8 In (ValueSet) https://cql.hl7.org/09-b-cqlreference.html#in-valueset


from typing import Union
from cqlpy._internal.operators.nullological.is_null import is_null

from cqlpy._internal.types.code import Code
from cqlpy._internal.types.concept import Concept
from cqlpy._internal.types.null import Some
from cqlpy._internal.types.value_set import ValueSet


def in_valueset(argument: Some[Union[str, Code, Concept]], value_set: ValueSet) -> bool:
    if is_null(argument):
        return False

    elif isinstance(argument, str):
        for value_set_code in value_set.codes:
            if argument == value_set_code:
                return True

    elif isinstance(argument, Code):
        for value_set_code in value_set.codes:
            if argument.code == value_set_code.code:
                return True

    elif isinstance(argument, Concept):
        for code in argument.codes:
            for value_set_code in value_set.codes:
                if code.code == value_set_code.code:
                    return True

    return False
