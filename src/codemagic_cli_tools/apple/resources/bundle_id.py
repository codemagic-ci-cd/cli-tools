import enum
from collections import OrderedDict
from typing import NamedTuple, Dict

from .resource import Resource


class BundleIdPlatform(enum.Enum):
    IOS = 'IOS'
    MAC_OS = 'MAC_OS'


class BundleIdAttributes(NamedTuple):
    name: str
    identifier: str
    platform: BundleIdPlatform
    seedId: str

    def dict(self) -> OrderedDict:
        d = OrderedDict((k, v) for k, v in self._asdict().items() if v is not None)
        d['platform'] = self.platform.value
        return d


class BundleId(Resource):

    def __init__(self, api_response: Dict):
        super().__init__(api_response)
        self.attributes = BundleIdAttributes(
            name=api_response['attributes']['name'],
            identifier=api_response['attributes']['identifier'],
            platform=BundleIdPlatform(api_response['attributes']['platform']),
            seedId=api_response['attributes']['seedId'],
        )
