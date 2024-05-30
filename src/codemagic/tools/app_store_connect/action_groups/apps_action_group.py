from __future__ import annotations

from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Union
from typing import cast

from codemagic import cli
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import Platform
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ReviewSubmission
from codemagic.apple.resources import ReviewSubmissionState
from codemagic.apple.resources.enums import BetaReviewState

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppArgument
from ..arguments import AppStoreVersionArgument
from ..arguments import ArgumentGroups
from ..arguments import BuildArgument
from ..arguments import BundleIdArgument
from ..arguments import CommonArgument
from ..arguments import ReviewSubmissionArgument

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import ListingResourceManager


class AppsActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action("get", AppArgument.APPLICATION_ID_RESOURCE_ID, action_group=AppStoreConnectActionGroup.APPS)
    def get_app(self, application_id: ResourceId, should_print: bool = True) -> App:
        """
        Get information about a specific app
        """

        return self._get_resource(application_id, self.api_client.apps, should_print)

    @cli.action(
        "list",
        BundleIdArgument.BUNDLE_ID_IDENTIFIER_OPTIONAL,
        BundleIdArgument.IDENTIFIER_STRICT_MATCH,
        AppArgument.APPLICATION_ID_RESOURCE_ID_OPTIONAL,
        AppArgument.APPLICATION_NAME,
        AppArgument.APPLICATION_SKU,
        AppStoreVersionArgument.VERSION_STRING,
        AppStoreVersionArgument.PLATFORM_OPTIONAL,
        AppStoreVersionArgument.APP_STORE_STATE,
        action_group=AppStoreConnectActionGroup.APPS,
    )
    def list_apps(
        self,
        bundle_id_identifier: Optional[str] = None,
        bundle_id_identifier_strict_match: bool = False,
        application_id: Optional[ResourceId] = None,
        application_name: Optional[str] = None,
        application_sku: Optional[str] = None,
        version_string: Optional[str] = None,
        platform: Optional[Platform] = None,
        app_store_state: Optional[AppStoreState] = None,
        should_print: bool = True,
    ) -> List[App]:
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
            cast("ListingResourceManager[App]", self.api_client.apps),
            should_print,
            filter_predicate=predicate if bundle_id_identifier and bundle_id_identifier_strict_match else None,
        )

    @cli.action(
        "builds",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        *ArgumentGroups.LIST_BUILDS_FILTERING_ARGUMENTS,
        action_group=AppStoreConnectActionGroup.APPS,
    )
    def list_app_builds(self, application_id: ResourceId, should_print: bool = True, **builds_filters) -> List[Build]:
        """
        Get a list of builds associated with a specific app matching given constrains
        """
        return self.list_builds(application_id=application_id, **builds_filters, should_print=should_print)

    @cli.action(
        "pre-release-versions",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        action_group=AppStoreConnectActionGroup.APPS,
    )
    def list_app_pre_release_versions(
        self,
        application_id: ResourceId,
        should_print: bool = True,
    ) -> List[PreReleaseVersion]:
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

    @cli.action(
        "app-store-versions",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        AppStoreVersionArgument.APP_STORE_VERSION_ID_OPTIONAL,
        AppStoreVersionArgument.VERSION_STRING,
        AppStoreVersionArgument.PLATFORM_OPTIONAL,
        AppStoreVersionArgument.APP_STORE_STATE,
        action_group=AppStoreConnectActionGroup.APPS,
    )
    def list_app_store_versions_for_app(
        self,
        application_id: ResourceId,
        app_store_version_id: Optional[ResourceId] = None,
        version_string: Optional[str] = None,
        platform: Optional[Platform] = None,
        app_store_state: Optional[AppStoreState] = None,
        should_print: bool = True,
    ) -> List[AppStoreVersion]:
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

    @cli.action(
        "expire-builds",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        BuildArgument.BUILD_ID_RESOURCE_ID_EXCLUDE_OPTIONAL,
        action_group=AppStoreConnectActionGroup.APPS,
    )
    def expire_app_builds(
        self,
        application_id: ResourceId,
        excluded_build_id: Optional[Union[ResourceId, Sequence[ResourceId]]] = None,
        should_print: bool = False,
    ) -> List[Build]:
        """
        Expire all application builds except the given build(s)
        """
        builds_to_skip: Set[ResourceId] = set()

        if isinstance(excluded_build_id, ResourceId):
            builds_to_skip.add(excluded_build_id)
        elif excluded_build_id is not None:
            builds_to_skip.update(excluded_build_id)

        builds = self.list_builds(application_id=application_id, not_expired=True, should_print=should_print)
        return [
            self.expire_build(
                build_id=build.id,
            )
            for build in builds
            if build.id not in builds_to_skip
        ]

    @cli.action(
        "expire-build-submitted-for-review",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        CommonArgument.PLATFORM,
        action_group=AppStoreConnectActionGroup.APPS,
    )
    def expire_build_submitted_for_review(
        self,
        application_id: ResourceId,
        platform: Optional[Platform] = None,
        should_print: bool = False,
    ) -> Optional[Build]:
        """
        Expire application build that is currently waiting for review, or is currently in review in TestFlight
        """

        states_to_cancel = (
            BetaReviewState.WAITING_FOR_REVIEW,
            BetaReviewState.IN_REVIEW,
        )

        builds = self.list_builds(
            application_id=application_id,
            not_expired=True,
            beta_review_state=states_to_cancel,
            platform=platform,
            should_print=should_print,
        )
        try:
            return self.expire_build(builds[0].id)
        except IndexError:
            return None

    @cli.action(
        "cancel-review-submissions",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        AppStoreVersionArgument.PLATFORM_OPTIONAL,
        ReviewSubmissionArgument.REVIEW_SUBMISSION_STATE,
        action_group=AppStoreConnectActionGroup.APPS,
    )
    def cancel_review_submissions(
        self,
        application_id: ResourceId,
        platform: Optional[Platform] = None,
        review_submission_state: Optional[Union[ReviewSubmissionState, Sequence[ReviewSubmissionState]]] = None,
        should_print: bool = False,
    ) -> List[ReviewSubmission]:
        """
        Find and cancel review submissions in App Store Connect for the given application
        """

        review_submissions = self.list_review_submissions(
            application_id,
            platform,
            review_submission_state,
            should_print,
        )

        return [self.cancel_review_submission(submission.id) for submission in review_submissions]

    @cli.action(
        "list-review-submissions",
        AppArgument.APPLICATION_ID_RESOURCE_ID,
        AppStoreVersionArgument.PLATFORM_OPTIONAL,
        ReviewSubmissionArgument.REVIEW_SUBMISSION_STATE,
        action_group=AppStoreConnectActionGroup.APPS,
    )
    def list_review_submissions(
        self,
        application_id: ResourceId,
        platform: Optional[Platform] = None,
        review_submission_state: Optional[Union[ReviewSubmissionState, Sequence[ReviewSubmissionState]]] = None,
        should_print: bool = True,
    ) -> List[ReviewSubmission]:
        """
        Find and list review submissions in App Store Connect for the given application
        """

        review_submissions_filter = self.api_client.review_submissions.Filter(
            app=application_id,
            platform=platform,
            state=review_submission_state,
        )

        return self._list_resources(
            review_submissions_filter,
            cast("ListingResourceManager[ReviewSubmission]", self.api_client.review_submissions),
            should_print,
        )
