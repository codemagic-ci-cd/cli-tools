from _typeshed import Incomplete

from . import Traceback as Traceback

class Error:
    exc_type: Incomplete
    exc_value: Incomplete
    def __init__(self, exc_type, exc_value, traceback) -> None: ...
    @property
    def traceback(self): ...
    def reraise(self) -> None: ...

def return_error(func, exc_type=...): ...
returns_error = return_error
return_errors = return_error
returns_errors = return_error

def apply_with_return_error(args): ...
