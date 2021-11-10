from __future__ import annotations

from abc import ABCMeta
from datetime import datetime
from typing import Optional
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ReleaseType
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppArgument
from ..arguments import AppStoreVersionArgument
from ..arguments import BuildArgument
from ..arguments import CommonArgument
from ..errors import AppStoreConnectError


class AppStoreVersionsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    def _get_build(self, build: Union[ResourceId, Build]) -> Build:
        if isinstance(build, Build):
            return build
        try:
            return self.api_client.builds.read(build)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

    def _get_app_id(self, build: Build, app: Optional[Union[ResourceId, App]]) -> ResourceId:
        if isinstance(app, ResourceId):
            return app
        elif isinstance(app, App):
            return app.id
        try:
            return self.api_client.builds.read_app(build).id
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

    @cli.action(
        'create',
        AppStoreVersionArgument.COPYRIGHT,
        AppStoreVersionArgument.VERSION_STRING,
        AppArgument.APPLICATION_ID_RESOURCE_ID_OPTIONAL,
        BuildArgument.BUILD_ID_RESOURCE_ID,
        AppStoreVersionArgument.EARLIEST_RELEASE_DATE,
        CommonArgument.PLATFORM,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSIONS,
    )
    def create_app_store_version(
            self,
            build_id: Union[ResourceId, Build],
            application_id: Optional[Union[ResourceId, App]] = None,
            platform: Platform = CommonArgument.PLATFORM.get_default(),
            copyright: Optional[str] = None,
            version_string: Optional[str] = None,
            release_type: Optional[ReleaseType] = None,
            earliest_release_date: Optional[datetime] = None,
            should_print: bool = True,
    ) -> AppStoreVersion:
        """
        Add a new App Store version to an app.
        """
        build = self._get_build(build_id)
        app_id = self._get_app_id(build, application_id)

        create_params = dict(
            app=app_id,
            build=build,
            copyright=copyright,
            earliest_release_date=earliest_release_date,
            platform=platform,
            release_type=release_type,
            version=version_string if version_string is not None else build.attributes.version,
        )
        return self._create_resource(
            self.api_client.app_store_versions,
            should_print,
            **{k: v for k, v in create_params.items() if v is not None},
        )
