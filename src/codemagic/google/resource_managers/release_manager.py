from __future__ import annotations

from typing import TYPE_CHECKING

from codemagic.google.resources.identifiers import AppIdentifier

from ..resources import Release
from .mixins import ListingManagerMixin
from .resource_manager import ResourceManager

if TYPE_CHECKING:
    from googleapiclient._apis.firebaseappdistribution.v1.resources import FirebaseAppDistributionResource
    from googleapiclient._apis.firebaseappdistribution.v1.resources import \
        GoogleFirebaseAppdistroV1ListReleasesResponseHttpRequest


class ReleaseManager(ResourceManager[Release], ListingManagerMixin[Release, AppIdentifier]):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases/list
    """

    resource_type = Release

    @property
    def _releases(
        self,
    ) -> FirebaseAppDistributionResource.ProjectsResource.AppsResource.ReleasesResource:
        return self._firebase_app_distribution.projects().apps().releases()

    def _get_resources_page_request(
        self,
        arguments: ListingManagerMixin.PageRequestArguments,
    ) -> GoogleFirebaseAppdistroV1ListReleasesResponseHttpRequest:
        """
        https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases/list
        """
        return self._releases.list(**arguments.as_request_kwargs())
