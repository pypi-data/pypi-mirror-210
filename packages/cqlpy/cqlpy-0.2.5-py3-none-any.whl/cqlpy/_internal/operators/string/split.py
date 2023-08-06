# 7.11 Split https://cql.hl7.org/09-b-cqlreference.html#split


def split(string_to_split: str, separator: str) -> list[str]:
    return string_to_split.split(separator)
