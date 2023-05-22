from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Generic
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar

from ..resources.abstract_resource import AbstractResource


@dataclass
class AbstractParentIdentifier(ABC):
    @property
    @abstractmethod
    def uri(self) -> str:
        ...


R = TypeVar('R', bound=AbstractResource)
PI = TypeVar('PI', bound=AbstractParentIdentifier)


class ResourceManager(Generic[R, PI], ABC):
    Resource: Type[R]
    ParentIdentifier: Type[PI]

    class OrderBy(Enum):
        create_time_desc = 'createTimeDesc'
        create_time_asc = 'createTime'

    def __init__(self, service):
        self.service = service

    @property
    @abstractmethod
    def _resource(self):
        ...

    def _list_page(
            self, parent_identifier: PI, order_by: OrderBy, page_size: int, page_token: Optional[str],
    ) -> Tuple[List[R], Optional[str]]:
        response = self._resource.list(
            orderBy=order_by.value,
            pageSize=page_size,
            pageToken=page_token,
            parent=parent_identifier.uri,
        ).execute()
        return [self.Resource(**item) for item in response[self.Resource.label]], response.get('nextPageToken')

    def list(
        self,
        parent_identifier: PI,
        order_by: OrderBy = OrderBy.create_time_desc,
        limit: Optional[int] = None,
        page_size: int = 25,
    ) -> List[R]:
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

        return items
