from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar

from googleapiclient import discovery
from typing_extensions import Protocol

from ..resources.resource import Resource

ResourceT = TypeVar('ResourceT', bound=Resource)
ParentResourceIdentifierT = TypeVar('ParentResourceIdentifierT', bound='ParentResourceIdentifier')


class ParentResourceIdentifier(ABC):
    @property
    @abstractmethod
    def uri(self) -> str:
        ...


class PExecutableInterface(Protocol):
    def execute(self) -> Dict[str, Any]:
        ...


class PListableInterface(Protocol):
    def list(self, **kwargs) -> PExecutableInterface:
        ...


class ResourceManager(Generic[ResourceT, ParentResourceIdentifierT], ABC):
    @property
    @abstractmethod
    def resource_type(self) -> Type[ResourceT]:
        ...

    class OrderBy(Enum):
        create_time_desc = 'createTimeDesc'
        create_time_asc = 'createTime'

    def __init__(self, discovery_service: discovery.Resource):
        self._discovery_service = discovery_service

    @property
    @abstractmethod
    def _discovery_interface(self) -> PListableInterface:
        ...

    def _list_page(
        self,
        parent_identifier: ParentResourceIdentifierT,
        order_by: OrderBy,
        page_size: int,
        page_token: Optional[str],
    ) -> Tuple[List[ResourceT], Optional[str]]:
        response = self._discovery_interface.list(
            orderBy=order_by.value,
            pageSize=page_size,
            pageToken=page_token,
            parent=parent_identifier.uri,
        ).execute()
        return (
            [self.resource_type(**item) for item in response[self.resource_type.label]],
            response.get('nextPageToken'),
        )

    def list(
        self,
        parent_identifier: ParentResourceIdentifierT,
        order_by: OrderBy = OrderBy.create_time_desc,
        limit: Optional[int] = None,
        page_size: int = 25,
    ) -> List[ResourceT]:
        page_size = min(limit, page_size) if limit else page_size

        items = []
        page_token = None
        while True:
            page_items, page_token = self._list_page(parent_identifier, order_by, page_size, page_token)

            items.extend(page_items)

            if limit and len(items) > limit:
                break

            if not page_token:
                break

        return items[:limit]
