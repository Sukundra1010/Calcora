import math


def calculate(first_number, operator, second_number=None):
    if operator == "sign":
        result = -first_number
    elif operator == "percent":
        result = first_number / 100
    elif operator == "+":
        result = first_number + second_number
    elif operator == "-":
        result = first_number - second_number
    elif operator == "*":
        result = first_number * second_number
    elif operator == "/":
        if second_number == 0:
            raise ValueError("Cannot divide by zero.")
        result = first_number / second_number
    else:
        raise ValueError("Unknown operation.")

    if not math.isfinite(result):
        raise ValueError("Result is too large.")
    return result
