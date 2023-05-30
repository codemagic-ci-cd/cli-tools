from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import TypeVar

from googleapiclient.http import HttpRequest

from ..resource_manager import ResourceManager
from .abstract_resource_manager_mixin import AbstractResourceManagerMixin

if TYPE_CHECKING:
    from ...resources.identifiers import ResourceIdentifier
    from ...resources.resource import Resource

ResourceT = TypeVar('ResourceT', bound='Resource')
ResourceIdentifierT = TypeVar('ResourceIdentifierT', bound='ResourceIdentifier')


class ListableResourceManagerMixin(AbstractResourceManagerMixin[ResourceT, ResourceIdentifierT]):
    action = 'list'

    @dataclass
    class PageRequestArguments:
        order_by: ResourceManager.OrderBy
        page_size: int
        page_token: Optional[str]
        parent_uri: str

        def as_request_kwargs(self):
            return {
                'orderBy': self.order_by.value,
                'pageSize': self.page_size,
                'pageToken': self.page_token,
                'parent': self.parent_uri,
            }

    @abstractmethod
    def _get_resources_page_request(self, arguments: PageRequestArguments) -> HttpRequest:
        raise NotImplementedError()

    def list(
        self,
        parent_identifier: ResourceIdentifierT,
        order_by: ResourceManager.OrderBy = ResourceManager.OrderBy.create_time_desc,
        limit: Optional[int] = None,
        page_size: int = 25,
    ) -> List[ResourceT]:
        page_request_args = self.PageRequestArguments(
            order_by=order_by,
            page_size=min(limit, page_size) if limit else page_size,
            page_token=None,
            parent_uri=parent_identifier.uri,
        )

        resources: List[ResourceT] = []
        while True:
            request = self._get_resources_page_request(page_request_args)
            response = self._execute_request(request)

            resources.extend(self.resource_type(**item) for item in response[self.resource_type.get_label()])
            page_request_args.page_token = response.get('nextPageToken')

            if limit and len(resources) > limit:
                break
            if not page_request_args.page_token:
                break
        return resources[:limit]
