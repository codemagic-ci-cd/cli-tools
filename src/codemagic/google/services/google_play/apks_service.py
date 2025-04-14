from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING
from typing import Final
from typing import List
from typing import cast

from codemagic.google.resources.google_play import Apk
from codemagic.google.services.resource_service import ResourceService

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3 import resources as android_publisher_resources


class ApksService(ResourceService[Apk, "android_publisher_resources.AndroidPublisherResource"]):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.apks
    """

    resource_type: Final = Apk

    @property
    def _apks(self) -> android_publisher_resources.AndroidPublisherResource.EditsResource.ApksResource:
        return self._google_service.edits().apks()

    def list(self, package_name: str, edit_id: str) -> List[Apk]:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.apks/list
        """
        self._logger.debug("List APKS for %r using edit %s", package_name, edit_id)
        list_request: android_publisher_resources.ApksListResponseHttpRequest = self._apks.list(
            packageName=package_name,
            editId=edit_id,
        )
        response = cast(
            "android_publisher_resources.ApksListResponse",
            self._execute_request(list_request, "list"),
        )
        self._logger.debug("Listed %d apks list for %r", len(response), package_name)
        return [Apk(**cast(dict, apk)) for apk in response.get("apks", [])]

    def upload(self, package_name: str, edit_id: str, apk_path: pathlib.Path) -> Apk:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.apks/upload
        """
        self._logger.debug("Upload APK for %r using edit %s", package_name, edit_id)
        upload_request: android_publisher_resources.ApkHttpRequest = self._apks.upload(
            packageName=package_name,
            editId=edit_id,
            media_body=str(apk_path),
            media_mime_type="application/octet-stream",
        )
        response = cast(
            "android_publisher_resources.Apk",
            self._execute_request(upload_request, "upload"),
        )
        self._logger.debug("Uploaded apk for %r", package_name)
        return Apk(**cast(dict, response))
