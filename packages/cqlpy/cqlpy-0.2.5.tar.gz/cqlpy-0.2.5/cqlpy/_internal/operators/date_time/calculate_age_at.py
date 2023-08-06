# 12.4 CalculateAgeAt https://cql.hl7.org/09-b-cqlreference.html#calculateageat

from typing import Optional

from cqlpy._internal.operators.date_time.date_time_precision import DateTimePrecision
from cqlpy._internal.types.datetime import DateTime


def calculate_age_at(
    birth_date: DateTime,
    as_of: DateTime,
    precision: Optional[DateTimePrecision] = None,
) -> int:
    return (
        as_of.value.year
        - birth_date.value.year
        - (
            (as_of.value.month, as_of.value.day)
            < (birth_date.value.month, birth_date.value.day)
        )
    )
