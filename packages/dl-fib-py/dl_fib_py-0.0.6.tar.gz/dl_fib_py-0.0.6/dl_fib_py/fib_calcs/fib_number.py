from typing import Optional


def recurring_fibonacci_number(number: int) -> int:
    if number < 0:
        raise ValueError("number must be integer greater or equal to 0")
    elif number <= 1:
        return number
    else:
        return recurring_fibonacci_number(number - 1) + recurring_fibonacci_number(
            number - 2
        )
