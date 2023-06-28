from packaging.version import InvalidVersion
from packaging.version import Version
from packaging.version import parse as _parse


def parse_version(given_version: str) -> Version:
    if not isinstance(given_version, str):
        raise TypeError(f"expected string, got {type(given_version).__name__}")

    # Clean up versions such as v.1.2.3
    cleaned_version = given_version.lstrip("vV.")
    try:
        return _parse(cleaned_version)
    except InvalidVersion as iv:
        raise ValueError("Invalid version", given_version) from iv


def sorting_key(given_version: str) -> Version:
    try:
        return parse_version(given_version)
    except ValueError:
        # Invalid version was given, just treat it as the lowest version possible
        return Version("0")
