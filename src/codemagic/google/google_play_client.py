from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING
from typing import ClassVar

from .google_client import GoogleClient
from .resource_managers import GooglePlayEditsManager
from .resource_managers import GooglePlayTracksManager

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3.resources import AndroidPublisherResource  # noqa: F401


class GooglePlayClient(GoogleClient["AndroidPublisherResource"]):
    google_service_name: ClassVar[str] = "androidpublisher"
    google_service_version: ClassVar[str] = "v3"

    @cached_property
    def tracks(self) -> GooglePlayTracksManager:
        return GooglePlayTracksManager(self.google_resource)

    @cached_property
    def edits(self) -> GooglePlayEditsManager:
        return GooglePlayEditsManager(self.google_resource)
