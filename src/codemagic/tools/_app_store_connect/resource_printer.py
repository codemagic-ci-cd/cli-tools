from __future__ import annotations

import enum
import json
import pathlib
import shlex
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from codemagic.apple.resources import Profile
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import SigningCertificate
from codemagic.cli import Colors
from codemagic.utilities import log

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import ResourceManager

R = TypeVar('R', bound=Resource)
R2 = TypeVar('R2', bound=Resource)


class ResourcePrinter:

    def __init__(self, print_json: bool, print_function: Callable[[str], None]):
        self.print_json = print_json
        self.logger = log.get_logger(self.__class__)
        self.print = print_function

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
            header = f'-- {resource.__class__}{" (Created)" if resource.created else ""} --'
            self.print(Colors.BLUE(header))
            self.print(str(resource))

    def log_creating(self, resource_type: Type[R], **params):
        def fmt(item: Tuple[str, Any]):
            name, value = item
            if isinstance(value, list):
                return f'{name.replace("_", " ")}: {[shlex.quote(str(el)) for el in value]}'
            elif isinstance(value, enum.Enum):
                value = str(value.value)
            elif not isinstance(value, (str, bytes)):
                value = str(value)
            return f'{name.replace("_", " ")}: {shlex.quote(value)}'

        message = f'Creating new {resource_type}'
        if params:
            message = f'{message}: {", ".join(map(fmt, params.items()))}'
        self.logger.info(message)

    def log_created(self, resource: Resource):
        self.logger.info(Colors.GREEN(f'Created {resource.__class__} {resource.id}'))

    def log_get(self, resource_type: Type[R], resource_id: ResourceId):
        self.logger.info(f'Get {resource_type} {resource_id}')

    def log_get_related(self, related_resource_type: Type[R], resource_type: Type[R2], resource_id: ResourceId):
        self.logger.info(f'Get {related_resource_type.s} for {resource_type} {resource_id}')

    def log_found(self,
                  resource_type: Type[R],
                  resources: Sequence[R],
                  resource_filter: Optional[ResourceManager.Filter] = None,
                  related_resource_type: Optional[Type[R2]] = None):
        count = len(resources)
        name = resource_type.plural(count)
        suffix = f' matching specified filters: {resource_filter}.' if resource_filter is not None else ''
        related = f' for {related_resource_type}' if related_resource_type is not None else ''
        if count == 0:
            self.logger.info(Colors.YELLOW(f'Did not find any {name}{related}{suffix}'))
        else:
            self.logger.info(Colors.GREEN(f'Found {count} {name}{related}{suffix}'))

    def log_filtered(self, resource_type: Type[R], resources: Sequence[R], constraint: str):
        count = len(resources)
        name = resource_type.plural(count)
        if count == 0:
            self.logger.info(Colors.YELLOW(f'Did not find any {name} {constraint}'))
        else:
            self.logger.info(Colors.GREEN(f'Filtered out {count} {name} {constraint}'))

    def log_delete(self, resource_type: Type[R], resource_id: ResourceId):
        self.logger.info(f'Delete {resource_type} {resource_id}')

    def log_ignore_not_deleted(self, resource_type: Type[R], resource_id: ResourceId):
        self.logger.info(f'{resource_type} {resource_id} does not exist, did not delete.')

    def log_deleted(self, resource_type: Type[R], resource_id: ResourceId):
        self.logger.info(Colors.GREEN(f'Successfully deleted {resource_type} {resource_id}'))

    def log_saved(self, resource: Union[SigningCertificate, Profile], path: pathlib.Path):
        destination = shlex.quote(str(path))
        self.logger.info(Colors.GREEN(f'Saved {resource.__class__} {resource.get_display_info()} to {destination}'))
