import os


def is_ci_environment() -> bool:
    """
    Check if environment variable "CI" is set and if it has a truthy value
    """
    ci_environment_value = os.environ.get("CI")
    if ci_environment_value is None:
        return False
    return ci_environment_value.lower() in ("1", "t", "true", "y", "yes")
