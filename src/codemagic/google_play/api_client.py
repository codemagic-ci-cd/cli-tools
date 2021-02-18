import json
from itertools import chain
from typing import NoReturn

import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
from googleapiclient import errors

from codemagic.google_play import Track
from codemagic.google_play.api_error import AuthorizationError
from codemagic.google_play.api_error import CredentialsError
from codemagic.google_play.api_error import EditError
from codemagic.google_play.api_error import VersionCodeFromTrackError


class Credentials(str):
    pass


class PackageName(str):
    pass


class GooglePlayDeveloperAPIClient:
    SCOPE = "androidpublisher"
    SCOPE_URI = f'https://www.googleapis.com/auth/{SCOPE}'
    API_VERSION = "v3"

    _service_instance = None

    def __init__(self, credentials: Credentials, package_name: PackageName):
        """
        :param credentials: Your Gloud Service account credentials with JSON key type
        :param package_name of the app in Google Play Console (Ex: com.google.example)
        """
        self._credentials = credentials
        self.package_name = package_name

    @property
    def _service(self) -> discovery.Resource:
        if self._service_instance is None:
            try:
                json_credentials = json.loads(self._credentials)
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

    def create_edit(self) -> dict:
        try:
            return self._service.edits().insert(body={}, packageName=self.package_name).execute()
        except errors.HttpError as e:
            raise EditError('create', self.package_name, e._get_reason() or 'Http Error')
        except errors.Error as e:
            raise EditError('create', self.package_name, str(e))

    def delete_edit(self, edit_id: str) -> NoReturn:
        try:
            self._service.edits().delete(packageName=self.package_name, editId=edit_id).execute()
        except errors.HttpError as e:
            raise EditError('delete', self.package_name, e._get_reason() or 'Http Error')
        except errors.Error as e:
            raise EditError('delete', self.package_name, str(e))

    def _get_track_latest_version_code(self, edit_id: str, track: ):
        try:
            track_response = self._service.edits().tracks().get(packageName=self.package_name, editId=edit_id, track=track).execute()
        except errors.HttpError as e:
            raise VersionCodeFromTrackError(self.package_name, track, e._get_reason() or 'Http Error')
        except errors.Error as e:
            raise VersionCodeFromTrackError(self.package_name, track, str(e))

        releases = track_response.get('releases', [])
        if not releases:
            raise VersionCodeFromTrackError(self.package_name, track, 'No release information')
        version_codes = [release['versionCodes'] for release in releases if release.get('versionCodes')]
        if not version_codes:
            raise VersionCodeFromTrackError(self.package_name, track, 'No releases with uploaded App bundles or APKs')
        return str(max(map(int, chain(*version_codes))))
