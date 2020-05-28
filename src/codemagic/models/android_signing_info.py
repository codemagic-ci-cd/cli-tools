import pathlib
from typing import NamedTuple


class AndroidSigningInfo(NamedTuple):
    store_path: pathlib.Path
    store_pass: str
    key_alias: str
    key_pass: str
