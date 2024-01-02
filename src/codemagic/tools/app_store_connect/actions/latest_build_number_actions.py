from __future__ import annotations

import dataclasses
import operator
from abc import ABC
from typing import List
from typing import Optional
from typing import cast

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import BuildVersionInfo
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ResourceId
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


@dataclasses.dataclass(frozen=True)
class _ResourceVersion:
    id: str  # App Store Version, Build or Prerelease Version ID
    version: str  # Version number


@dataclasses.dataclass
class _LatestBuildInfo:
    build_id: str
    build_number: str
    version: str = dataclasses.field(init=False)
    source: str = dataclasses.field(init=False)

    pre_release_version: dataclasses.InitVar[Optional[str]] = None
    app_store_version: dataclasses.InitVar[Optional[str]] = None

    def __post_init__(self, pre_release_version: Optional[str] = None, app_store_version: Optional[str] = None):
        if not operator.xor(bool(app_store_version), bool(pre_release_version)):
            raise ValueError("Either pre_release_version or app_store_version is required")
        self.source = "App Store" if app_store_version else "TestFlight"
        self.version = cast(str, pre_release_version or app_store_version)

    def get_build_version_info(self) -> BuildVersionInfo:
        return BuildVersionInfo(
            buildId=ResourceId(self.build_id),
            version=self.version,
            buildNumber=self.build_number,
        )

    def __str__(self):
        return f"build number {self.build_number} from {self.source} version {self.version}"


class AbstractGetLatestBuildNumberAction(AbstractBaseAction, ABC):
    def _log_latest_build_info(self, latest_build_info: _LatestBuildInfo, include_version: Optional[bool]):
        self.logger.info(Colors.GREEN(f"Found {latest_build_info}"))
        if include_version:
            self.logger.info(Colors.BLUE("-- Build Version Info --"))
            self.printer.print_value(latest_build_info.get_build_version_info(), True)
        else:
            self.printer.print_value(latest_build_info.build_number, True)

    def __get_ordered_pre_release_version_numbers(
        self,
        application_id: ResourceId,
        pre_release_version: Optional[str] = None,
        platform: Optional[Platform] = None,
    ) -> List[_ResourceVersion]:
        versions_filter = self.api_client.pre_release_versions.Filter(
            app=application_id,
            platform=platform,
            version=pre_release_version,
        )
        pre_release_versions_data = self.api_client.pre_release_versions.list_data(
            versions_filter,
            fields=("version",),
            page_size=200,
        )
        return sorted(
            (_ResourceVersion(prv["id"], prv["attributes"]["version"]) for prv in pre_release_versions_data),
            key=lambda rv: versions.sorting_key(rv.version),
            reverse=True,
        )

    def __get_ordered_app_store_version_numbers(
        self,
        application_id: ResourceId,
        version_string: Optional[str] = None,
        platform: Optional[Platform] = None,
    ) -> List[_ResourceVersion]:
        versions_filter = self.api_client.app_store_versions.Filter(
            platform=platform,
            version_string=version_string,
        )
        app_store_versions_data = self.api_client.apps.list_app_store_versions_data(
            application_id,
            resource_filter=versions_filter,
            fields=("versionString",),
            page_size=200,
        )
        return sorted(
            (_ResourceVersion(asv["id"], asv["attributes"]["versionString"]) for asv in app_store_versions_data),
            key=lambda rv: versions.sorting_key(rv.version),
            reverse=True,
        )

    def __get_pre_release_version_max_build(
        self,
        pre_release_version_id: str,
        build_expired_status: Optional[bool],
    ) -> Optional[_ResourceVersion]:
        builds_data = self.api_client.pre_release_versions.list_builds_data(
            ResourceId(pre_release_version_id),
            fields=("version",) if build_expired_status is None else ("version", "expired"),
            page_size=200,
        )
        build_versions = (
            _ResourceVersion(b["id"], b["attributes"]["version"])
            for b in builds_data
            if build_expired_status is None or b["attributes"]["expired"] is build_expired_status
        )
        return max(
            build_versions,
            key=lambda rv: versions.sorting_key(cast(_ResourceVersion, rv).version),
            default=None,
        )

    def __get_testflight_latest_build_info(
        self,
        pre_release_versions: List[_ResourceVersion],
        build_expired_status: Optional[bool],
    ) -> Optional[_LatestBuildInfo]:
        for pre_release_version in pre_release_versions:
            max_build = self.__get_pre_release_version_max_build(pre_release_version.id, build_expired_status)
            if not max_build:
                continue
            return _LatestBuildInfo(
                build_id=max_build.id,
                build_number=max_build.version,
                pre_release_version=pre_release_version.version,
            )
        return None

    def __get_app_store_latest_build_info(
        self,
        app_store_versions: List[_ResourceVersion],
    ) -> Optional[_LatestBuildInfo]:
        for app_store_version in app_store_versions:
            max_build_data = self.api_client.app_store_versions.read_build_data(
                ResourceId(app_store_version.id),
                fields=("version",),
            )
            if not max_build_data:
                continue
            return _LatestBuildInfo(
                build_id=ResourceId(max_build_data["id"]),
                build_number=max_build_data["attributes"]["version"],
                app_store_version=app_store_version.version,
            )
        return None

    def _get_testflight_latest_build_info(
        self,
        application_id: ResourceId,
        pre_release_version: Optional[str] = None,
        platform: Optional[Platform] = None,
        build_expired_status: Optional[bool] = None,
    ) -> Optional[_LatestBuildInfo]:
        try:
            pre_release_version_numbers = self.__get_ordered_pre_release_version_numbers(
                application_id,
                pre_release_version,
                platform,
            )
            return self.__get_testflight_latest_build_info(pre_release_version_numbers, build_expired_status)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

    def _get_app_store_latest_build_info(
        self,
        application_id: ResourceId,
        version_string: Optional[str] = None,
        platform: Optional[Platform] = None,
    ) -> Optional[_LatestBuildInfo]:
        try:
            app_store_version_numbers = self.__get_ordered_app_store_version_numbers(
                application_id,
                version_string,
                platform,
            )
            return self.__get_app_store_latest_build_info(app_store_version_numbers)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))


class GetLatestBuildNumberAction(AbstractGetLatestBuildNumberAction, ABC):
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
        app_store_build_info = self._get_app_store_latest_build_info(application_id, platform=platform)
        testflight_build_info = self._get_testflight_latest_build_info(application_id, platform=platform)

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


class GetLatestAppStoreBuildNumberAction(AbstractGetLatestBuildNumberAction, ABC):
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
        latest_build_info = self._get_app_store_latest_build_info(
            application_id,
            version_string=version_string,
            platform=platform,
        )
        if latest_build_info is None:
            self.logger.info(Colors.YELLOW(f"Did not find latest build for app {application_id}"))
            return None

        self._log_latest_build_info(latest_build_info, include_version)

        return latest_build_info.build_number


class GetLatestTestflightBuildNumberAction(AbstractGetLatestBuildNumberAction, ABC):
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

        latest_build_info = self._get_testflight_latest_build_info(
            application_id,
            pre_release_version=pre_release_version,
            platform=platform,
            build_expired_status=expired_value,
        )
        if latest_build_info is None:
            self.logger.info(Colors.YELLOW(f"Did not find latest build for app {application_id}"))
            return None

        self._log_latest_build_info(latest_build_info, include_version)

        return latest_build_info.build_number
