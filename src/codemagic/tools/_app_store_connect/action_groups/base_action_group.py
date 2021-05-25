import logging
import pathlib
from abc import ABCMeta
from typing import Generator
from typing import List
from typing import Optional

from codemagic.apple import AppStoreConnectApiClient
from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import Build
from codemagic.apple.resources import Platform
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ResourceId

from ..resource_printer import ResourcePrinter


class BaseActionGroup(metaclass=ABCMeta):
    logger: logging.Logger
    profiles_directory: pathlib.Path
    certificates_directory: pathlib.Path
    printer: ResourcePrinter
    _key_identifier: KeyIdentifier
    _issuer_id: IssuerId
    _private_key: str
    api_client: AppStoreConnectApiClient

    def find_paths(self, *patterns: pathlib.Path) -> Generator[pathlib.Path, None, None]:
        ...

    def create_beta_app_review_submission(
            self, build_id: ResourceId, should_print: bool = True) -> AppStoreVersionSubmission:
        ...

    def get_build_pre_release_version(self, build_id: ResourceId, should_print: bool = True) -> PreReleaseVersion:
        ...

    def list_app_builds(self, application_id: ResourceId, should_print: bool = True) -> List[Build]:
        ...

    def list_apps(self,
                  bundle_id_identifier: Optional[str] = None,
                  application_id: Optional[ResourceId] = None,
                  application_name: Optional[str] = None,
                  application_sku: Optional[str] = None,
                  version_string: Optional[str] = None,
                  platform: Optional[Platform] = None,
                  app_store_state: Optional[AppStoreState] = None,
                  should_print: bool = True) -> List[App]:
        ...
