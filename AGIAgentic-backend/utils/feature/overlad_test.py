

from typing import overload


@overload
def print_value(value: int) -> None:
    ...

@overload
def print_value(value: str) -> None:
    ...


def print_value(value: int | str) -> None:
    if isinstance(value, int):
        print(f"Integer value: {value}")
    else:
        print(f"String value: {value}")

# Example usage
print_value(42)        # Should print: Integer value: 42
print_value("Hello")   # Should print: String value: Hello