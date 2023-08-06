from cqlpy._internal.operators.sort.sort_by_expression import sort_by_expression


def sort_by_column(input_: list, field_name: str, direction: str = "asc") -> list:
    return sort_by_expression([(item[field_name], item) for item in input_], direction)
