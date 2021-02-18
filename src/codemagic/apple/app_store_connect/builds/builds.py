from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type

from codemagic.apple.app_store_connect.resource_manager import ResourceManager
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildProcessingState
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
        app: Optional[ResourceId] = None
        expired: Optional[bool] = None
        id: Optional[ResourceId] = None
        processing_state: Optional[BuildProcessingState] = None
        version: Optional[int] = None
        pre_release_version_version: Optional[str] = None

        @classmethod
        def _get_field_name(cls, field_name) -> str:
            if field_name == 'pre_release_version_version':
                field_name = 'pre_release_version.version'
            return super()._get_field_name(field_name)

    class Ordering(ResourceManager.Ordering):
        PRE_RELEASE_VERSION = 'preReleaseVersion'
        UPLOADED_DATE = 'uploadedDate'
        VERSION = 'version'

    def list(self,
             resource_filter: Filter = Filter(),
             ordering=Ordering.UPLOADED_DATE,
             reverse=False) -> List[Build]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_builds
        """

        params = {'sort': ordering.as_param(reverse), **resource_filter.as_query_params()}
        builds = self.client.paginate(f'{self.client.API_URL}/builds', params=params)
        return [Build(build) for build in builds]
