from __future__ import annotations

import time
from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union
from typing import cast

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildBetaDetail
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import ExternalBetaState
from codemagic.apple.resources import InternalBetaState
from codemagic.apple.resources import Locale
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources.enums import BetaReviewState
from codemagic.apple.resources.enums import Platform
from codemagic.cli import Argument
from codemagic.cli import Colors

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppArgument
from ..arguments import ArgumentGroups
from ..arguments import BetaBuildInfo
from ..arguments import BuildArgument
from ..arguments import PublishArgument
from ..arguments import Types
from ..errors import AppStoreConnectError

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import ListingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ModifyingResourceManager


BetaBuildLocalizationsInfo = Union[
    List[BetaBuildInfo],
    Types.BetaBuildLocalizations,
]


class BuildsActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "get",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        action_group=AppStoreConnectActionGroup.BUILDS,
    )
    def get_build(self, build_id: ResourceId, should_print: bool = True) -> Build:
        """
        Get information about a specific build
        """

        return self._get_resource(build_id, self.api_client.builds, should_print)

    @cli.action(
        "list",
        AppArgument.APPLICATION_ID_RESOURCE_ID_OPTIONAL,
        *ArgumentGroups.LIST_BUILDS_FILTERING_ARGUMENTS,
        action_group=AppStoreConnectActionGroup.BUILDS,
        deprecation_info=cli.ActionDeprecationInfo("list-builds", "0.49.0"),
    )
    def list_builds(
        self,
        application_id: Optional[ResourceId] = None,
        expired: Optional[bool] = None,
        not_expired: Optional[bool] = None,
        build_id: Optional[ResourceId] = None,
        pre_release_version: Optional[str] = None,
        processing_state: Optional[BuildProcessingState] = None,
        beta_review_state: Optional[Union[BetaReviewState, Sequence[BetaReviewState]]] = None,
        build_version_number: Optional[int] = None,
        platform: Optional[Platform] = None,
        should_print: bool = True,
    ) -> List[Build]:
        """
        List Builds from Apple Developer Portal matching given constraints
        """
        try:
            expired_value = Argument.resolve_optional_two_way_switch(expired, not_expired)
        except ValueError:
            flags = f"{BuildArgument.EXPIRED.flag!r} and {BuildArgument.NOT_EXPIRED.flag!r}"
            raise BuildArgument.NOT_EXPIRED.raise_argument_error(f"Using mutually exclusive switches {flags}.")

        builds_filter = self.api_client.builds.Filter(
            app=application_id,
            expired=expired_value,
            id=build_id,
            processing_state=processing_state,
            beta_app_review_submission_beta_review_state=beta_review_state,
            version=build_version_number,
            pre_release_version_version=pre_release_version,
            pre_release_version_platform=platform,
        )
        return self._list_resources(
            builds_filter,
            cast("ListingResourceManager[Build]", self.api_client.builds),
            should_print,
        )

    @cli.action(
        "expire",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        action_group=AppStoreConnectActionGroup.BUILDS,
    )
    def expire_build(
        self,
        build_id: ResourceId,
        should_print: bool = True,
    ) -> Build:
        """
        Expire a specific build, an expired build becomes unavailable for testing
        """

        return self._modify_resource(
            cast("ModifyingResourceManager[Build]", self.api_client.builds),
            build_id,
            should_print,
            expired=True,
        )

    @cli.action(
        "pre-release-version",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        action_group=AppStoreConnectActionGroup.BUILDS,
    )
    def get_build_pre_release_version(
        self,
        build_id: ResourceId,
        should_print: bool = True,
    ) -> PreReleaseVersion:
        """
        Get the prerelease version for a specific build
        """

        return self._get_related_resource(
            build_id,
            Build,
            PreReleaseVersion,
            self.api_client.builds.read_pre_release_version,
            should_print,
        )

    @cli.action(
        "app-store-version",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        action_group=AppStoreConnectActionGroup.BUILDS,
    )
    def get_build_app_store_version(
        self,
        build_id: ResourceId,
        should_print: bool = True,
    ) -> AppStoreVersion:
        """
        Get the App Store version of a specific build.
        """

        return self._get_related_resource(
            build_id,
            Build,
            AppStoreVersion,
            self.api_client.builds.read_app_store_version,
            should_print,
        )

    @cli.action(
        "app",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        action_group=AppStoreConnectActionGroup.BUILDS,
    )
    def get_build_app(
        self,
        build_id: ResourceId,
        should_print: bool = True,
    ) -> App:
        """
        Get the App details for a specific build.
        """

        return self._get_related_resource(
            build_id,
            Build,
            App,
            self.api_client.builds.read_app,
            should_print,
        )

    @cli.action(
        "beta-details",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        action_group=AppStoreConnectActionGroup.BUILDS,
    )
    def get_build_beta_detail(self, build_id: ResourceId, should_print: bool = True) -> BuildBetaDetail:
        """
        Get Build Beta Details Information of a specific build.
        """
        return self._get_related_resource(
            build_id,
            Build,
            BuildBetaDetail,
            self.api_client.builds.read_beta_detail,
            should_print,
        )

    @cli.action(
        "add-beta-test-info",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        *ArgumentGroups.ADD_BETA_TEST_INFO_OPTIONAL_ARGUMENTS,
        action_group=AppStoreConnectActionGroup.BUILDS,
    )
    def add_beta_test_info(
        self,
        build_id: ResourceId,
        beta_build_localizations: Optional[BetaBuildLocalizationsInfo] = None,
        locale: Optional[Locale] = None,
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
    ):
        """
        Add localized What's new (what to test) information
        """

        if isinstance(beta_build_localizations, Types.BetaBuildLocalizations):
            beta_test_info_items = beta_build_localizations.value
        else:
            beta_test_info_items = beta_build_localizations or []

        if whats_new:
            whats_new = whats_new.value if isinstance(whats_new, Types.WhatsNewArgument) else whats_new
            beta_test_info_items.append(BetaBuildInfo(whats_new=whats_new, locale=locale))

        self.logger.info(Colors.BLUE("\nUpdate beta build localization info in TestFlight for uploaded build"))
        for item in beta_test_info_items:
            self.create_beta_build_localization(build_id=build_id, locale=item.locale, whats_new=item.whats_new)

    def _wait_until_build_is_processed(
        self,
        build: Build,
        processing_started_at: float,
        max_processing_minutes: int,
        retry_wait_seconds: int,
    ) -> Build:
        is_first_attempt = True
        while time.time() - processing_started_at < max_processing_minutes * 60:
            if build.attributes.processingState is BuildProcessingState.PROCESSING:
                if is_first_attempt:
                    self._log_build_processing_message(build.id, max_processing_minutes)

                msg_template = (
                    "Build %s is still being processed on App Store Connect side, waiting %d seconds "
                    "and checking again"
                )
                self.logger.info(msg_template, build.id, retry_wait_seconds)
                time.sleep(retry_wait_seconds)
                try:
                    build = self.api_client.builds.read(build)
                except AppStoreConnectApiError as api_error:
                    raise AppStoreConnectError(str(api_error))
            elif build.attributes.processingState in (BuildProcessingState.FAILED, BuildProcessingState.INVALID):
                raise IOError(f"Uploaded build {build.id} is {build.attributes.processingState.value.lower()}")
            else:
                self.logger.info(Colors.GREEN("Processing build %s is completed"), build.id)
                return build
            is_first_attempt = False

        raise IOError(
            (
                f"Waiting for build {build.id} processing timed out in {max_processing_minutes} minutes. "
                f"You can configure maximum timeout using {PublishArgument.MAX_BUILD_PROCESSING_WAIT.flag} "
                f"command line option, or {Types.MaxBuildProcessingWait.environment_variable_key} environment variable."
            ),
        )

    def _wait_until_build_beta_detail_is_processed(
        self,
        build: Build,
        processing_started_at: float,
        max_processing_minutes: int,
        retry_wait_seconds: int,
    ) -> BuildBetaDetail:
        is_first_attempt = True
        build_beta_detail = None
        while time.time() - processing_started_at < max_processing_minutes * 60:
            try:
                build_beta_detail = self.api_client.builds.read_beta_detail(build)
            except AppStoreConnectApiError as api_error:
                raise AppStoreConnectError(str(api_error))

            if (
                build_beta_detail.attributes.externalBuildState is not ExternalBetaState.PROCESSING
                or build_beta_detail.attributes.internalBuildState is not InternalBetaState.PROCESSING
            ):
                self.logger.info(
                    Colors.GREEN("Processing build %s beta detail %s is completed"),
                    build.id,
                    build_beta_detail.id,
                )
                return build_beta_detail

            if is_first_attempt:
                self._log_build_beta_detail_processing_message(build.id, max_processing_minutes)

            msg_template = (
                "Build %s beta details %s are still being processed on App Store Connect side, "
                "waiting %d seconds and checking again"
            )
            self.logger.info(msg_template, build.id, build_beta_detail.id, retry_wait_seconds)
            time.sleep(retry_wait_seconds)
            is_first_attempt = False

        build_beta_detail_id = build_beta_detail.id if build_beta_detail else "N/A"
        raise IOError(
            (
                f"Waiting for build {build.id} beta detail {build_beta_detail_id} processing "
                f"timed out in {max_processing_minutes} minutes. "
                f"You can configure maximum timeout using {PublishArgument.MAX_BUILD_PROCESSING_WAIT.flag} "
                f"command line option, or {Types.MaxBuildProcessingWait.environment_variable_key} environment variable."
            ),
        )

    def wait_until_build_is_processed(
        self,
        build: Build,
        max_processing_minutes: int,
        retry_wait_seconds: int = 30,
    ) -> Build:
        """
        Wait until
        1. build's processing state becomes 'processed', and
        2. beta details of the build report that both external and internal build
           state are not processing anymore.
        Returns updated build instance that is already processed.
        """
        self.logger.info(Colors.BLUE(f"\nWait until build {build.id} and its beta details are processed"))

        processing_started_at = time.time()

        build = self._wait_until_build_is_processed(
            build,
            processing_started_at,
            max_processing_minutes,
            retry_wait_seconds,
        )
        build_beta_detail = self._wait_until_build_beta_detail_is_processed(
            build,
            processing_started_at,
            max_processing_minutes,
            retry_wait_seconds,
        )

        self.logger.info(Colors.GREEN("\nProcessed build and beta details are"))
        self.printer.print_resource(build, True)
        self.printer.print_resource(build_beta_detail, True)

        return build

    def _log_build_processing_message(self, build_id: ResourceId, max_processing_minutes: int):
        processing_message_template = (
            "Processing of builds by Apple can take a while, "
            "the timeout for waiting the processing "
            "to finish for build %s is set to %d minutes."
        )
        self.logger.info(Colors.BLUE(processing_message_template), build_id, max_processing_minutes)

    def _log_build_beta_detail_processing_message(self, build_beta_detail_id: ResourceId, max_processing_minutes: int):
        processing_message_template = (
            "Processing build beta detail information by Apple can take some time after "
            "the build is already processed. Timeout for waiting the processing "
            "to finish for build beta detail %s is set to %d minutes."
        )
        self.logger.info(Colors.BLUE(processing_message_template), build_beta_detail_id, max_processing_minutes)
