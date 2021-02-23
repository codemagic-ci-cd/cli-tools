import json
from typing import Dict

import httplib2  # type: ignore
from googleapiclient import discovery  # type: ignore
from googleapiclient import errors  # type: ignore
from oauth2client.service_account import ServiceAccountCredentials  # type: ignore

from codemagic.google_play import AuthorizationError
from codemagic.google_play import CredentialsError
from codemagic.google_play import EditError
from codemagic.google_play import GooglePlayTypes
from codemagic.google_play import Track
from codemagic.google_play import VersionCodeFromTrackError


class GooglePlayDeveloperAPIClient:
    SCOPE = 'androidpublisher'
    SCOPE_URI = f'https://www.googleapis.com/auth/{SCOPE}'
    API_VERSION = 'v3'

    _service_instance: discovery.Resource = None

    def __init__(self, credentials: GooglePlayTypes.Credentials, package_name: GooglePlayTypes.PackageName):
        """
        :param credentials: Your Gloud Service account credentials with JSON key type
        :param package_name of the app in Google Play Console (Ex: com.google.example)
        """
        self._credentials = credentials
        self.package_name = package_name

    @property
    def service(self) -> discovery.Resource:
        if self._service_instance is None:
            try:
                json_credentials = json.loads(str(self._credentials))
            except json.decoder.JSONDecodeError:
                raise CredentialsError()

            http = httplib2.Http()
            try:
                service_account_credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    json_credentials, scopes=self.SCOPE_URI)
                http = service_account_credentials.authorize(http)
                self._service_instance = discovery.build(self.SCOPE, self.API_VERSION, http=http, cache_discovery=False)
            except errors.HttpError as e:
                raise AuthorizationError(e._get_reason() or 'Http Error')
            except errors.Error as e:
                raise AuthorizationError(str(e))
        return self._service_instance

    def create_edit(self) -> Dict:
        try:
            return self.service.edits().insert(body={}, packageName=self.package_name).execute()
        except errors.HttpError as e:
            raise EditError('create', self.package_name, e._get_reason() or 'Http Error')
        except errors.Error as e:
            raise EditError('create', self.package_name, str(e))

    def delete_edit(self, edit_id: str) -> None:
        try:
            self.service.edits().delete(packageName=self.package_name, editId=edit_id).execute()
            self._service_instance = None
        except errors.HttpError as e:
            raise EditError('delete', self.package_name, e._get_reason() or 'Http Error')
        except errors.Error as e:
            raise EditError('delete', self.package_name, str(e))

    def get_track_information(self, edit_id: str, track: Track) -> Dict:
        try:
            return self.service.edits().tracks().get(
                packageName=self.package_name, editId=edit_id, track=track.value,
            ).execute()
        except errors.HttpError as e:
            raise VersionCodeFromTrackError(self.package_name, track.value, e._get_reason() or 'Http Error')
        except errors.Error as e:
            raise VersionCodeFromTrackError(self.package_name, track.value, str(e))
