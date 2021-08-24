from __future__ import annotations

import logging
import pathlib
from abc import ABCMeta
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

from codemagic.apple import AppStoreConnectApiClient
from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import BetaBuildLocalization
from codemagic.apple.resources import Locale
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ResourceId
from codemagic.mixins import PathFinderMixin

from .arguments import BetaBuildInfo
from .arguments import Types
from .resource_manager_mixin import ResourceManagerMixin
from .resource_printer import ResourcePrinter


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
    def api_client(self) -> AppStoreConnectApiClient:
        ...

    def _assert_api_client_credentials(self, custom_error: Optional[str]) -> str:
        ...

    def create_beta_app_review_submission(
            self, build_id: ResourceId, should_print: bool = True) -> AppStoreVersionSubmission:
        ...

    def create_beta_build_localization(
            self,
            build_id: ResourceId,
            locale: Optional[Locale],
            whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
            should_print: bool = True) -> BetaBuildLocalization:
        ...

    def add_build_to_beta_groups(self, build_id: ResourceId, beta_group_names: Sequence[str]):
        ...

    def add_beta_test_info(
            self,
            build_id: ResourceId,
            beta_build_localizations: Optional[Union[List[BetaBuildInfo], Types.BetaBuildLocalizations]] = None,
            locale: Optional[Locale] = None,
            whats_new: Optional[Types.WhatsNewArgument] = None):
        ...

    def submit_to_testflight(
            self,
            build_id: ResourceId,
            max_build_processing_wait: Optional[Union[int, Types.MaxBuildProcessingWait]] = None):
        ...

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
        ...
