from functools import wraps
from typing import Optional

from codemagic.cli import Colors
from codemagic.utilities import log


def deprecated(
    deprecation_version: str,
    comment: Optional[str] = None,
    color: Optional[Colors] = Colors.YELLOW,
):
    def decorator(function):
        if "<locals>" in function.__qualname__:
            qualifier = function.__qualname__.split(">.")[-1]
        else:
            qualifier = function.__qualname__

        message = (
            "Deprecation warning! "
            f'"{qualifier}" was deprecated in version {deprecation_version} '
            "and is subject for removal in future releases."
        )
        if comment:
            message = f"{message} {comment}"
        if color:
            message = color(message)

        @wraps(function)
        def wrapper(*args, **kwargs):
            log.get_logger(function).warning(message)
            return function(*args, **kwargs)

        return wrapper

    return decorator
