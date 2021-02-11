def get_binary_arguments_value(value, not_value):
    if value and not_value:
        raise Exception

    if not value and not not_value:
        return None

    return value or not not_value
