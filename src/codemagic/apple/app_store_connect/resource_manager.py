from __future__ import annotations

import abc
import enum
import re
import shlex
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Generic
from typing import Optional
from typing import Sequence
from typing import Type
from typing import TypeVar
from typing import Union

from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType

if TYPE_CHECKING:
    from codemagic.apple import AppStoreConnectApiClient

R = TypeVar('R', bound=Resource)
R2 = TypeVar('R2', bound=Resource)


class ResourceManager(Generic[R], metaclass=abc.ABCMeta):
    class Filter:
        @classmethod
        def _get_field_name(cls, field_name) -> str:
            return cls._snake_to_camel(field_name)

        @classmethod
        def _snake_to_camel(cls, field_name: str) -> str:
            patt = re.compile(r'_(\w)')
            return patt.sub(lambda m: m.group(1).upper(), field_name)

        @classmethod
        def _get_param_value(cls, field_value) -> str:
            if isinstance(field_value, enum.Enum):
                return str(field_value.value)
            elif isinstance(field_value, str):
                return field_value
            elif isinstance(field_value, Sequence):
                return ','.join(cls._get_param_value(element) for element in field_value)
            return str(field_value)

        def _get_restrictions(self) -> Dict[str, str]:
            return {
                self._get_field_name(field_name): self._get_param_value(value)
                for field_name, value in self.__dict__.items()
                if value is not None
            }

        def as_query_params(self) -> Dict[str, str]:
            return {f'filter[{field}]': p for field, p in self._get_restrictions().items()}

        @classmethod
        def _field_matches(cls, field_value, resource_value):
            if field_value is None:
                return True
            return field_value == resource_value

        def __bool__(self):
            return any(self.__dict__.values())

        def __str__(self):
            restrictions = self._get_restrictions()
            if not restrictions:
                return '*'
            return ', '.join(f'{param}={shlex.quote(value)}' for param, value in restrictions.items())

    class Ordering(enum.Enum):
        def as_param(self, reverse=False) -> str:
            return f'{"-" if reverse else ""}{self.value}'

    def __init__(self, client: AppStoreConnectApiClient):
        self.client = client

    @property
    @abc.abstractmethod
    def resource_type(self) -> Type[R]:
        raise NotImplementedError()

    @classmethod
    def _get_include_field_name(cls, include_type: Type[R]) -> str:
        raise NotImplemented  # noqa: F901

    @classmethod
    def _get_update_payload(
            cls,
            resource_id: ResourceId,
            resource_type: ResourceType,
            *,
            attributes: Optional[Dict] = None,
            relationships: Optional[Dict] = None,
    ) -> Dict:
        data: Dict[str, Any] = {
            'id': resource_id,
            'type': resource_type.value,
        }
        if attributes:
            data['attributes'] = attributes
        if relationships:
            data['relationships'] = relationships
        return {'data': data}

    @classmethod
    def _get_create_payload(cls,
                            resource_type: ResourceType, *,
                            attributes: Optional[Dict] = None,
                            relationships: Optional[Dict] = None) -> Dict[str, Dict[str, Any]]:
        data: Dict[str, Any] = {'type': resource_type.value}
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
            'type': resource_type.value,
        }
