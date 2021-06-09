from typing import Callable
from typing import Optional

from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceId

from .errors import AppStoreConnectError
from .resource_printer import ResourcePrinter


class ResourceManagerMixin:
    printer: ResourcePrinter

    def _create_resource(self, resource_manager, should_print, **create_params):
        omit_keys = create_params.pop('omit_keys', tuple())
        self.printer.log_creating(
            resource_manager.resource_type,
            **{k: v for k, v in create_params.items() if k not in omit_keys},
        )
        try:
            resource = resource_manager.create(**create_params)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        self.printer.print_resource(resource, should_print)
        self.printer.log_created(resource)
        return resource

    def _get_resource(self, resource_id, resource_manager, should_print):
        self.printer.log_get(resource_manager.resource_type, resource_id)
        try:
            resource = resource_manager.read(resource_id)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))
        self.printer.print_resource(resource, should_print)
        return resource

    def _list_resources(self,
                        resource_filter,
                        resource_manager,
                        should_print: bool,
                        filter_predicate: Optional[Callable[[Resource], bool]] = None):
        try:
            resources = resource_manager.list(resource_filter=resource_filter)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        if filter_predicate is not None:
            resources = list(filter(filter_predicate, resources))

        self.printer.log_found(resource_manager.resource_type, resources, resource_filter)
        self.printer.print_resources(resources, should_print)
        return resources

    def _get_related_resource(self,
                              resource_id,
                              resource_type,
                              related_resource_type,
                              read_related_resource_method,
                              should_print: bool):
        self.printer.log_get_related(related_resource_type, resource_type, resource_id)
        try:
            resource = read_related_resource_method(resource_id)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))
        self.printer.print_resource(resource, should_print)
        return resource

    def _list_related_resources(self,
                                resource_id: ResourceId,
                                resource_type,
                                related_resource_type,
                                list_related_resources_method,
                                resource_filter,
                                should_print: bool):
        self.printer.log_get_related(related_resource_type, resource_type, resource_id)
        try:
            kwargs = {'resource_filter': resource_filter} if resource_filter else {}
            resources = list_related_resources_method(resource_id, **kwargs)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        self.printer.log_found(related_resource_type, resources, resource_filter, resource_type)
        self.printer.print_resources(resources, should_print)
        return resources

    def _delete_resource(self, resource_manager, resource_id: ResourceId, ignore_not_found: bool):
        self.printer.log_delete(resource_manager.resource_type, resource_id)
        try:
            resource_manager.delete(resource_id)
            self.printer.log_deleted(resource_manager.resource_type, resource_id)
        except AppStoreConnectApiError as api_error:
            if ignore_not_found is True and api_error.status_code == 404:
                self.printer.log_ignore_not_deleted(resource_manager.resource_type, resource_id)
            else:
                raise AppStoreConnectError(str(api_error))

    def _modify_resource(
            self,
            resource_manager,
            resource_id: ResourceId,
            should_print: bool,
            **update_params):
        self.printer.log_modify(resource_manager.resource_type, resource_id)
        try:
            resource = resource_manager.modify(resource_id, **update_params)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        self.printer.log_modified(resource_manager.resource_type, resource_id)
        self.printer.print_resource(resource, should_print)
        return resource
