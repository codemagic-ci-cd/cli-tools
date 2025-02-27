from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final
from typing import List
from typing import cast

from codemagic.google.resources.google_play import Track
from codemagic.google.services.resource_service import ResourceService

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3 import resources as android_publisher_resources


class TracksService(ResourceService[Track, "android_publisher_resources.AndroidPublisherResource"]):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks
    """

    resource_type: Final = Track

    @property
    def _tracks(self) -> android_publisher_resources.AndroidPublisherResource.EditsResource.TracksResource:
        return self._google_service.edits().tracks()

    def get(self, package_name: str, track_name: str, edit_id: str) -> Track:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks/get
        """
        self._logger.debug("Get track %r for %r using edit %s", track_name, package_name, edit_id)
        get_request: android_publisher_resources.TrackHttpRequest = self._tracks.get(
            packageName=package_name,
            editId=edit_id,
            track=track_name,
        )
        response = cast(
            "android_publisher_resources.Track",
            self._execute_request(get_request, "get"),
        )
        self._logger.debug("Got track %r for %r", track_name, package_name)
        return Track(**cast(dict, response))

    def list(self, package_name: str, edit_id: str) -> List[Track]:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks/list
        """
        self._logger.debug("List tracks for %r using edit %s", package_name, edit_id)
        get_request: android_publisher_resources.TracksListResponseHttpRequest = self._tracks.list(
            packageName=package_name,
            editId=edit_id,
        )
        response = cast(
            "android_publisher_resources.TracksListResponse",
            self._execute_request(get_request, "list"),
        )
        self._logger.debug("Listed %d tracks list for %r", len(response), package_name)
        return [Track(**cast(dict, track)) for track in response["tracks"]]

    def update(self, track: Track, package_name: str, edit_id: str) -> Track:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks/update
        """
        self._logger.debug("Update track %r for %r using edit %s", track.track, package_name, edit_id)
        update_request: android_publisher_resources.TrackHttpRequest = self._tracks.update(
            packageName=package_name,
            editId=edit_id,
            track=track.track,
            body=cast("android_publisher_resources.Track", track.dict()),
        )
        response = cast(
            "android_publisher_resources.Track",
            self._execute_request(update_request, "update"),
        )
        self._logger.debug("Updated track %r for %r", track.track, package_name)
        return Track(**cast(dict, response))
