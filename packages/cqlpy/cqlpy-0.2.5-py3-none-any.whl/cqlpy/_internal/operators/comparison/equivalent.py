# 5.3 Equivalent https://cql.hl7.org/09-b-cqlreference.html#equivalent


from cqlpy._internal.types.concept import Concept


def equivalent(left, right) -> bool:
    if isinstance(left, Concept) and isinstance(right, Concept):
        return any(
            code_left.code == code_right.code
            for code_left in left.codes
            for code_right in right.codes
        )
    return (
        hasattr(left, "value")
        and hasattr(right, "value")
        and (left.value == right.value)
    )
