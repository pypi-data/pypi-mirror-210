# 5.5 Greater or Equal https://cql.hl7.org/09-b-cqlreference.html#greater-or-equal


from cqlpy._internal.operators.nullological.is_null import is_null
from cqlpy._internal.types.quantity import Quantity


def greater_or_equal(left, right) -> bool:
    if is_null(left) or is_null(right):
        return False
    else:
        left_value = (
            left["value"]
            if left.__class__.__name__ == "Resource"
            else left.value
            if isinstance(left, Quantity)
            else left
        )
        right_value = (
            right["value"]
            if right.__class__.__name__ == "Resource"
            else right.value
            if isinstance(right, Quantity)
            else right
        )
        return left >= right
