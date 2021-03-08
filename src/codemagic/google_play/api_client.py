import json
from typing import Optional

import httplib2
from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.service_account import ServiceAccountCredentials

from .api_error import AuthorizationError
from .api_error import CredentialsError
from .api_error import EditError
from .api_error import VersionCodeFromTrackError
from .resource_printer import ResourcePrinter
from .resources import Edit
from .resources import Track
from .resources import TrackName


class GooglePlayDeveloperAPIClient:
    SCOPE = 'androidpublisher'
    SCOPE_URI = f'https://www.googleapis.com/auth/{SCOPE}'
    API_VERSION = 'v3'

    _service_instance: Optional[discovery.Resource] = None

    def __init__(self,
                 credentials: str,
                 package_name: str,
                 resource_printer: ResourcePrinter):
        """
        :param credentials: Your Gloud Service account credentials with JSON key type
        :param package_name: package name of the app in Google Play Console (Ex: com.google.example)
        :param resource_printer: printer initialized in google-play tool
        """
        self._credentials = credentials
        self.package_name = package_name
        self.resource_printer = resource_printer

    def get_edit_resource(self):
        return self.service.edits()  # type: ignore

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

    def create_edit(self) -> Edit:
        self.resource_printer.log_request(f'Create an edit for the package "{self.package_name}"')
        try:
            edit_response = self.get_edit_resource().insert(body={}, packageName=self.package_name).execute()
            resource = Edit(**edit_response)
            self.resource_printer.print_resource(resource)
            return resource
        except errors.HttpError as e:
            raise EditError('create', self.package_name, e._get_reason() or 'Http Error')
        except errors.Error as e:
            raise EditError('create', self.package_name, str(e))

    def delete_edit(self, edit_id: str) -> None:
        self.resource_printer.log_request(f'Delete the edit "{edit_id}" for the package "{self.package_name}"')
        try:
            self.get_edit_resource().delete(packageName=self.package_name, editId=edit_id).execute()
            self._service_instance = None
        except errors.HttpError as e:
            raise EditError('delete', self.package_name, e._get_reason() or 'Http Error')
        except errors.Error as e:
            raise EditError('delete', self.package_name, str(e))

    def get_track_information(self, edit_id: str, track_name: TrackName) -> Track:
        self.resource_printer.log_request(
            f'Get information about the track "{track_name.value}" '
            f'for the package "{self.package_name}"',
        )
        try:
            track_response = self.get_edit_resource().tracks().get(
                packageName=self.package_name, editId=edit_id, track=track_name.value).execute()
            resource = Track(**track_response)
            self.resource_printer.print_resource(resource)
            return resource
        except errors.HttpError as e:
            raise VersionCodeFromTrackError(track_name.value, e._get_reason() or 'Http Error')
        except errors.Error as e:
            raise VersionCodeFromTrackError(track_name.value, str(e))
