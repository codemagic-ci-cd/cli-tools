from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Type
from typing import Union
from typing import cast

from codemagic.google.resource_managers.resource_manager import ResourceManager
from codemagic.google.resources.google_play import Edit

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3 import AndroidPublisherResource
    from googleapiclient._apis.androidpublisher.v3 import AppEdit
    from googleapiclient._apis.androidpublisher.v3 import AppEditHttpRequest


class GooglePlayEditsManager(ResourceManager[Edit, "AndroidPublisherResource"]):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits
    """

    resource_type: ClassVar[Type[Edit]] = Edit

    @property
    def _edits(self) -> AndroidPublisherResource.EditsResource:
        return self._google_service.edits()

    @classmethod
    def _resolve_id(cls, edit: Union[Edit, str]) -> str:
        if isinstance(edit, Edit):
            return edit.id
        return edit

    def create(self, package_name: str) -> Edit:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits/insert
        """
        self._logger.debug("Create edit for %r", package_name)
        insert_request: AppEditHttpRequest = self._edits.insert(
            body={},
            packageName=package_name,
        )
        response = cast(
            "AppEdit",
            self._execute_request(insert_request, "insert"),
        )
        self._logger.debug("Created edit %s", response["id"])
        return Edit(**response)

    def delete(self, edit: Union[Edit, str], package_name: str) -> None:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits/delete
        """
        edit_id = self._resolve_id(edit)
        self._logger.debug("Delete edit %s for %r", edit_id, package_name)
        delete_request = self._edits.delete(
            packageName=package_name,
            editId=edit_id,
        )
        self._execute_request(delete_request, "delete")
        self._logger.debug("Deleted edit %s", edit_id)
