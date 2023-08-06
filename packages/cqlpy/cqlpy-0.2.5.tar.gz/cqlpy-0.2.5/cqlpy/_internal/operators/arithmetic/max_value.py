# 6.11 Maximum https://cql.hl7.org/09-b-cqlreference.html#maximum

from cqlpy._internal.types.datetime import DateTime
from cqlpy._internal.types.null import Null, Some


def max_value(type_name: str) -> Some[DateTime]:
    if type_name == "DateTime":
        return DateTime(9999, 12, 31, 23, 59, 59, 999)
    else:
        return Null()
