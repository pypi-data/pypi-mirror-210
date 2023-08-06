def sort_by_expression(input_: list, direction: str = "asc") -> list:
    input_.sort(reverse=(direction == "desc"), key=tuple_sort)
    return [item[1] for item in input_]
