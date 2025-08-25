from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar
from typing import List
from typing import Optional
from typing import Type
from typing import cast

from codemagic.google.resources.firebase import OrderBy
from codemagic.google.resources.firebase import Release
from codemagic.google.services.resource_service import ResourceService

if TYPE_CHECKING:
    from googleapiclient._apis.firebaseappdistribution.v1 import GoogleFirebaseAppdistroV1ListReleasesResponse
    from googleapiclient._apis.firebaseappdistribution.v1 import (
        GoogleFirebaseAppdistroV1ListReleasesResponseHttpRequest,
    )
    from googleapiclient._apis.firebaseappdistribution.v1 import GoogleFirebaseAppdistroV1Release
    from googleapiclient._apis.firebaseappdistribution.v1.resources import FirebaseAppDistributionResource


class ReleasesService(ResourceService[Release, "FirebaseAppDistributionResource"]):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases
    """

    resource_type: ClassVar[Type[Release]] = Release

    @property
    def _releases(self) -> FirebaseAppDistributionResource.ProjectsResource.AppsResource.ReleasesResource:
        return self._google_service.projects().apps().releases()

    def list(
        self,
        project_number: str,
        app_id: str,
        order_by: OrderBy = OrderBy.CREATE_TIME_DESC,
        limit: Optional[int] = None,
        page_size: int = 25,
    ) -> List[Release]:
        """
        https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases/list
        """

        self._logger.debug("List Firebase releases for project %r app %r", project_number, app_id)

        firebase_releases: List[GoogleFirebaseAppdistroV1Release] = []
        next_page_token = ""
        while True:
            list_request: GoogleFirebaseAppdistroV1ListReleasesResponseHttpRequest = self._releases.list(
                orderBy=order_by.value,
                parent=f"projects/{project_number}/apps/{app_id}",
                pageSize=min(limit, page_size) if limit else page_size,
                pageToken=next_page_token,
            )
            response = cast(
                "GoogleFirebaseAppdistroV1ListReleasesResponse",
                self._execute_request(list_request, "list"),
            )
            # In case no matches are found, then the relevant key is missing from response
            firebase_releases.extend(response.get("releases", []))
            if not response.get("nextPageToken"):
                break
            elif limit and len(firebase_releases) > limit:
                break
            next_page_token = response["nextPageToken"]

        self._logger.debug("Listed %d Firebase releases for app %r", len(firebase_releases[:limit]), app_id)
        return [Release.from_api_response(firebase_release) for firebase_release in firebase_releases[:limit]]
