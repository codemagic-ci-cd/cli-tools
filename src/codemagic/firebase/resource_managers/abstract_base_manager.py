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

from ..resources.abstract_base_resource import AbstractFirebaseResource

R = TypeVar('R', bound=AbstractFirebaseResource)


class FirebaseResourceManager(Generic[R], ABC):
    Resource: Type[R]

    class OrderBy(Enum):
        create_time_desc = 'createTimeDesc'
        create_time_asc = 'createTime'

    @classmethod
    def resource(cls, service) -> Any:
        ...

    @property
    @abstractmethod
    def query_parameters(self) -> Dict[str, str]:
        ...

    def _list_page_resource_items(
            self, service, order_by: OrderBy, page_size: int, page_token: Optional[str],
    ) -> Tuple[List[R], Optional[str]]:
        resource = self.resource(service)
        response = resource.list(
            orderBy=order_by.value,
            pageSize=page_size,
            pageToken=page_token,
            **self.query_parameters,
        ).execute()
        return [self.Resource(**item) for item in response[self.Resource.label]], response.get('nextPageToken')

    def iterate_resource_items(self, service, order_by: OrderBy, limit: Optional[int], page_size: int):
        page_size = min(limit, page_size) if limit else page_size

        page_token = None
        count = 0
        while True:
            items, page_token = self._list_page_resource_items(service, order_by, page_size, page_token)

            yield from items

            count += len(items)
            if limit and count > limit:
                break

            if not page_token:
                break
