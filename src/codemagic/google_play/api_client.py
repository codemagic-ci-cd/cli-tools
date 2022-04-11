import contextlib
import json
from functools import lru_cache
from typing import AnyStr
from typing import List
from typing import Optional
from typing import Union

import httplib2
from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.service_account import ServiceAccountCredentials

from codemagic.utilities import log

from .api_error import AuthorizationError
from .api_error import EditError
from .api_error import GetResourceError
from .api_error import GooglePlayDeveloperAPIClientError
from .api_error import ListResourcesError
from .resources import Edit
from .resources import Track

CredentialsJson = Union[AnyStr, dict]


class GooglePlayDeveloperAPIClient:
    SCOPE = 'androidpublisher'
    SCOPE_URI = f'https://www.googleapis.com/auth/{SCOPE}'
    API_VERSION = 'v3'

    def __init__(self, service_account_json_keyfile: CredentialsJson):
        """
        :param service_account_json_keyfile: Your Gcloud Service account credentials with JSON key type
        """
        self._service_account_json_keyfile = service_account_json_keyfile
        self._logger = log.get_logger(self.__class__)

    @classmethod
    def _get_edit_id(cls, edit: Union[str, Edit]) -> str:
        if isinstance(edit, Edit):
            return edit.id
        return edit

    def _get_json_keyfile_dict(self) -> dict:
        if isinstance(self._service_account_json_keyfile, dict):
            return self._service_account_json_keyfile
        try:
            return json.loads(self._service_account_json_keyfile)
        except ValueError as ve:
            message = 'Unable to parse service account credentials, must be a valid json'
            raise GooglePlayDeveloperAPIClientError(message) from ve

    @lru_cache(1)
    def _get_android_publisher_service(self):
        json_keyfile = self._get_json_keyfile_dict()
        http = httplib2.Http()
        try:
            service_account_credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                json_keyfile,
                scopes=self.SCOPE_URI,
            )
            http = service_account_credentials.authorize(http)
            return discovery.build(
                self.SCOPE,
                self.API_VERSION,
                http=http,
                cache_discovery=False,
            )
        except (errors.Error, errors.HttpError) as e:
            raise AuthorizationError(e) from e

    @property
    def android_publishing_service(self):
        return self._get_android_publisher_service()

    @property
    def edits_service(self):
        return self.android_publishing_service.edits()

    def create_edit(self, package_name: str) -> Edit:
        self._logger.debug(f'Create an edit for the package {package_name!r}')
        try:
            edit_request = self.edits_service.insert(body={}, packageName=package_name)
            edit_response = edit_request.execute()
            self._logger.debug(f'Created edit {edit_response} for package {package_name!r}')
        except (errors.Error, errors.HttpError) as e:
            raise EditError('create', package_name, e) from e
        else:
            return Edit(**edit_response)

    def delete_edit(self, edit: Union[str, Edit], package_name: str) -> None:
        edit_id = self._get_edit_id(edit)
        self._logger.debug(f'Delete the edit {edit_id!r} for the package {package_name!r}')
        try:
            delete_request = self.edits_service.delete(
                packageName=package_name,
                editId=edit_id,
            )
            delete_request.execute()
            self._logger.debug(f'Deleted edit {edit_id} for package {package_name!r}')
        except (errors.Error, errors.HttpError) as e:
            raise EditError('delete', package_name, e) from e

    @contextlib.contextmanager
    def use_app_edit(self, package_name: str):
        edit = self.create_edit(package_name)
        try:
            yield edit
        finally:
            self.delete_edit(edit, package_name)

    def get_track(
        self,
        package_name: str,
        track_name: str,
        edit: Optional[Union[str, Edit]] = None,
    ) -> Track:
        if edit is not None:
            edit_id = self._get_edit_id(edit)
            return self._get_track(package_name, track_name, edit_id)
        with self.use_app_edit(package_name) as _edit:
            return self._get_track(package_name, track_name, _edit.id)

    def _get_track(self, package_name: str, track_name: str, edit_id: str) -> Track:
        self._logger.debug(f'Get track {track_name!r} for package {package_name!r} using edit {edit_id}')
        try:
            track_request = self.edits_service.tracks().get(
                packageName=package_name,
                editId=edit_id,
                track=track_name,
            )
            track_response = track_request.execute()
            self._logger.debug(f'Got track {track_name!r} for package {package_name!r}: {track_response}')
        except (errors.Error, errors.HttpError) as e:
            raise GetResourceError('track', package_name, e) from e
        else:
            return Track(**track_response)

    def list_tracks(
        self,
        package_name: str,
        edit: Optional[Union[str, Edit]] = None,
    ) -> List[Track]:
        if edit is not None:
            edit_id = self._get_edit_id(edit)
            return self._list_tracks(package_name, edit_id)
        with self.use_app_edit(package_name) as _edit:
            return self._list_tracks(package_name, _edit.id)

    def _list_tracks(self, package_name: str, edit_id: str) -> List[Track]:
        self._logger.debug(f'List tracks for package {package_name!r} using edit {edit_id}')
        try:
            tracks_request = self.edits_service.tracks().list(
                packageName=package_name,
                editId=edit_id,
            )
            tracks_response = tracks_request.execute()
            self._logger.debug(f'Got tracks for package {package_name!r}: {tracks_response}')
        except (errors.Error, errors.HttpError) as e:
            raise ListResourcesError('tracks', package_name, e) from e
        else:
            return [Track(**track) for track in tracks_response['tracks']]
