from __future__ import annotations

import abc
import enum
from typing import Dict
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from codemagic_cli_tools.apple.resources import LinkedResourceData
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.apple.resources import ResourceType

if TYPE_CHECKING:
    from codemagic_cli_tools.apple import AppStoreConnectApiClient


class ResourceManager(metaclass=abc.ABCMeta):
    class Ordering(enum.Enum):
        def as_param(self, reverse=False):
            return f'{"-" if reverse else ""}{self.value}'

    def __init__(self, client: AppStoreConnectApiClient):
        self.client = client

    @classmethod
    def _get_update_payload(
            cls, resource_id: ResourceId, resource_type: ResourceType, attributes: Dict) -> Dict:
        return {
            'data': {
                'id': resource_id,
                'type': resource_type.value,
                'attributes': attributes
            }
        }

    @classmethod
    def _get_create_payload(cls,
                            resource_type: ResourceType, *,
                            attributes: Optional[Dict] = None,
                            relationships: Optional[Dict] = None) -> Dict:
        data = {'type': resource_type.value}
        if attributes is not None:
            data['attributes'] = attributes
        if relationships is not None:
            data['relationships'] = relationships
        return {'data': data}

    @classmethod
    def _get_resource_id(cls, resource: Union[ResourceId, LinkedResourceData]) -> ResourceId:
        if isinstance(resource, LinkedResourceData):
            return resource.id
        else:
            return resource

    @classmethod
    def _get_attribute_data(cls,
                            resource: Union[ResourceId, LinkedResourceData],
                            resource_type: ResourceType) -> Dict[str, str]:
        return {
            'id': cls._get_resource_id(resource),
            'type': resource_type.value
        }
