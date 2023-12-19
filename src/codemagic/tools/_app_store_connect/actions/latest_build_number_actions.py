from __future__ import annotations

import dataclasses
import operator
from abc import ABCMeta
from typing import List
from typing import Optional
from typing import cast

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import BuildVersionInfo
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceVersion
from codemagic.cli import Argument
from codemagic.cli import Colors
from codemagic.utilities import versions

from ..abstract_base_action import AbstractBaseAction
from ..arguments import AppArgument
from ..arguments import AppStoreVersionArgument
from ..arguments import BuildArgument
from ..arguments import BuildNumberArgument
from ..arguments import CommonArgument
from ..errors import AppStoreConnectError


@dataclasses.dataclass
class _LatestBuildInfo:
    build_id: ResourceId
    build_number: str
    version: str = dataclasses.field(init=False)
    is_app_store_version: bool = dataclasses.field(init=False)
    is_pre_release_version: bool = dataclasses.field(init=False)

    pre_release_version: dataclasses.InitVar[Optional[str]] = None
    app_store_version: dataclasses.InitVar[Optional[str]] = None

    def __post_init__(
        self,
        pre_release_version: Optional[str] = None,
        app_store_version: Optional[str] = None,
    ):
        self.is_pre_release_version = bool(pre_release_version)
        self.is_app_store_version = bool(app_store_version)
        if not operator.xor(self.is_pre_release_version, self.is_app_store_version):
            raise ValueError("Either pre_release_version or app_store_version is required")
        self.version = cast(str, pre_release_version or app_store_version)


class AbstractGetLatestBuildNumberAction(AbstractBaseAction, metaclass=ABCMeta):
    def _get_max_testflight_version_and_build(
        self,
        application_id: ResourceId,
        pre_release_version: Optional[str] = None,
        platform: Optional[Platform] = None,
        is_build_expired: Optional[bool] = None,
    ) -> Optional[_LatestBuildInfo]:
        versions_filter = self.api_client.pre_release_versions.Filter(
            app=application_id,
            platform=platform,
            version=pre_release_version,
        )
        try:
            pre_release_version_numbers = self.api_client.pre_release_versions.list_version_numbers(
                resource_filter=versions_filter,
            )
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        pre_release_version_numbers.sort(
            key=lambda prv: versions.sorting_key(prv.version),
            reverse=True,
        )
        try:
            for pre_release_version_number in pre_release_version_numbers:
                version_builds: List[ResourceVersion] = self.api_client.pre_release_versions.list_build_version_numbers(
                    pre_release_version_number.id,
                    expired=is_build_expired,
                )
                max_build = max(
                    version_builds,
                    key=lambda b: versions.sorting_key(b.version),
                    default=None,
                )
                if max_build is not None:
                    return _LatestBuildInfo(
                        build_id=max_build.id,
                        build_number=max_build.version,
                        pre_release_version=pre_release_version_number.version,
                    )
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        return None

    def _get_max_app_store_version_and_build(
        self,
        application_id: ResourceId,
        version_string: Optional[str] = None,
        platform: Optional[Platform] = None,
    ) -> Optional[_LatestBuildInfo]:
        versions_filter = self.api_client.app_store_versions.Filter(
            platform=platform,
            version_string=version_string,
        )
        try:
            app_store_version_numbers = self.api_client.apps.list_app_store_version_numbers(
                application_id,
                resource_filter=versions_filter,
            )
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        app_store_version_numbers.sort(
            key=lambda asv: versions.sorting_key(asv.version),
            reverse=True,
        )
        try:
            for app_store_version in app_store_version_numbers:
                build = self.api_client.app_store_versions.read_build_version_number(app_store_version.id)
                if not build:
                    continue
                return _LatestBuildInfo(
                    build_id=build.id,
                    build_number=build.version,
                    app_store_version=app_store_version.version,
                )
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        return None

    def _log_latest_build_info(self, latest_build_info: _LatestBuildInfo, include_version: Optional[bool] = False):
        if latest_build_info.is_app_store_version:
            version_info = f"App Store version {latest_build_info.version}"
        else:
            version_info = f"TestFlight version {latest_build_info.version}"

        self.logger.info(Colors.GREEN(f"Found build number {latest_build_info.build_number} from {version_info}"))
        if include_version:
            build_version_info = BuildVersionInfo(
                buildId=latest_build_info.build_id,
                version=latest_build_info.version,
                buildNumber=latest_build_info.build_number,
            )
            self.logger.info(Colors.BLUE("-- Build Version Info --"))
            self.printer.print_value(build_version_info, True)
        else:
            self.printer.print_value(latest_build_info.build_number, True)


class GetLatestBuildNumberAction(AbstractGetLatestBuildNumberAction, metaclass=ABCMeta):
    @cli.action(
        "get-latest-build-number",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        CommonArgument.PLATFORM,
        BuildNumberArgument.INCLUDE_VERSION,
    )
    def get_latest_build_number(
        self,
        application_id: ResourceId,
        platform: Optional[Platform] = None,
        include_version: Optional[bool] = None,
    ) -> Optional[str]:
        """
        Get the highest build number of the highest version used for the given app.
        """
        app_store_build_info = self._get_max_app_store_version_and_build(application_id, platform=platform)
        testflight_build_info = self._get_max_testflight_version_and_build(application_id, platform=platform)

        latest_build_info: _LatestBuildInfo
        if app_store_build_info is not None and testflight_build_info is not None:
            asv = versions.parse_version(app_store_build_info.version)
            tfv = versions.parse_version(testflight_build_info.version)
            latest_build_info = app_store_build_info if asv > tfv else testflight_build_info
        elif app_store_build_info is not None:
            latest_build_info = app_store_build_info
        elif testflight_build_info is not None:
            latest_build_info = testflight_build_info
        else:
            self.logger.info(Colors.YELLOW(f"Did not find any builds for app {application_id}"))
            return None

        self._log_latest_build_info(latest_build_info, include_version)

        return latest_build_info.build_number


class GetLatestAppStoreBuildNumberAction(AbstractGetLatestBuildNumberAction, metaclass=ABCMeta):
    @cli.action(
        "get-latest-app-store-build-number",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        AppStoreVersionArgument.VERSION_STRING,
        CommonArgument.PLATFORM,
        BuildNumberArgument.INCLUDE_VERSION,
    )
    def get_latest_app_store_build_number(
        self,
        application_id: ResourceId,
        version_string: Optional[str] = None,
        platform: Optional[Platform] = None,
        include_version: Optional[bool] = None,
    ) -> Optional[str]:
        """
        Get the latest App Store build number of the highest version for the given application
        """
        latest_build_info = self._get_max_app_store_version_and_build(
            application_id,
            version_string=version_string,
            platform=platform,
        )
        if latest_build_info is None:
            self.logger.info(Colors.YELLOW(f"Did not find latest build for app {application_id}"))
            return None

        self._log_latest_build_info(latest_build_info, include_version)

        return latest_build_info.build_number


class GetLatestTestflightBuildNumberAction(AbstractGetLatestBuildNumberAction, metaclass=ABCMeta):
    @cli.action(
        "get-latest-testflight-build-number",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        BuildArgument.PRE_RELEASE_VERSION,
        CommonArgument.PLATFORM,
        BuildArgument.EXPIRED,
        BuildArgument.NOT_EXPIRED,
        BuildNumberArgument.INCLUDE_VERSION,
    )
    def get_latest_testflight_build_number(
        self,
        application_id: ResourceId,
        pre_release_version: Optional[str] = None,
        platform: Optional[Platform] = None,
        expired: Optional[bool] = None,
        not_expired: Optional[bool] = None,
        include_version: Optional[bool] = None,
    ) -> Optional[str]:
        """
        Get the latest Testflight build number of the highest version for the given application
        """
        try:
            expired_value: Optional[bool] = Argument.resolve_optional_two_way_switch(expired, not_expired)
        except ValueError:
            flags = f"{BuildArgument.EXPIRED.flag!r} and {BuildArgument.NOT_EXPIRED.flag!r}"
            raise BuildArgument.NOT_EXPIRED.raise_argument_error(f"Using mutually exclusive switches {flags}.")

        latest_build_info = self._get_max_testflight_version_and_build(
            application_id,
            pre_release_version=pre_release_version,
            platform=platform,
            is_build_expired=expired_value,
        )
        if latest_build_info is None:
            self.logger.info(Colors.YELLOW(f"Did not find latest build for app {application_id}"))
            return None

        self._log_latest_build_info(latest_build_info, include_version)

        return latest_build_info.build_number
