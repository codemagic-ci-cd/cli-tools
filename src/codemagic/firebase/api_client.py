import json
from pathlib import Path
from typing import AnyStr
from typing import List
from typing import Optional
from typing import Union

from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

from .api_error import FirebaseAPIClientError
from .resource_managers.release_manager import FirebaseReleaseResourceManager
from .resources import FirebaseReleaseResource

CredentialsJson = Union[AnyStr, dict, Path]


class FirebaseAPIClient:
    def __init__(self, service_account_json_keyfile: CredentialsJson):
        self._service_account_json_keyfile = service_account_json_keyfile

    @property
    def service_account_json(self):
        if isinstance(self._service_account_json_keyfile, dict):
            return self._service_account_json_keyfile

        if isinstance(self._service_account_json_keyfile, Path):
            content = self._service_account_json_keyfile.read_text()
        else:
            content = self._service_account_json_keyfile

        try:
            return json.loads(content)
        except ValueError as ve:
            message = 'Unable to parse service account credentials, must be a valid json'
            raise FirebaseAPIClientError(message) from ve

    @property
    def service(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(self.service_account_json)
        return discovery.build('firebaseappdistribution', 'v1', credentials=credentials)

    def list_releases(
        self,
        project_id: str,
        app_id: str,
        page_size: int = 25,
        limit: Optional[int] = None,
        order_by: FirebaseReleaseResourceManager.OrderBy = FirebaseReleaseResourceManager.OrderBy.create_time_desc,
    ) -> List[FirebaseReleaseResource]:
        """https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases/list
        """
        manager = FirebaseReleaseResourceManager(project_id, app_id)
        return list(manager.iterate_resource_items(self.service, order_by, limit, page_size))
