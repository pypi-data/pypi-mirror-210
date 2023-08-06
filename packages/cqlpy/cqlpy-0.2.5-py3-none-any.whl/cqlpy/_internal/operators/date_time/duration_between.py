from cqlpy._internal.operators.date_time.date_time_precision import DateTimePrecision
from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.types.datetime import DateTime
from cqlpy._internal.types.null import Null, Some

from dateutil.relativedelta import relativedelta


# 8.8 Duration Between https://cql.hl7.org/09-b-cqlreference.html#duration


def duration_between(
    low: DateTime, high: DateTime, precision: DateTimePrecision
) -> Some[int]:
    if is_null(low) or is_null(high):
        return Null()
    elif precision == DateTimePrecision.Day:
        return (high.value - low.value).days
    elif precision == DateTimePrecision.Month:
        (high.value.year - low.value.year) * 12 + high.value.month - low.value.month
    elif precision == DateTimePrecision.Year:
        return relativedelta(high.value, low.value).years
    return Null()
