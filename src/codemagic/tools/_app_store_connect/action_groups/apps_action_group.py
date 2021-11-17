from __future__ import annotations

from abc import ABCMeta
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import Platform
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppArgument
from ..arguments import AppStoreVersionArgument
from ..arguments import ArgumentGroups
from ..arguments import BundleIdArgument


class AppsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action('get', AppArgument.APPLICATION_ID_RESOURCE_ID, action_group=AppStoreConnectActionGroup.APPS)
    def get_app(self, application_id: ResourceId, should_print: bool = True) -> App:
        """
        Get information about a specific app
        """

        return self._get_resource(application_id, self.api_client.apps, should_print)

    @cli.action('list',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER_OPTIONAL,
                BundleIdArgument.IDENTIFIER_STRICT_MATCH,
                AppArgument.APPLICATION_ID_RESOURCE_ID_OPTIONAL,
                AppArgument.APPLICATION_NAME,
                AppArgument.APPLICATION_SKU,
                AppStoreVersionArgument.VERSION_STRING,
                AppStoreVersionArgument.PLATFORM_OPTIONAL,
                AppStoreVersionArgument.APP_STORE_STATE,
                action_group=AppStoreConnectActionGroup.APPS)
    def list_apps(self,
                  bundle_id_identifier: Optional[str] = None,
                  bundle_id_identifier_strict_match: bool = False,
                  application_id: Optional[ResourceId] = None,
                  application_name: Optional[str] = None,
                  application_sku: Optional[str] = None,
                  version_string: Optional[str] = None,
                  platform: Optional[Platform] = None,
                  app_store_state: Optional[AppStoreState] = None,
                  should_print: bool = True) -> List[App]:
        """
        Find and list apps added in App Store Connect
        """

        def predicate(app):
            return app.attributes.bundleId == bundle_id_identifier

        apps_filter = self.api_client.apps.Filter(
            bundle_id=bundle_id_identifier,
            id=application_id,
            name=application_name,
            sku=application_sku,
            app_store_versions=version_string,
            app_store_versions_platform=platform,
            app_store_versions_app_store_state=app_store_state,
        )

        return self._list_resources(
            apps_filter,
            self.api_client.apps,
            should_print,
            filter_predicate=predicate if bundle_id_identifier and bundle_id_identifier_strict_match else None,
        )

    @cli.action('builds',
                AppArgument.APPLICATION_ID_RESOURCE_ID,
                *ArgumentGroups.LIST_BUILDS_FILTERING_ARGUMENTS,
                action_group=AppStoreConnectActionGroup.APPS)
    def list_app_builds(self, application_id: ResourceId, should_print: bool = True, **builds_filters) -> List[Build]:
        """
        Get a list of builds associated with a specific app matching given constrains
        """
        return self.list_builds(application_id=application_id, **builds_filters, should_print=should_print)

    @cli.action('pre-release-versions',
                AppArgument.APPLICATION_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.APPS)
    def list_app_pre_release_versions(
            self, application_id: ResourceId, should_print: bool = True) -> List[PreReleaseVersion]:
        """
        Get a list of prerelease versions associated with a specific app
        """

        return self._list_related_resources(
            application_id,
            App,
            PreReleaseVersion,
            self.api_client.apps.list_pre_release_versions,
            None,
            should_print,
        )

    @cli.action('app-store-versions',
                AppArgument.APPLICATION_ID_RESOURCE_ID,
                AppStoreVersionArgument.APP_STORE_VERSION_ID_OPTIONAL,
                AppStoreVersionArgument.VERSION_STRING,
                AppStoreVersionArgument.PLATFORM_OPTIONAL,
                AppStoreVersionArgument.APP_STORE_STATE,
                action_group=AppStoreConnectActionGroup.APPS)
    def list_app_store_versions_for_app(
            self,
            application_id: ResourceId,
            app_store_version_id: Optional[ResourceId] = None,
            version_string: Optional[str] = None,
            platform: Optional[Platform] = None,
            app_store_state: Optional[AppStoreState] = None,
            should_print: bool = True) -> List[PreReleaseVersion]:
        """
        Get a list of App Store versions associated with a specific app
        """

        app_store_versions_filter = self.api_client.app_store_versions.Filter(
            id=app_store_version_id,
            version_string=version_string,
            platform=platform,
            app_store_state=app_store_state,
        )
        return self._list_related_resources(
            application_id,
            App,
            AppStoreVersion,
            self.api_client.apps.list_app_store_versions,
            app_store_versions_filter,
            should_print,
        )
