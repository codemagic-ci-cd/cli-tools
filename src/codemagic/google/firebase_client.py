from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from .google_client import GoogleClient
from .resource_managers.release_manager import ReleaseManager

if TYPE_CHECKING:
    from googleapiclient._apis.firebaseappdistribution.v1.resources import FirebaseAppDistributionResource  # noqa: F401


class FirebaseClient(GoogleClient["FirebaseAppDistributionResource"]):
    google_service_name: ClassVar[str] = "firebaseappdistribution"

    @property
    def releases(self) -> ReleaseManager:
        return ReleaseManager(self.google_resource)
