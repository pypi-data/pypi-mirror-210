# 10.6 Exists https://cql.hl7.org/09-b-cqlreference.html#exists


from cqlpy._internal.operators.nullological.is_null import is_null


def exists(argument: list) -> bool:
    return (not is_null(argument)) and (len(argument) > 0)
