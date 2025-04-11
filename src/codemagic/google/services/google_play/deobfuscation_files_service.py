from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING
from typing import Final
from typing import cast

from codemagic.google.resources.google_play import DeobfuscationFile
from codemagic.google.resources.google_play import DeobfuscationFileType
from codemagic.google.services.resource_service import ResourceService

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3 import resources as android_publisher_resources


class DeobfuscationFilesService(
    ResourceService[DeobfuscationFile, "android_publisher_resources.AndroidPublisherResource"],
):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.deobfuscationfiles
    """

    resource_type: Final = DeobfuscationFile

    @property
    def _debug_obfuscation_files(
        self,
    ) -> android_publisher_resources.AndroidPublisherResource.EditsResource.DeobfuscationfilesResource:
        return self._google_service.edits().deobfuscationfiles()

    def upload(
        self,
        package_name: str,
        edit_id: str,
        apk_version_code: int,
        deobfuscation_file_path: pathlib.Path,
        deobfuscation_file_type: DeobfuscationFileType,
    ) -> DeobfuscationFile:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits.deobfuscationfiles/upload
        """
        self._logger.debug(
            "Upload %s deobfuscation file for %r version %r using edit %s",
            deobfuscation_file_type,
            package_name,
            apk_version_code,
            edit_id,
        )
        upload_request: android_publisher_resources.DeobfuscationFilesUploadResponseHttpRequest = (
            self._debug_obfuscation_files.upload(
                packageName=package_name,
                editId=edit_id,
                apkVersionCode=apk_version_code,
                deobfuscationFileType=deobfuscation_file_type.value,
                media_body=str(deobfuscation_file_path),
                media_mime_type="application/octet-stream",
            )
        )
        response = cast(
            "android_publisher_resources.DeobfuscationFilesUploadResponse",
            self._execute_request(upload_request, "upload"),
        )
        self._logger.debug("Uploaded deobfuscation file for %r", package_name)
        return DeobfuscationFile(**cast(dict, response["deobfuscationFile"]))
