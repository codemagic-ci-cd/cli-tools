from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from googleapiclient.http import HttpRequest

from codemagic.google.resources import OrderBy

from .acting_manager_mixin import ActingManagerMixin

if TYPE_CHECKING:
    from codemagic.google.resources.identifiers import ResourceIdentifier
    from codemagic.google.resources.resource import Resource

ResourceT = TypeVar("ResourceT", bound="Resource")
ResourceIdentifierT = TypeVar("ResourceIdentifierT", bound="ResourceIdentifier")


class ListingManagerMixin(Generic[ResourceT, ResourceIdentifierT], ActingManagerMixin[ResourceT], ABC):
    manager_action: ClassVar[str] = "list"

    @dataclass
    class PageRequestArguments:
        order_by: OrderBy
        page_size: int
        page_token: Optional[str]
        parent_uri: str

        def as_request_kwargs(self):
            return {
                "orderBy": self.order_by.value,
                "pageSize": self.page_size,
                "pageToken": self.page_token,
                "parent": self.parent_uri,
            }

    @abstractmethod
    def _get_resources_page_request(self, arguments: PageRequestArguments) -> HttpRequest:
        ...

    def list(
        self,
        parent_identifier: ResourceIdentifierT,
        order_by: OrderBy = OrderBy.CREATE_TIME_DESC,
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

            # In case no matches are found, then the relevant key is missing from response
            response_items = response.get(self.resource_type.get_label(), [])
            resources.extend(self.resource_type(**item) for item in response_items)
            page_request_args.page_token = response.get("nextPageToken")

            if limit and len(resources) > limit:
                break
            if not page_request_args.page_token:
                break
        return resources[:limit]
