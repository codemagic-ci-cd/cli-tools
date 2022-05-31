from __future__ import annotations

from typing import Callable
from typing import List
from typing import Optional
from typing import Type

from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.app_store_connect.resource_manager import R2
from codemagic.apple.app_store_connect.resource_manager import R
from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import ResourceId

from .errors import AppStoreConnectError
from .resource_printer import ResourcePrinter


class ResourceManagerMixin:
    printer: ResourcePrinter

    def _create_resource(
        self,
        resource_manager: ResourceManager[R],
        should_print: bool,
        **create_params,
    ) -> R:
        try:
            create_resource: Callable[..., R] = getattr(resource_manager, 'create')
        except AttributeError:
            raise RuntimeError('Resource manager cannot create resources', resource_manager)

        omit_keys = create_params.pop('omit_keys', tuple())
        self.printer.log_creating(
            resource_manager.resource_type,
            **{k: v for k, v in create_params.items() if k not in omit_keys},
        )
        try:
            resource = create_resource(**create_params)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error)) from api_error

        self.printer.print_resource(resource, should_print)
        self.printer.log_created(resource)
        return resource

    def _get_resource(
        self,
        resource_id: ResourceId,
        resource_manager: ResourceManager[R],
        should_print: bool,
    ) -> R:
        try:
            read_resource: Callable[[ResourceId], R] = getattr(resource_manager, 'read')
        except AttributeError:
            raise RuntimeError('Resource manager cannot read resources', resource_manager)

        self.printer.log_get(resource_manager.resource_type, resource_id)
        try:
            resource = read_resource(resource_id)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))
        self.printer.print_resource(resource, should_print)
        return resource

    def _list_resources(
        self,
        resource_filter: ResourceManager.Filter,
        resource_manager: ResourceManager[R],
        should_print: bool,
        filter_predicate: Optional[Callable[[R], bool]] = None,
    ) -> List[R]:
        try:
            list_resources: Callable[..., List[R]] = getattr(resource_manager, 'list')
        except AttributeError:
            raise RuntimeError('Resource manager cannot list resources', resource_manager)

        try:
            resources = list_resources(resource_filter=resource_filter)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        if filter_predicate is not None:
            resources = list(filter(filter_predicate, resources))

        self.printer.log_found(resource_manager.resource_type, resources, resource_filter)
        self.printer.print_resources(resources, should_print)
        return resources

    def _get_related_resource(
        self,
        resource_id: ResourceId,
        resource_type: Type[R],
        related_resource_type: Type[R2],
        read_related_resource_method: Callable[..., Optional[R2]],
        should_print: bool,
    ) -> R2:
        self.printer.log_get_related(related_resource_type, resource_type, resource_id)

        try:
            resource = read_related_resource_method(resource_id)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        if resource is None:
            raise AppStoreConnectError(f'{related_resource_type} was not found for {resource_type} {resource_id}')

        self.printer.print_resource(resource, should_print)
        return resource

    def _list_related_resources(
        self,
        resource_id: ResourceId,
        resource_type: Type[R],
        related_resource_type: Type[R2],
        list_related_resources_method: Callable[..., List[R2]],
        resource_filter: Optional[ResourceManager.Filter],
        should_print: bool,
    ) -> List[R2]:
        self.printer.log_get_related(related_resource_type, resource_type, resource_id)
        kwargs = {'resource_filter': resource_filter} if resource_filter else {}

        try:
            resources = list_related_resources_method(resource_id, **kwargs)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        self.printer.log_found(related_resource_type, resources, resource_filter, resource_type, resource_id)
        self.printer.print_resources(resources, should_print)
        return resources

    def _delete_resource(
        self,
        resource_manager: ResourceManager[R],
        resource_id: ResourceId,
        ignore_not_found: bool,
    ):
        try:
            delete_resource: Callable[[ResourceId], None] = getattr(resource_manager, 'delete')
        except AttributeError:
            raise RuntimeError('Resource manager cannot delete resources', resource_manager)

        self.printer.log_delete(resource_manager.resource_type, resource_id)
        try:
            delete_resource(resource_id)
        except AppStoreConnectApiError as api_error:
            if ignore_not_found is True and api_error.status_code == 404:
                self.printer.log_ignore_not_deleted(resource_manager.resource_type, resource_id)
            else:
                raise AppStoreConnectError(str(api_error))
        else:
            self.printer.log_deleted(resource_manager.resource_type, resource_id)

    def _modify_resource(
        self,
        resource_manager: ResourceManager[R],
        resource_id: ResourceId,
        should_print: bool,
        **update_params,
    ) -> R:
        try:
            modify_resource: Callable[..., R] = getattr(resource_manager, 'modify')
        except AttributeError:
            raise RuntimeError('Resource manager cannot modify resources', resource_manager)

        self.printer.log_modify(resource_manager.resource_type, resource_id)
        try:
            resource = modify_resource(resource_id, **update_params)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        self.printer.log_modified(resource_manager.resource_type, resource_id)
        self.printer.print_resource(resource, should_print)
        return resource
