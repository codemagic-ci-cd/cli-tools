from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Type
from typing import Union
from typing import cast

from codemagic.google.resources.google_play import AppEdit
from codemagic.google.services.resource_service import ResourceService

if TYPE_CHECKING:
    from googleapiclient._apis.androidpublisher.v3 import AndroidPublisherResource
    from googleapiclient._apis.androidpublisher.v3 import AppEdit as GooglePlayAppEdit
    from googleapiclient._apis.androidpublisher.v3 import AppEditHttpRequest


class EditsService(ResourceService[AppEdit, "AndroidPublisherResource"]):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits
    """

    resource_type: ClassVar[Type[AppEdit]] = AppEdit

    @property
    def _edits(self) -> AndroidPublisherResource.EditsResource:
        return self._google_service.edits()

    @classmethod
    def _resolve_id(cls, edit: Union[AppEdit, str]) -> str:
        if isinstance(edit, AppEdit):
            return edit.id
        return edit

    def create(self, package_name: str) -> AppEdit:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits/insert
        """
        self._logger.debug("Create edit for %r", package_name)
        insert_request: AppEditHttpRequest = self._edits.insert(
            body={},
            packageName=package_name,
        )
        response = cast(
            "GooglePlayAppEdit",
            self._execute_request(insert_request, "insert"),
        )
        self._logger.debug("Created edit %s", response["id"])
        return AppEdit(**response)

    def commit(self, edit: Union[AppEdit, str], package_name: str) -> AppEdit:
        """
        https://developers.google.com/android-publisher/api-ref/rest/v3/edits/commit
        """
        edit_id = self._resolve_id(edit)
        self._logger.debug("Commit edit %s for %r", edit_id, package_name)
        commit_request = self._edits.commit(
            packageName=package_name,
            editId=edit_id,
        )
        response = cast(
            "GooglePlayAppEdit",
            self._execute_request(commit_request, "commit"),
        )
        self._logger.debug("Commited edit %s", response["id"])
        return AppEdit(**response)

    def delete(self, edit: Union[AppEdit, str], package_name: str) -> None:
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
