from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Type

from codemagic.google.resource_managers.mixins import ListingManagerMixin
from codemagic.google.resource_managers.resource_manager import ResourceManager
from codemagic.google.resources.firebase_resources import AppIdentifier
from codemagic.google.resources.firebase_resources import Release

if TYPE_CHECKING:
    from googleapiclient._apis.firebaseappdistribution.v1.resources import FirebaseAppDistributionResource
    from googleapiclient._apis.firebaseappdistribution.v1.resources import (
        GoogleFirebaseAppdistroV1ListReleasesResponseHttpRequest,
    )


class FirebaseReleasesManager(
    ResourceManager[Release, "FirebaseAppDistributionResource"],
    ListingManagerMixin[Release, AppIdentifier],
):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases/list
    """

    resource_type: ClassVar[Type[Release]] = Release

    @property
    def _releases(self) -> FirebaseAppDistributionResource.ProjectsResource.AppsResource.ReleasesResource:
        return self._google_resource.projects().apps().releases()

    def _get_resources_page_request(
        self,
        arguments: ListingManagerMixin.PageRequestArguments,
    ) -> GoogleFirebaseAppdistroV1ListReleasesResponseHttpRequest:
        """
        https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases/list
        """
        return self._releases.list(**arguments.as_request_kwargs())
