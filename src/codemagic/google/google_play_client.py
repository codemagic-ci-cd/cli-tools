from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING
from typing import ClassVar

from .google_client import GoogleClient
from .services.google_play import ApksService
from .services.google_play import BundlesService
from .services.google_play import DeobfuscationFilesService
from .services.google_play import EditsService
from .services.google_play import TracksService
from .services.google_play.expansion_files_service import ExpansionFilesService

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3.resources import AndroidPublisherResource  # noqa: F401


class GooglePlayClient(GoogleClient["AndroidPublisherResource"]):
    google_service_name: ClassVar[str] = "androidpublisher"
    google_service_version: ClassVar[str] = "v3"

    @cached_property
    def tracks(self) -> TracksService:
        return TracksService(self.google_resource)

    @cached_property
    def edits(self) -> EditsService:
        return EditsService(self.google_resource)

    @cached_property
    def apks(self) -> ApksService:
        return ApksService(self.google_resource)

    @cached_property
    def bundles(self) -> BundlesService:
        return BundlesService(self.google_resource)

    @cached_property
    def deobfuscation_files(self) -> DeobfuscationFilesService:
        return DeobfuscationFilesService(self.google_resource)

    @cached_property
    def expansion_files(self) -> ExpansionFilesService:
        return ExpansionFilesService(self.google_resource)
