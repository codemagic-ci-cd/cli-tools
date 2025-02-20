from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING
from typing import ClassVar

from .google_client import GoogleClient
from .services.firebase import ReleasesService

if TYPE_CHECKING:
    from googleapiclient._apis.firebaseappdistribution.v1.resources import FirebaseAppDistributionResource  # noqa: F401


class FirebaseClient(GoogleClient["FirebaseAppDistributionResource"]):
    google_service_name: ClassVar[str] = "firebaseappdistribution"
    google_service_version: ClassVar[str] = "v1"

    @cached_property
    def releases(self) -> ReleasesService:
        return ReleasesService(self.google_resource)
