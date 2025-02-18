from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar
from typing import List
from typing import Type
from typing import cast

from codemagic.google.resource_managers.resource_manager import ResourceManager
from codemagic.google.resources.google_play_resources import Track

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3 import TrackHttpRequest
    from googleapiclient._apis.androidpublisher.v3.resources import AndroidPublisherResource
    from googleapiclient._apis.androidpublisher.v3.resources import Track as GooglePlayTrack
    from googleapiclient._apis.androidpublisher.v3.resources import TracksListResponse
    from googleapiclient._apis.androidpublisher.v3.resources import TracksListResponseHttpRequest


class GooglePlayTracksManager(ResourceManager[Track, "AndroidPublisherResource"]):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks
    """

    resource_type: ClassVar[Type[Track]] = Track

    @property
    def _tracks(self) -> AndroidPublisherResource.EditsResource.TracksResource:
        return self._google_service.edits().tracks()

    def get(self, package_name: str, track_name: str, edit_id: str) -> Track:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks/get
        """
        self._logger.debug("Get track %r for %r using edit %s", track_name, package_name, edit_id)
        get_request: TrackHttpRequest = self._tracks.get(
            packageName=package_name,
            editId=edit_id,
            track=track_name,
        )
        response = cast(
            "GooglePlayTrack",
            self._execute_request(get_request, "get"),
        )
        self._logger.debug("Got track %r for %r", track_name, package_name)
        return Track(**cast(dict, response))

    def list(self, package_name: str, edit_id: str) -> List[Track]:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks/list
        """
        self._logger.debug("List tracks for %r using edit %s", package_name, edit_id)
        get_request: TracksListResponseHttpRequest = self._tracks.list(
            packageName=package_name,
            editId=edit_id,
        )
        response = cast(
            "TracksListResponse",
            self._execute_request(get_request, "list"),
        )
        self._logger.debug("Listed %d tracks list for %r", len(response), package_name)
        return [Track(**cast(dict, track)) for track in response["tracks"]]

    def update(self, track: Track, package_name: str, edit_id: str) -> Track:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks/update
        """
        self._logger.debug("Update track %r for %r using edit %s", track.track, package_name, edit_id)
        update_request: TrackHttpRequest = self._tracks.update(
            packageName=package_name,
            editId=edit_id,
            track=track.track,
            body=cast("GooglePlayTrack", track.dict()),
        )
        response = cast(
            "GooglePlayTrack",
            self._execute_request(update_request, "update"),
        )
        self._logger.debug("Updated track %r for %r", track.track, package_name)
        return Track(**cast(dict, response))
