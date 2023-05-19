from codemagic.firebase.resource_managers.abstract_base_manager import FirebaseResourceManager
from codemagic.firebase.resources import FirebaseReleaseResource


class FirebaseReleaseResourceManager(FirebaseResourceManager[FirebaseReleaseResource]):
    Resource = FirebaseReleaseResource

    def __init__(self, project_id, app_id):
        self.project_id = project_id
        self.app_id = app_id

    @classmethod
    def resource(cls, service):
        return service.projects().apps().releases()

    @property
    def query_parameters(self):
        parent = f'projects/{self.project_id}/apps/{self.app_id}'
        return {'parent': parent}
