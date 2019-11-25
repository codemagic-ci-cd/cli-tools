from collections import OrderedDict
from typing import NamedTuple, Dict

from .resource import Resource


class AppAttributes(NamedTuple):
    name: str
    bundleId: str
    sku: str
    primaryLocale: str

    def dict(self) -> OrderedDict:
        return OrderedDict((k, v) for k, v in self._asdict().items() if v is not None)


class App(Resource):

    def __init__(self, api_response: Dict):
        print(api_response)
        super().__init__(api_response)
        self.attributes = AppAttributes(**api_response['attributes'])
