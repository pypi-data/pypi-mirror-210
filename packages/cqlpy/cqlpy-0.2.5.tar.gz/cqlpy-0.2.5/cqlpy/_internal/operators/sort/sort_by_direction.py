def sort_by_direction(input_: list, direction: str = "asc") -> list:
    input_.sort(reverse=(direction == "desc"))
    return input_
