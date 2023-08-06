# 6.12 Minimum https://cql.hl7.org/09-b-cqlreference.html#minimum


from cqlpy._internal.types.datetime import DateTime
from cqlpy._internal.types.null import Null, Some


def min_value(type_name: str) -> Some:
    if type_name == "DateTime":
        return DateTime(1, 1, 1, 0, 0, 0, 0)
    else:
        return Null()
