from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

from .resource_managers.release_manager import FirebaseReleaseManager


class FirebaseApiClient:
    SERVICE_NAME = 'firebaseappdistribution'

    def __init__(self, service_account_dict: dict):
        self.service_account_dict = service_account_dict

    @property
    def _discovery_service(self) -> discovery.Resource:
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(self.service_account_dict)
        return discovery.build(self.SERVICE_NAME, 'v1', credentials=credentials)

    @property
    def releases(self) -> FirebaseReleaseManager:
        return FirebaseReleaseManager(self._discovery_service)
