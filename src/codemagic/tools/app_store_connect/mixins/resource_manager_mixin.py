from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Callable
from typing import List
from typing import Optional
from typing import Type

from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.app_store_connect.resource_manager import R2
from codemagic.apple.app_store_connect.resource_manager import R
from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceReference

from ..errors import AppStoreConnectError
from ..resource_printer import ResourcePrinter

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import CreatingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import DeletingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ListingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ModifyingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ReadingResourceManager


class ResourceManagerMixin:
    printer: ResourcePrinter

    def _create_resource(
        self,
        resource_manager: CreatingResourceManager[R],
        should_print: bool,
        **create_params,
    ) -> R:
        omit_keys = create_params.pop("omit_keys", tuple())
        self.printer.log_creating(
            resource_manager.resource_type,
            **{k: v for k, v in create_params.items() if k not in omit_keys},
        )
        try:
            resource = resource_manager.create(**create_params)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                str(api_error),
                api_error_response=api_error.error_response,
            ) from api_error

        self.printer.print_resource(resource, should_print)
        self.printer.log_created(resource)
        return resource

    def _get_resource(
        self,
        resource_reference: ResourceReference,
        resource_manager: ReadingResourceManager[R],
        should_print: bool,
    ) -> R:
        self.printer.log_get(resource_manager.resource_type, resource_reference)
        try:
            resource = resource_manager.read(resource_reference)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                str(api_error),
                api_error_response=api_error.error_response,
            ) from api_error
        self.printer.print_resource(resource, should_print)
        return resource

    def _list_resources(
        self,
        resource_filter: ResourceManager.Filter,
        resource_manager: ListingResourceManager[R],
        should_print: bool,
        filter_predicate: Optional[Callable[[R], bool]] = None,
    ) -> List[R]:
        try:
            resources = resource_manager.list(resource_filter=resource_filter)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                str(api_error),
                api_error_response=api_error.error_response,
            ) from api_error

        if filter_predicate is not None:
            resources = list(filter(filter_predicate, resources))

        self.printer.log_found(resource_manager.resource_type, resources, resource_filter)
        self.printer.print_resources(resources, should_print)
        return resources

    def _get_related_resource(
        self,
        resource_reference: ResourceReference,
        resource_type: Type[R],
        related_resource_type: Type[R2],
        read_related_resource_method: Callable[..., Optional[R2]],
        should_print: bool,
    ) -> R2:
        self.printer.log_get_related(related_resource_type, resource_type, resource_reference)

        try:
            resource = read_related_resource_method(resource_reference)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                str(api_error),
                api_error_response=api_error.error_response,
            ) from api_error

        if resource is None:
            resource_id = Resource.get_id(resource_reference)
            raise AppStoreConnectError(f"{related_resource_type} was not found for {resource_type} {resource_id}")

        self.printer.print_resource(resource, should_print)
        return resource

    def _list_related_resources(
        self,
        resource_reference: ResourceReference,
        resource_type: Type[R],
        related_resource_type: Type[R2],
        list_related_resources_method: Callable[..., List[R2]],
        resource_filter: Optional[ResourceManager.Filter],
        should_print: bool,
        filter_predicate: Optional[Callable[[R2], bool]] = None,
    ) -> List[R2]:
        self.printer.log_get_related(related_resource_type, resource_type, resource_reference)
        kwargs = {"resource_filter": resource_filter} if resource_filter else {}

        try:
            resources = list_related_resources_method(resource_reference, **kwargs)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                str(api_error),
                api_error_response=api_error.error_response,
            ) from api_error

        if filter_predicate is not None:
            resources = list(filter(filter_predicate, resources))

        self.printer.log_found(related_resource_type, resources, resource_filter, resource_type, resource_reference)
        self.printer.print_resources(resources, should_print)
        return resources

    def _delete_resource(
        self,
        resource_manager: DeletingResourceManager[R],
        resource_reference: ResourceReference,
        ignore_not_found: bool,
    ):
        self.printer.log_delete(resource_manager.resource_type, resource_reference)
        try:
            resource_manager.delete(resource_reference)
        except AppStoreConnectApiError as api_error:
            if ignore_not_found is True and api_error.status_code == 404:
                self.printer.log_ignore_not_deleted(resource_manager.resource_type, resource_reference)
            else:
                raise AppStoreConnectError(
                    str(api_error),
                    api_error_response=api_error.error_response,
                ) from api_error
        else:
            self.printer.log_deleted(resource_manager.resource_type, resource_reference)

    def _modify_resource(
        self,
        resource_manager: ModifyingResourceManager[R],
        resource_reference: ResourceReference,
        should_print: bool,
        **update_params,
    ) -> R:
        self.printer.log_modify(resource_manager.resource_type, resource_reference)
        try:
            resource = resource_manager.modify(resource_reference, **update_params)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                str(api_error),
                api_error_response=api_error.error_response,
            ) from api_error

        self.printer.log_modified(resource_manager.resource_type, resource_reference)
        self.printer.print_resource(resource, should_print)
        return resource
