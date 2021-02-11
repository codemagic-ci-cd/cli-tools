from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildOrdering
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import LinkedResourceData
from codemagic.apple.resources import ResourceId


class Builds(ResourceManager[Build]):
    """
    Builds
    https://developer.apple.com/documentation/appstoreconnectapi/builds
    """

    @property
    def resource_type(self) -> Type[Build]:
        return Build

    @dataclass
    class Filter(ResourceManager.Filter):
        app: Optional[Union[str, ResourceId]] = None
        expired: Optional[str] = None
        id: Optional[Union[str, ResourceId]] = None
        processing_state: Optional[BuildProcessingState] = None
        version: Optional[str] = None
        pre_release_version__dot__version: Optional[str] = None

    class Ordering(ResourceManager.Ordering):
        PRE_RELEASE_VERSION = 'preReleaseVersion'
        UPLOADED_DATE = 'uploadedDate'
        VERSION = 'version'

    def list(self,
             resource_filter: Filter = Filter(),
             ordering: Optional[BuildOrdering] = None,
             reverse: bool = False) -> List[Build]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_builds
        """

        params = resource_filter.as_query_params()
        if ordering:
            params['sort'] = self.Ordering[ordering.value].as_param(reverse)

        builds = self.client.paginate(f'{self.client.API_URL}/builds', params=params)
        return [Build(build) for build in builds]

    def read(self, build: Union[LinkedResourceData, ResourceId]) -> Build:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_build_information
        """
        build_id = self._get_resource_id(build)
        response = self.client.session.get(f'{self.client.API_URL}/builds/{build_id}').json()
        return Build(response['data'])
