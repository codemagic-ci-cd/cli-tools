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


def run_once(function):
    """
    Ensure that decorated function is executed only once.
    Cache the result for subsequent calls unless the function
    fails with an exception.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.return_value = function(*args, **kwargs)
            wrapper.has_run = True
        return wrapper.return_value

    wrapper.has_run = False
    return wrapper
