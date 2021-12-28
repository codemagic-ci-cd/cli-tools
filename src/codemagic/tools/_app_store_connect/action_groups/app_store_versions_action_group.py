from __future__ import annotations

from abc import ABCMeta
from datetime import datetime
from typing import List
from typing import Optional
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import AppStoreVersionLocalization
from codemagic.apple.resources import Build
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ReleaseType
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppStoreVersionArgument
from ..arguments import BuildArgument
from ..arguments import CommonArgument
from ..arguments import Types
from ..errors import AppStoreConnectError


class AppStoreVersionsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action(
        'create',
        AppStoreVersionArgument.COPYRIGHT,
        AppStoreVersionArgument.VERSION_STRING,
        BuildArgument.BUILD_ID_RESOURCE_ID,
        AppStoreVersionArgument.EARLIEST_RELEASE_DATE,
        AppStoreVersionArgument.RELEASE_TYPE,
        CommonArgument.PLATFORM,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSIONS,
    )
    def create_app_store_version(
        self,
        build_id: ResourceId,
        platform: Platform = CommonArgument.PLATFORM.get_default(),
        copyright: Optional[str] = None,
        version_string: Optional[str] = None,
        release_type: Optional[ReleaseType] = None,
        earliest_release_date: Optional[Union[datetime, Types.EarliestReleaseDate]] = None,
        should_print: bool = True,
    ) -> AppStoreVersion:
        """
        Add a new App Store version to an app using specified build.
        """
        if isinstance(earliest_release_date, Types.EarliestReleaseDate):
            earliest_release_date = earliest_release_date.value

        try:
            build, app = self.api_client.builds.read_with_include(build_id, App)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        create_params = dict(
            app=app.id,
            build=build.id,
            copyright=copyright,
            earliest_release_date=earliest_release_date,
            platform=platform,
            release_type=release_type,
            version=self._get_build_version(version_string, build),
        )
        return self._create_resource(
            self.api_client.app_store_versions,
            should_print,
            **{k: v for k, v in create_params.items() if v is not None},
        )

    @cli.action(
        'modify',
        AppStoreVersionArgument.APP_STORE_VERSION_ID,
        BuildArgument.BUILD_ID_RESOURCE_ID_OPTIONAL,
        AppStoreVersionArgument.COPYRIGHT,
        AppStoreVersionArgument.EARLIEST_RELEASE_DATE,
        AppStoreVersionArgument.RELEASE_TYPE,
        AppStoreVersionArgument.VERSION_STRING,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSIONS,
    )
    def update_app_store_version(
        self,
        app_store_version_id: ResourceId,
        build_id: Optional[ResourceId] = None,
        copyright: Optional[str] = None,
        earliest_release_date: Optional[Union[datetime, Types.EarliestReleaseDate]] = None,
        release_type: Optional[ReleaseType] = None,
        version_string: Optional[str] = None,
        should_print: bool = True,
    ) -> AppStoreVersion:
        """
        Update the app store version for a specific app.
        """
        if isinstance(earliest_release_date, Types.EarliestReleaseDate):
            earliest_release_date = earliest_release_date.value
        return self._modify_resource(
            self.api_client.app_store_versions,
            app_store_version_id,
            should_print,
            build=build_id,
            copyright=copyright,
            earliest_release_date=earliest_release_date,
            release_type=release_type,
            version=version_string,
        )

    @cli.action(
        'delete',
        AppStoreVersionArgument.APP_STORE_VERSION_ID,
        CommonArgument.IGNORE_NOT_FOUND,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSIONS,
    )
    def delete_app_store_version(
        self,
        app_store_version_id: ResourceId,
        ignore_not_found: bool = False,
    ) -> None:
        """
        Delete specified App Store version from Apple Developer portal
        """
        self._delete_resource(
            self.api_client.app_store_versions,
            app_store_version_id,
            ignore_not_found,
        )

    def _get_build_version(self, version_string: Optional[str], build: Build) -> str:
        if version_string:
            return version_string
        try:
            pre_release_version = self.api_client.builds.read_pre_release_version(build)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                f'Build version is not specified and checking it from prerelease version failed: {api_error}')

        if not pre_release_version:
            raise AppStoreConnectError(
                'Build version is not specified and build does not have prerelease version to check the version from')

        return pre_release_version.attributes.version

    @cli.action(
        'localizations',
        AppStoreVersionArgument.APP_STORE_VERSION_ID,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSIONS,
    )
    def list_app_store_version_localizations(
        self,
        app_store_version_id: ResourceId,
        should_print: bool = True,
    ) -> List[AppStoreVersionLocalization]:
        """
        List All App Store Version Localizations for an App Store Version.
        Get a list of localized, version-level information about an app, for all locales.
        """
        return self._list_related_resources(
            app_store_version_id,
            AppStoreVersion,
            AppStoreVersionLocalization,
            self.api_client.app_store_versions.list_app_store_version_localizations,
            None,
            should_print,
        )
