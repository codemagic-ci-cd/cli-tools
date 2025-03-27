from __future__ import annotations

import re
import shlex
import time
from abc import ABCMeta
from datetime import datetime
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import AppStoreVersionLocalization
from codemagic.apple.resources import Build
from codemagic.apple.resources import Locale
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ReleaseType
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ReviewSubmission
from codemagic.apple.resources import ReviewSubmissionItem
from codemagic.apple.resources.enums import AppStoreState
from codemagic.apple.resources.enums import ReviewSubmissionState
from codemagic.cli import Argument
from codemagic.cli import Colors
from codemagic.utilities import versions

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppStoreVersionArgument
from ..arguments import AppStoreVersionInfo
from ..arguments import AppStoreVersionLocalizationInfo
from ..arguments import ArgumentGroups
from ..arguments import BuildArgument
from ..arguments import Types
from ..errors import AppStoreConnectError

AppStoreVersionLocalizationInfos = Union[
    List[AppStoreVersionLocalizationInfo],
    Types.AppStoreVersionLocalizationInfoArgument,
]


class SubmitToAppStoreAction(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "submit-to-app-store",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        *ArgumentGroups.SUBMIT_TO_APP_STORE_OPTIONAL_ARGUMENTS,
        action_group=AppStoreConnectActionGroup.BUILDS,
    )
    def submit_to_app_store(
        self,
        build_id: ResourceId,
        max_build_processing_wait: Optional[Union[int, Types.MaxBuildProcessingWait]] = None,
        cancel_previous_submissions: bool = False,
        # App Store Version information arguments
        copyright: Optional[str] = None,
        earliest_release_date: Optional[Union[datetime, Types.EarliestReleaseDate]] = None,
        platform: Platform = AppStoreVersionArgument.PLATFORM.get_default(),
        release_type: Optional[ReleaseType] = None,
        version_string: Optional[str] = None,
        app_store_version_info: Optional[Union[AppStoreVersionInfo, Types.AppStoreVersionInfoArgument]] = None,
        # App Store Version Localization arguments
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        locale: Optional[Locale] = None,
        marketing_url: Optional[str] = None,
        promotional_text: Optional[str] = None,
        support_url: Optional[str] = None,
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
        app_store_version_localizations: Optional[AppStoreVersionLocalizationInfos] = None,
        # App Store Version Phased Release arguments
        enable_phased_release: Optional[bool] = None,
        disable_phased_release: Optional[bool] = None,
    ) -> Tuple[ReviewSubmission, ReviewSubmissionItem]:
        """
        Submit build to App Store review
        """
        try:
            phased_release: Optional[bool] = Argument.resolve_optional_two_way_switch(
                enable_phased_release,
                disable_phased_release,
            )
        except ValueError:
            enable_argument = AppStoreVersionArgument.ENABLE_PHASED_RELEASE
            disable_argument = AppStoreVersionArgument.DISABLE_PHASED_RELEASE
            raise AppStoreVersionArgument.ENABLE_PHASED_RELEASE.raise_argument_error(
                f'Using mutually exclusive switches "{enable_argument.flag}" and "{disable_argument.flag}".',
            )

        app_store_version_info = self._get_app_store_version_info(
            app_store_version_info,
            copyright,
            earliest_release_date,
            platform,
            release_type,
            version_string,
        )
        app_store_version_localization_infos = self._get_app_store_version_localization_infos(
            app_store_version_localizations,
            description,
            keywords,
            locale,
            marketing_url,
            promotional_text,
            support_url,
            whats_new,
        )

        return self._submit_to_app_store(
            build_id=build_id,
            max_processing_minutes=Types.MaxBuildProcessingWait.resolve_value(max_build_processing_wait),
            app_store_version_info=app_store_version_info,
            app_store_version_localization_infos=app_store_version_localization_infos,
            cancel_previous_submissions=cancel_previous_submissions,
            phased_release=phased_release,
        )

    def _cancel_previous_submissions(
        self,
        application_id: ResourceId,
        platform: Platform,
    ):
        self.logger.info(Colors.BLUE("\nCancel previous submissions before creating new submission"))
        states_to_cancel = (
            ReviewSubmissionState.WAITING_FOR_REVIEW,
            ReviewSubmissionState.IN_REVIEW,
            ReviewSubmissionState.UNRESOLVED_ISSUES,
        )

        cancelled_submissions = self.cancel_review_submissions(
            application_id=application_id,
            review_submission_state=states_to_cancel,
            platform=platform,
            should_print=False,
        )

        if cancelled_submissions:
            self._wait_for_cancelled_review_submissions_to_complete(application_id, platform)

    def _wait_for_cancelled_review_submissions_to_complete(
        self,
        application_id: ResourceId,
        platform: Platform,
        timeout=120,
    ):
        self.logger.info(Colors.BLUE("Wait until cancelled submissions are completed"))

        review_submissions_filter = self.api_client.review_submissions.Filter(
            app=application_id,
            platform=platform,
            state=ReviewSubmissionState.CANCELING,
        )

        waited_duration = 0
        while timeout > waited_duration:
            cancelling_submissions = self.api_client.review_submissions.list(review_submissions_filter)
            if not cancelling_submissions:
                self.logger.info(Colors.GREEN("Previous submissions are successfully cancelled"))
                return
            time.sleep(1)
            waited_duration += 1

        warning_message = f"Cancelling submissions was not completed in {timeout} seconds. Try to continue..."
        self.logger.warning(Colors.YELLOW(warning_message))

    def _submit_to_app_store(
        self,
        build_id: ResourceId,
        max_processing_minutes: int,
        app_store_version_info: AppStoreVersionInfo,
        app_store_version_localization_infos: List[AppStoreVersionLocalizationInfo],
        cancel_previous_submissions: bool,
        phased_release: Optional[bool],
    ) -> Tuple[ReviewSubmission, ReviewSubmissionItem]:
        self.logger.info(Colors.BLUE(f"\nSubmit build {build_id!r} to App Store review"))

        try:
            build, app = self.api_client.builds.read_with_include(build_id, App)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error)) from api_error

        if cancel_previous_submissions:
            self._cancel_previous_submissions(application_id=app.id, platform=app_store_version_info.platform)

        if max_processing_minutes:
            build = self.wait_until_build_is_processed(build, max_processing_minutes)

        if app_store_version_info.version_string is None:
            self.logger.info("\nVersion string is not specified. Obtain it from build's pre-release version...")
            pre_release_version = self.get_build_pre_release_version(build_id, should_print=False)
            app_store_version_info.version_string = pre_release_version.attributes.version

        self.logger.info(
            Colors.BLUE(f"\nUsing version {app_store_version_info.version_string} for App Store submission"),
        )

        app_store_version = self._ensure_app_store_version(app, build, app_store_version_info)

        self._manage_app_store_version_phased_release(app_store_version, phased_release)

        self._create_or_update_app_store_version_localizations(
            app,
            app_store_version,
            app_store_version_localization_infos,
        )

        review_submission = self._create_review_submission(app, app_store_version_info.platform)
        review_submission_item = self.create_review_submission_item(
            review_submission_id=review_submission.id,
            app_store_version_id=app_store_version.id,
        )

        self.echo(Colors.BLUE("\nSubmit to App Review\n"))
        self.confirm_review_submission(review_submission.id)

        submission_url = (
            f"https://appstoreconnect.apple.com/apps/{app.id}/appstore/reviewsubmissions/details/{review_submission.id}"
        )
        self.logger.info(f"\nCheck App Store review submission details from\n{submission_url}\n")

        return review_submission, review_submission_item

    def _create_review_submission(self, app: App, platform: Platform) -> ReviewSubmission:
        self.printer.log_creating(ReviewSubmission, platform=platform, app=app.id)
        try:
            review_submission = self.api_client.review_submissions.create(platform, app)
        except AppStoreConnectApiError as api_error:
            existing_submission_error_patt = re.compile(
                r"There is another reviewSubmissions with id ([\w-]+) still in progress",
            )

            existing_submission_matches: Iterator[Optional[re.Match]] = (
                existing_submission_error_patt.search(error.detail)
                for error in api_error.error_response.errors
                if error.detail is not None
            )

            try:
                existing_submission_match: re.Match = next(m for m in existing_submission_matches if m)
            except StopIteration:
                raise AppStoreConnectError(str(api_error)) from api_error

            self.logger.warning("Review submission already exists, reuse it")
            existing_review_submission_id = ResourceId(existing_submission_match.group(1))
            review_submission = self.api_client.review_submissions.read(existing_review_submission_id)

        self.printer.print_resource(review_submission, True)
        if review_submission.created:
            self.printer.log_created(review_submission)
        self.echo("")

        return review_submission

    def _ensure_app_store_version(
        self,
        app: App,
        build: Build,
        app_store_version_info: AppStoreVersionInfo,
    ) -> AppStoreVersion:
        app_store_version = self._get_editable_app_store_version(app, app_store_version_info.platform)
        if app_store_version is None:
            # Version does not exist, create a new version for App Store review submission
            self.logger.info(f"\n{AppStoreVersion} does not exist for build {build.id}")
            app_store_version = self.create_app_store_version(
                build.id,
                platform=app_store_version_info.platform,
                copyright=app_store_version_info.copyright,
                earliest_release_date=app_store_version_info.earliest_release_date,
                release_type=app_store_version_info.release_type,
                version_string=app_store_version_info.version_string,
            )
        else:
            self._update_existing_app_store_version(app_store_version, build, app_store_version_info)
        return app_store_version

    def _create_or_update_app_store_version_localizations(
        self,
        app: App,
        app_store_version: AppStoreVersion,
        app_store_version_localizations: List[AppStoreVersionLocalizationInfo],
    ):
        is_first_app_store_version = self._is_first_app_store_version(app, app_store_version.attributes.platform)
        existing_localizations = self._get_existing_app_store_version_localizations(app_store_version)
        for localization in app_store_version_localizations:
            if is_first_app_store_version:  # Release notes are not allowed for first releases
                localization.whats_new = None
            localization_id = existing_localizations.get(localization.locale or app.attributes.primaryLocale)

            try:
                self._create_or_update_app_store_version_localization(
                    localization_id,
                    app,
                    app_store_version,
                    localization,
                )
            except AppStoreConnectApiError as error:
                verb = "update" if localization_id else "create new"
                message = f"Failed to {verb} {AppStoreVersionLocalization} for locale {localization.locale}:"
                self.echo(f"{Colors.YELLOW(message)}\n{error}\n")

    def _create_or_update_app_store_version_localization(
        self,
        existing_localization_id: Optional[ResourceId],
        app: App,
        app_store_version: AppStoreVersion,
        localization: AppStoreVersionLocalizationInfo,
    ):
        if localization.locale:
            locale_description = f"locale {localization.locale}"
        else:
            locale_description = f"default locale ({app.attributes.primaryLocale})"

        if existing_localization_id is None:
            self.echo(Colors.GREEN(f"Create new {AppStoreVersionLocalization} for {locale_description}"))
            app_store_version_localization = self.api_client.app_store_version_localizations.create(
                app_store_version,
                localization.locale or app.attributes.primaryLocale,  # Use app's primary locale if not defined
                description=localization.description,
                keywords=localization.keywords,
                marketing_url=localization.marketing_url,
                promotional_text=localization.promotional_text,
                support_url=localization.support_url,
                whats_new=localization.whats_new,
            )
        else:
            self.echo(Colors.GREEN(f"Update {AppStoreVersionLocalization} for {locale_description}"))
            app_store_version_localization = self.api_client.app_store_version_localizations.modify(
                existing_localization_id,
                description=localization.description,
                keywords=localization.keywords,
                marketing_url=localization.marketing_url,
                promotional_text=localization.promotional_text,
                support_url=localization.support_url,
                whats_new=localization.whats_new,
            )
        self.printer.print_resource(app_store_version_localization, True)
        self.echo("")

    def _update_existing_app_store_version(
        self,
        app_store_version: AppStoreVersion,
        build: Build,
        app_store_version_info: AppStoreVersionInfo,
    ):
        self.logger.info(
            (
                f"\nFound existing {AppStoreVersion} {app_store_version.id} "
                f'in state "{app_store_version.attributes.appStoreState}". '
            ),
        )

        updates: Dict[str, str] = {"build": build.id}
        if app_store_version_info.copyright:
            updates["copyright"] = app_store_version_info.copyright
        if app_store_version_info.earliest_release_date:
            updates["earliest release date"] = AppStoreVersion.to_iso_8601(app_store_version_info.earliest_release_date)
        if app_store_version_info.release_type:
            updates["release type"] = app_store_version_info.release_type.value.lower()
        if app_store_version_info.version_string:
            updates["version string"] = app_store_version_info.version_string

        update_message = ", ".join(f"{param}: {shlex.quote(value)}" for param, value in updates.items())
        self.logger.info(f"Use it for current submission by updating it with {update_message}.")

        return self.update_app_store_version(
            app_store_version.id,
            build_id=build.id,
            copyright=app_store_version_info.copyright,
            earliest_release_date=app_store_version_info.earliest_release_date,
            release_type=app_store_version_info.release_type,
            version_string=app_store_version_info.version_string,
        )

    def _is_first_app_store_version(self, app: App, platform: Platform) -> bool:
        versions_filter = self.api_client.app_store_versions.Filter(platform=platform)
        app_store_versions = self.api_client.apps.list_app_store_versions(
            app,
            resource_filter=versions_filter,
            limit=2,
        )
        return len(app_store_versions) < 2

    def _get_existing_app_store_version_localizations(
        self,
        app_store_version: AppStoreVersion,
    ) -> Dict[Locale, ResourceId]:
        localizations = self.api_client.app_store_versions.list_app_store_version_localizations(app_store_version)
        return {localization.attributes.locale: localization.id for localization in localizations}

    def _get_editable_app_store_version(self, app: App, platform: Platform) -> Optional[AppStoreVersion]:
        def sorting_key(app_store_version: Optional[AppStoreVersion]) -> versions.Version:
            assert app_store_version is not None  # Make mypy happy
            return versions.sorting_key(app_store_version.attributes.versionString)

        versions_filter = self.api_client.app_store_versions.Filter(
            app_store_state=AppStoreState.editable_states(),
            platform=platform,
        )
        app_store_versions = self.api_client.apps.list_app_store_versions(app, resource_filter=versions_filter)
        return max(app_store_versions, default=None, key=sorting_key)

    @classmethod
    def _get_app_store_version_info(
        cls,
        app_store_version_info_argument: Optional[Union[AppStoreVersionInfo, Types.AppStoreVersionInfoArgument]],
        copyright: Optional[str],
        earliest_release_date: Optional[Union[datetime, Types.EarliestReleaseDate]],
        platform: Platform,
        release_type: Optional[ReleaseType],
        version_string: Optional[str],
    ) -> AppStoreVersionInfo:
        if app_store_version_info_argument is None:
            app_store_version_info = AppStoreVersionInfo(platform=platform)
        elif isinstance(app_store_version_info_argument, Types.AppStoreVersionInfoArgument):
            app_store_version_info = app_store_version_info_argument.value
        else:
            app_store_version_info = app_store_version_info_argument

        if platform is not AppStoreVersionArgument.PLATFORM.get_default():
            # Platform has a default value when invoked from CLI,
            # override it only in case non-default value was provided
            app_store_version_info.platform = platform
        if copyright:
            app_store_version_info.copyright = copyright
        if earliest_release_date:
            if isinstance(earliest_release_date, Types.EarliestReleaseDate):
                app_store_version_info.earliest_release_date = earliest_release_date.value
            else:
                app_store_version_info.earliest_release_date = earliest_release_date
        if release_type:
            app_store_version_info.release_type = release_type
        if version_string:
            app_store_version_info.version_string = version_string
        return app_store_version_info

    @classmethod
    def _get_app_store_version_localization_infos(
        cls,
        app_store_version_localizations: Optional[AppStoreVersionLocalizationInfos],
        description: Optional[str],
        keywords: Optional[str],
        locale: Optional[Locale],
        marketing_url: Optional[str],
        promotional_text: Optional[str],
        support_url: Optional[str],
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
    ) -> List[AppStoreVersionLocalizationInfo]:
        if isinstance(app_store_version_localizations, Types.AppStoreVersionLocalizationInfoArgument):
            app_store_version_localization_infos = app_store_version_localizations.value
        else:
            app_store_version_localization_infos = app_store_version_localizations or []

        app_store_version_localization_info = AppStoreVersionLocalizationInfo(
            description=description,
            keywords=keywords,
            locale=locale,
            marketing_url=marketing_url,
            promotional_text=promotional_text,
            support_url=support_url,
            whats_new=whats_new.value if isinstance(whats_new, Types.WhatsNewArgument) else whats_new,
        )
        if set(app_store_version_localization_info.__dict__.values()) != {None}:
            # At least some field is defined
            app_store_version_localization_infos.append(app_store_version_localization_info)

        return app_store_version_localization_infos

    def _manage_app_store_version_phased_release(
        self,
        app_store_version: AppStoreVersion,
        should_enable_phased_release: Optional[bool],
    ):
        if should_enable_phased_release is True:
            self._enable_app_store_version_phased_release(app_store_version)
        elif should_enable_phased_release is False:
            self._disable_app_store_version_phased_release(app_store_version)
        else:
            pass  # Leave it as is without changing anything
        self.echo("")

    def _enable_app_store_version_phased_release(self, app_store_version: AppStoreVersion):
        self.echo(Colors.BLUE(f"\nEnable phased release for App Store Version {app_store_version.id}"))
        phased_release = self.api_client.app_store_versions.read_app_store_version_phased_release(app_store_version)
        if phased_release:
            self.echo(Colors.GREEN(f"Phased release is already enabled for App Store Version {app_store_version.id}"))
        else:
            phased_release = self.enable_app_store_version_phased_release(app_store_version, should_print=False)
        self.printer.print_resource(phased_release, should_print=True)

    def _disable_app_store_version_phased_release(self, app_store_version: AppStoreVersion):
        self.echo(Colors.BLUE(f"\nDisable phased release for App Store Version {app_store_version.id}"))
        phased_release = self.api_client.app_store_versions.read_app_store_version_phased_release(app_store_version)
        if not phased_release:
            self.echo(Colors.GREEN(f"Phased release is already disabled for App Store Version {app_store_version.id}"))
        else:
            self.cancel_app_store_version_phased_release(phased_release)
