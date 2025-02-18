from __future__ import annotations

import enum
import json
import pathlib
import shlex
from typing import Any
from typing import Callable
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import R2
from codemagic.apple.app_store_connect.resource_manager import R
from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import Profile
from codemagic.apple.resources import Resource
from codemagic.apple.resources import SigningCertificate
from codemagic.apple.resources.resource import ResourceReference
from codemagic.cli import Colors
from codemagic.models import DictSerializable
from codemagic.models import JsonSerializable
from codemagic.utilities import log

JsonSerializableT = Union[
    Mapping[str, "JsonSerializableT"],
    Sequence["JsonSerializableT"],
    JsonSerializable,
    DictSerializable,
    str,
    int,
    float,
    bool,
    None,
]


class ResourcePrinter:
    def __init__(self, print_json: bool, print_function: Callable[[str], None]):
        self.print_json = print_json
        self.logger = log.get_logger(self.__class__)
        self.print = print_function

    def print_value(self, value: JsonSerializableT, should_print: bool):
        if not should_print:
            return
        if self.print_json:
            if isinstance(value, JsonSerializable):
                serialized = value.json(indent=4)
            elif isinstance(value, DictSerializable):
                serialized = json.dumps(value.dict(), indent=4)
            else:
                serialized = json.dumps(value, indent=4)
            self.print(serialized)
        else:
            self.print(str(value))

    def print_resources(self, resources: Sequence[R], should_print: bool):
        if should_print is not True:
            return
        if self.print_json:
            items = [resource.dict() for resource in resources]
            self.print(json.dumps(items, indent=4))
        else:
            for resource in resources:
                self.print_resource(resource, True)

    def print_resource(self, resource: R, should_print: bool):
        if should_print is not True:
            return
        if self.print_json:
            self.print(resource.json())
        else:
            header = f"-- {resource.__class__}{' (Created)' if resource.created else ''} --"
            self.print(Colors.BLUE(header))
            self.print(str(resource))

    def log_creating(self, resource_type: Type[R], **params):
        def fmt(item: Tuple[str, Any]):
            name, value = item
            value = Resource.get_id(value) if isinstance(value, Resource) else value
            name = name.replace("_", " ").replace("app store", "App Store")
            if isinstance(value, list):
                return f"{name}: {[shlex.quote(str(el)) for el in value]}"
            elif isinstance(value, enum.Enum):
                value = str(value.value)
            elif not isinstance(value, (str, bytes)):
                value = str(value)
            return f"{name}: {shlex.quote(value)}"

        message = f"Creating new {resource_type}"
        if params:
            message = f"{message}: {', '.join(map(fmt, params.items()))}"
        self.logger.info(Colors.BLUE(message))

    def log_created(self, resource: Resource):
        self.logger.info(Colors.GREEN(f"Created {resource.__class__} {resource.id}"))

    def log_get(self, resource_type: Type[R], resource_reference: ResourceReference):
        self.logger.info(f"Get {resource_type} {Resource.get_id(resource_reference)}")

    def log_get_related(
        self,
        related_resource_type: Type[R],
        resource_type: Type[R2],
        resource_reference: ResourceReference,
    ):
        self.logger.info(f"Get {related_resource_type.s} for {resource_type} {Resource.get_id(resource_reference)}")

    def log_found(
        self,
        resource_type: Type[R],
        resources: Sequence[R],
        resource_filter: Optional[ResourceManager.Filter] = None,
        related_resource_type: Optional[Type[R2]] = None,
        related_resource_reference: Optional[ResourceReference] = None,
    ):
        if related_resource_type is not None and related_resource_reference:
            related = f" for {related_resource_type} {Resource.get_id(related_resource_reference)}"
        elif related_resource_type is not None:
            related = f" for {related_resource_type}"
        else:
            related = ""

        if resource_filter is not None:
            suffix = f" matching specified filters: {resource_filter}."
        else:
            suffix = ""

        count = len(resources)
        name = resource_type.plural(count)
        if count == 0:
            self.logger.info(Colors.YELLOW(f"Did not find any {name}{related}{suffix}"))
        else:
            self.logger.info(Colors.GREEN(f"Found {count} {name}{related}{suffix}"))

    def log_filtered(self, resource_type: Type[R], resources: Sequence[R], constraint: str):
        count = len(resources)
        name = resource_type.plural(count)
        if count == 0:
            self.logger.info(Colors.YELLOW(f"Did not find any {name} {constraint}"))
        else:
            self.logger.info(Colors.GREEN(f"Filtered out {count} {name} {constraint}"))

    def log_delete(self, resource_type: Type[R], resource_reference: ResourceReference):
        self.logger.info(Colors.BLUE(f"Delete {resource_type} {Resource.get_id(resource_reference)}"))

    def log_ignore_not_deleted(self, resource_type: Type[R], resource_reference: ResourceReference):
        self.logger.info(f"{resource_type} {Resource.get_id(resource_reference)} does not exist, did not delete.")

    def log_deleted(self, resource_type: Type[R], resource_reference: ResourceReference):
        self.logger.info(Colors.GREEN(f"Successfully deleted {resource_type} {Resource.get_id(resource_reference)}"))

    def log_saved(self, resource: Union[SigningCertificate, Profile], path: pathlib.Path):
        destination = shlex.quote(str(path))
        self.logger.info(Colors.GREEN(f"Saved {resource.__class__} {resource.get_display_info()} to {destination}"))

    def log_modify(self, resource_type: Type[R], resource_reference: ResourceReference):
        self.logger.info(Colors.BLUE(f"Modify {resource_type} {Resource.get_id(resource_reference)}"))

    def log_modified(self, resource_type: Type[R], resource_reference: ResourceReference):
        self.logger.info(Colors.GREEN(f"Successfully modified {resource_type} {Resource.get_id(resource_reference)}"))
