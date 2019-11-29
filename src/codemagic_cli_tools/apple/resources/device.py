from __future__ import annotations

from dataclasses import dataclass

from .resource import Relationship
from .resource import Resource


class Device(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/device
    """

    @dataclass
    class Attributes(Resource.Attributes):
        # TODO
        ...

    @dataclass
    class Relationships(Resource.Relationships):
        # TODO
        ...

