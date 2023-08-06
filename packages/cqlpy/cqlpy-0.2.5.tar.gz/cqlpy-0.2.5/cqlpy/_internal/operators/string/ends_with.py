# 7.3 EndsWith https://cql.hl7.org/09-b-cqlreference.html#endswith


def ends_with(argument: str, suffix: str) -> bool:
    return argument[-len(suffix) :] == suffix
