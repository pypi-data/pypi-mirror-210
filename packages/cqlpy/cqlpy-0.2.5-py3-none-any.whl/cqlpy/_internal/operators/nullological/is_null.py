from cqlpy._internal.types.null import Null

# 4.2 IsNull https://cql.hl7.org/09-b-cqlreference.html#isnull


def is_null(argument: object) -> bool:
    return (
        (argument is None)
        or (argument == Null)
        or (
            hasattr(argument, "value")
            and ((argument.value is None) or (argument.value == Null))
        )
    )
