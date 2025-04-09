from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING
from typing import Final
from typing import cast

from codemagic.google.resources.google_play import InternalAppSharingArtifact
from codemagic.google.services.resource_service import ResourceService

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3 import resources as android_publisher_resources


class InternalAppSharingArtifactsService(
    ResourceService[InternalAppSharingArtifact, "android_publisher_resources.AndroidPublisherResource"],
):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/internalappsharingartifacts
    """

    resource_type: Final = InternalAppSharingArtifact

    @property
    def _internal_app_sharing_artifacts(
        self,
    ) -> android_publisher_resources.AndroidPublisherResource.InternalappsharingartifactsResource:
        return self._google_service.internalappsharingartifacts()

    def upload_apk(
        self,
        package_name: str,
        apk_path: pathlib.Path,
    ) -> InternalAppSharingArtifact:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/internalappsharingartifacts/uploadapk
        """

        self._logger.debug("Upload an APK for %r to internal app sharing", package_name)
        upload_request: android_publisher_resources.InternalAppSharingArtifactHttpRequest = (
            self._internal_app_sharing_artifacts.uploadapk(
                packageName=package_name,
                media_body=str(apk_path),
                media_mime_type="application/octet-stream",
            )
        )
        response = cast(
            "android_publisher_resources.InternalAppSharingArtifact",
            self._execute_request(upload_request, "upload"),
        )
        self._logger.debug("Uploaded APK to internal app sharing for %r", package_name)
        return InternalAppSharingArtifact(**response)

    def upload_bundle(
        self,
        package_name: str,
        bundle_path: pathlib.Path,
    ) -> InternalAppSharingArtifact:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/internalappsharingartifacts/uploadbundle
        """

        self._logger.debug("Upload an app bundle for %r to internal app sharing", package_name)
        upload_request: android_publisher_resources.InternalAppSharingArtifactHttpRequest = (
            self._internal_app_sharing_artifacts.uploadbundle(
                packageName=package_name,
                media_body=str(bundle_path),
                media_mime_type="application/octet-stream",
            )
        )
        response = cast(
            "android_publisher_resources.InternalAppSharingArtifact",
            self._execute_request(upload_request, "upload"),
        )
        self._logger.debug("Uploaded app bundle to internal app sharing for %r", package_name)
        return InternalAppSharingArtifact(**response)
