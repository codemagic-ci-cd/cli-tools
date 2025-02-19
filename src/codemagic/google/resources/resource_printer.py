from __future__ import annotations

import json
from typing import Callable
from typing import Sequence

from codemagic.cli import Colors
from codemagic.google.resources import Resource


class ResourcePrinter:
    def __init__(self, print_json: bool, print_function: Callable[[str], None]):
        self.print_json = print_json
        self.print = print_function

    def print_resources(self, resources: Sequence[Resource], should_print: bool):
        if not should_print:
            return
        if self.print_json:
            items = [resource.dict() for resource in resources]
            self.print(json.dumps(items, indent=4))
        else:
            for resource in resources:
                self.print_resource(resource, True)

    def print_resource(self, resource: Resource, should_print: bool):
        if not should_print:
            return
        if self.print_json:
            self.print(json.dumps(resource.dict(), indent=4))
        else:
            header = f"-- {resource.__class__.__name__} --"
            self.print(f"{Colors.BLUE(header)}\n{resource}\n")
