from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING
from typing import Final
from typing import cast

from codemagic.google.resources.google_play import ExpansionFile
from codemagic.google.resources.google_play import ExpansionFileType
from codemagic.google.services.resource_service import ResourceService

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3 import resources as android_publisher_resources


class ExpansionFilesService(ResourceService[ExpansionFile, "android_publisher_resources.AndroidPublisherResource"]):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.expansionfiles
    """

    resource_type: Final = ExpansionFile

    @property
    def _expansion_files(
        self,
    ) -> android_publisher_resources.AndroidPublisherResource.EditsResource.ExpansionfilesResource:
        return self._google_service.edits().expansionfiles()

    def upload(
        self,
        package_name: str,
        edit_id: str,
        apk_version_code: int,
        expansion_file_path: pathlib.Path,
        expansion_file_type: ExpansionFileType,
    ) -> ExpansionFile:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.expansionfiles/upload
        """
        self._logger.debug(
            "Upload %s expansion file for %r version %r using edit %s",
            expansion_file_type,
            package_name,
            apk_version_code,
            edit_id,
        )
        upload_request: android_publisher_resources.ExpansionFilesUploadResponseHttpRequest = (
            self._expansion_files.upload(
                packageName=package_name,
                editId=edit_id,
                apkVersionCode=apk_version_code,
                expansionFileType=expansion_file_type.value,
                media_body=str(expansion_file_path),
                media_mime_type="application/octet-stream",
            )
        )
        response = cast(
            "android_publisher_resources.ExpansionFilesUploadResponse",
            self._execute_request(upload_request, "upload"),
        )
        self._logger.debug("Uploaded expansion file for %r", package_name)
        return ExpansionFile(**response["expansionFile"])

    def update(
        self,
        package_name: str,
        edit_id: str,
        apk_version_code: int,
        expansion_file_type: ExpansionFileType,
        references_version: int,
    ):
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.expansionfiles/update
        """
        self._logger.debug(
            "Update %s expansion file for %r version %r using edit %s",
            expansion_file_type,
            package_name,
            apk_version_code,
            edit_id,
        )

        update_request: android_publisher_resources.ExpansionFileHttpRequest = self._expansion_files.update(
            packageName=package_name,
            editId=edit_id,
            apkVersionCode=apk_version_code,
            expansionFileType=expansion_file_type.value,
            body={
                "referencesVersion": references_version,
            },
        )
        response = cast(
            "android_publisher_resources.ExpansionFile",
            self._execute_request(update_request, "update"),
        )
        self._logger.debug("Updated expansion file for %r", package_name)
        return ExpansionFile(**response)
