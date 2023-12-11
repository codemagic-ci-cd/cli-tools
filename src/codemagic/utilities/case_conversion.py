import re


def snake_to_camel(snake_case: str) -> str:
    return re.sub(r"_(\w)", lambda m: m.group(1).upper(), snake_case)


def camel_to_snake(camel_case: str) -> str:
    return re.sub(r"([A-Z])", lambda m: f"_{m.group(1).lower()}", camel_case).lstrip("_")
