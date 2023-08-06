# 3.20 ToDateTime https://cql.hl7.org/09-b-cqlreference.html#todatetime


from typing import Union

from cqlpy._internal.types.date import Date
from cqlpy._internal.types.datetime import DateTime


def to_datetime(argument: Union[Date, DateTime]) -> DateTime:
    return argument
