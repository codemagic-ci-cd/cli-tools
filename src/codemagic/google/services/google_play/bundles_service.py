from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING
from typing import Final
from typing import List
from typing import cast

from codemagic.google.resources.google_play import Bundle
from codemagic.google.services.resource_service import ResourceService

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3 import resources as android_publisher_resources


class BundlesService(ResourceService[Bundle, "android_publisher_resources.AndroidPublisherResource"]):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.bundles
    """

    resource_type: Final = Bundle

    @property
    def _bundles(self) -> android_publisher_resources.AndroidPublisherResource.EditsResource.BundlesResource:
        return self._google_service.edits().bundles()

    def list(self, package_name: str, edit_id: str) -> List[Bundle]:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.bundles/list
        """
        self._logger.debug("List App Bundles for %r using edit %s", package_name, edit_id)
        list_request: android_publisher_resources.BundlesListResponseHttpRequest = self._bundles.list(
            packageName=package_name,
            editId=edit_id,
        )
        response = cast(
            "android_publisher_resources.BundlesListResponse",
            self._execute_request(list_request, "list"),
        )
        self._logger.debug("Listed %d App Bundles list for %r", len(response), package_name)
        return [Bundle(**bundle) for bundle in response.get("bundles", [])]

    def upload(self, package_name: str, edit_id: str, bundle_path: pathlib.Path) -> Bundle:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.bundles/upload
        """
        self._logger.debug("Upload App Bundle for %r using edit %s", package_name, edit_id)
        upload_request: android_publisher_resources.BundleHttpRequest = self._bundles.upload(
            packageName=package_name,
            editId=edit_id,
            media_body=str(bundle_path),
            media_mime_type="application/octet-stream",
        )
        response = cast(
            "android_publisher_resources.Bundle",
            self._execute_request(upload_request, "upload"),
        )
        self._logger.debug("Uploaded App Bundle for %r", package_name)
        return Bundle(**response)
