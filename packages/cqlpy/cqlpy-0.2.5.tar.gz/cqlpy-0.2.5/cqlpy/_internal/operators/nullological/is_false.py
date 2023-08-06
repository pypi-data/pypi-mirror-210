# 4.3 IsFalse https://cql.hl7.org/09-b-cqlreference.html#isfalse


def is_false(argument: object) -> bool:
    return (argument == False) or (
        hasattr(argument, "value") and argument.value == False
    )
