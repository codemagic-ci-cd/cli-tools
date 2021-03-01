from typing import Callable

from codemagic.cli import Colors


class ResourcePrinter:

    def __init__(self,
                 print_function: Callable[[str], None],
                 should_print: bool = False,
                 print_json: bool = False):
        self.print = print_function
        self.should_print = should_print
        self.print_json = print_json

    def log_request(self, header):
        self.print(Colors.BLUE(header))

    def print_resource(self, result):
        if self.should_print:
            if self.print_json:
                self.print(result.json())
            else:
                self.print(str(result))
        return result
