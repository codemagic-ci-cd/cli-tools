from __future__ import annotations

import logging
import pathlib
from abc import ABCMeta
from abc import abstractmethod
from datetime import datetime
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from codemagic.apple import AppStoreConnectApiClient
from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import AppStoreVersionLocalization
from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import BetaAppReviewSubmission
from codemagic.apple.resources import BetaBuildLocalization
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import Locale
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ReleaseType
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ReviewSubmission
from codemagic.apple.resources import ReviewSubmissionItem
from codemagic.mixins import PathFinderMixin

from .arguments import AppStoreVersionInfo
from .arguments import AppStoreVersionLocalizationInfo
from .arguments import BetaBuildInfo
from .arguments import Types
from .resource_manager_mixin import ResourceManagerMixin
from .resource_printer import ResourcePrinter

AppStoreVersionLocalizationInfos = Union[
    List[AppStoreVersionLocalizationInfo],
    Types.AppStoreVersionLocalizationInfoArgument,
]


class AbstractBaseAction(ResourceManagerMixin, PathFinderMixin, metaclass=ABCMeta):
    logger: logging.Logger
    profiles_directory: pathlib.Path
    certificates_directory: pathlib.Path
    printer: ResourcePrinter
    _key_identifier: Optional[KeyIdentifier]
    _issuer_id: Optional[IssuerId]
    _private_key: Optional[str]

    # Define signatures for self-reference to other action groups

    @property
    @abstractmethod
    def api_client(self) -> AppStoreConnectApiClient:
        ...

    @classmethod
    def echo(cls, message: str, *args, **kwargs) -> None:
        ...

    def _assert_api_client_credentials(self, custom_error: Optional[str] = None):
        ...

    # Action signatures in alphabetical order

    @abstractmethod
    def add_beta_test_info(
        self,
        build_id: ResourceId,
        beta_build_localizations: Optional[Union[List[BetaBuildInfo], Types.BetaBuildLocalizations]] = None,
        locale: Optional[Locale] = None,
        whats_new: Optional[Types.WhatsNewArgument] = None,
    ):
        from .action_groups import BuildsActionGroup
        _ = BuildsActionGroup.add_beta_test_info  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def add_build_to_beta_groups(
        self,
        build_id: ResourceId,
        beta_group_names: Sequence[str],
    ):
        from .action_groups import BetaGroupsActionGroup
        _ = BetaGroupsActionGroup.add_build_to_beta_groups  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def confirm_review_submission(
        self,
        review_submission_id: ResourceId,
        should_print: bool = True,
    ) -> ReviewSubmission:
        from .action_groups import ReviewSubmissionsActionGroup
        _ = ReviewSubmissionsActionGroup.confirm_review_submission  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def create_app_store_version(
        self,
        build_id: ResourceId,
        platform: Platform = Platform.IOS,
        copyright: Optional[str] = None,
        version_string: Optional[str] = None,
        release_type: Optional[ReleaseType] = None,
        earliest_release_date: Optional[Union[datetime, Types.EarliestReleaseDate]] = None,
        should_print: bool = True,
    ) -> AppStoreVersion:
        from .action_groups import AppStoreVersionsActionGroup
        _ = AppStoreVersionsActionGroup.create_app_store_version  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def create_app_store_version_localization(
        self,
        app_store_version_id: ResourceId,
        locale: Locale,
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        marketing_url: Optional[str] = None,
        promotional_text: Optional[str] = None,
        support_url: Optional[str] = None,
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
        should_print: bool = True,
    ) -> AppStoreVersionLocalization:
        from .action_groups import AppStoreVersionLocalizationsActionGroup
        _ = AppStoreVersionLocalizationsActionGroup.create_app_store_version_localization  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def create_app_store_version_submission(
        self,
        app_store_version_id: ResourceId,
        should_print: bool = True,
    ) -> AppStoreVersionSubmission:
        from .action_groups import AppStoreVersionSubmissionsActionGroup
        _ = AppStoreVersionSubmissionsActionGroup.create_app_store_version_submission  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def create_beta_app_review_submission(
        self,
        build_id: ResourceId,
        should_print: bool = True,
    ) -> BetaAppReviewSubmission:
        from .action_groups import BetaAppReviewSubmissionsActionGroup
        _ = BetaAppReviewSubmissionsActionGroup.create_beta_app_review_submission  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def create_beta_build_localization(
        self,
        build_id: ResourceId,
        locale: Optional[Locale],
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
        should_print: bool = True,
    ) -> BetaBuildLocalization:
        from .action_groups import BetaBuildLocalizationsActionGroup
        _ = BetaBuildLocalizationsActionGroup.create_beta_build_localization  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def create_review_submission(
            self,
            application_id: ResourceId,
            platform: Platform,
            should_print: bool = True,
    ) -> ReviewSubmission:
        from .action_groups import ReviewSubmissionsActionGroup
        _ = ReviewSubmissionsActionGroup.create_review_submission  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def create_review_submission_item(
        self,
        review_submission_id: ResourceId,
        app_custom_product_page_version_id: Optional[ResourceId] = None,
        app_event_id: Optional[ResourceId] = None,
        app_store_version_id: Optional[ResourceId] = None,
        app_store_version_experiment_id: Optional[ResourceId] = None,
        should_print: bool = True,
    ) -> ReviewSubmissionItem:
        from .action_groups import ReviewSubmissionItemsActionGroup
        _ = ReviewSubmissionItemsActionGroup.create_review_submission_item  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def list_app_store_version_localizations(
        self,
        app_store_version_id: ResourceId,
        should_print: bool = True,
    ) -> List[AppStoreVersionLocalization]:
        from .action_groups import AppStoreVersionsActionGroup
        _ = AppStoreVersionsActionGroup.list_app_store_version_localizations  # Implementation
        raise NotImplementedError()

    @abstractmethod
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
        from .action_groups import AppsActionGroup
        _ = AppsActionGroup.list_apps  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def list_builds(
        self,
        application_id: Optional[ResourceId] = None,
        expired: Optional[bool] = None,
        not_expired: Optional[bool] = None,
        build_id: Optional[ResourceId] = None,
        pre_release_version: Optional[str] = None,
        processing_state: Optional[BuildProcessingState] = None,
        build_version_number: Optional[int] = None,
        should_print: bool = True,
    ) -> List[Build]:
        from ..app_store_connect import AppStoreConnect
        _ = AppStoreConnect.list_builds  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def submit_to_app_store(
        self,
        build_id: ResourceId,
        max_build_processing_wait: Optional[Union[int, Types.MaxBuildProcessingWait]] = None,
        # App Store Version information arguments
        copyright: Optional[str] = None,
        earliest_release_date: Optional[Union[datetime, Types.EarliestReleaseDate]] = None,
        platform: Platform = Platform.IOS,
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
    ) -> Tuple[ReviewSubmission, ReviewSubmissionItem]:
        from .action_groups import BuildsActionGroup
        _ = BuildsActionGroup.submit_to_app_store  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def submit_to_testflight(
        self,
        build_id: ResourceId,
        max_build_processing_wait: Optional[Union[int, Types.MaxBuildProcessingWait]] = None,
    ) -> BetaAppReviewSubmission:
        from .action_groups import BuildsActionGroup
        _ = BuildsActionGroup.submit_to_testflight  # Implementation
        raise NotImplementedError()

    @abstractmethod
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
        from .action_groups import AppStoreVersionsActionGroup
        _ = AppStoreVersionsActionGroup.update_app_store_version  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def update_app_store_version_localization(
        self,
        app_store_version_localization_id: ResourceId,
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        marketing_url: Optional[str] = None,
        promotional_text: Optional[str] = None,
        support_url: Optional[str] = None,
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
        should_print: bool = True,
    ) -> AppStoreVersionLocalization:
        from .action_groups import AppStoreVersionLocalizationsActionGroup
        _ = AppStoreVersionLocalizationsActionGroup.update_app_store_version_localization  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def wait_until_build_is_processed(
        self,
        build: Build,
        max_processing_minutes: int,
        retry_wait_seconds: int = 30,
    ) -> Build:
        from .action_groups import BuildsActionGroup
        _ = BuildsActionGroup.wait_until_build_is_processed  # Implementation
        raise NotImplementedError()
