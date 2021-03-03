from typing import Callable
from typing import TypeVar

from codemagic.cli import Colors

from .resources.resource import Resource

ResourceToPrint = TypeVar('ResourceToPrint', bound=Resource)


class ResourcePrinter:

    def __init__(self,
                 should_print: bool = False,
                 print_json: bool = False,
                 print_function: Callable[[str], None] = None):
        self.print = print_function
        self.should_print = should_print
        self.print_json = print_json

    def log_request(self, header: str) -> None:
        if not self.print:
            return
        self.print(Colors.BLUE(header))

    def print_resource(self, resource: ResourceToPrint) -> None:
        if not self.print:
            return
        if self.should_print:
            if self.print_json:
                self.print(resource.json())
            else:
                self.print(str(resource))
