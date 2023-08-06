# 4.4 IsTrue https://cql.hl7.org/09-b-cqlreference.html#istrue


def is_true(argument: object) -> bool:
    return (argument == True) or (hasattr(argument, "value") and argument.value == True)
