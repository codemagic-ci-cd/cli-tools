from __future__ import annotations

from abc import ABCMeta
from datetime import datetime
from typing import Optional

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ReleaseType
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppStoreVersionArgument
from ..arguments import BuildArgument
from ..arguments import CommonArgument
from ..errors import AppStoreConnectError


class AppStoreVersionsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action(
        'create',
        AppStoreVersionArgument.COPYRIGHT,
        AppStoreVersionArgument.VERSION_STRING,
        BuildArgument.BUILD_ID_RESOURCE_ID,
        AppStoreVersionArgument.EARLIEST_RELEASE_DATE,
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
            earliest_release_date: Optional[datetime] = None,
            should_print: bool = True,
    ) -> AppStoreVersion:
        """
        Add a new App Store version to an app.
        """
        try:
            build, app = self.api_client.builds.read_with_include(build_id, App)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        create_params = dict(
            app=app,
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
