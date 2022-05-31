from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .bundle_id import BundleIdPlatform
from .enums import DeviceClass
from .enums import DeviceStatus
from .resource import Resource


class Device(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/device
    """

    attributes: Attributes
    relationships: Optional[Resource.Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        deviceClass: DeviceClass
        model: str
        name: str
        platform: BundleIdPlatform
        status: DeviceStatus
        udid: str
        addedDate: datetime

        def __post_init__(self):
            if isinstance(self.deviceClass, str):
                self.deviceClass = DeviceClass(self.deviceClass)
            if isinstance(self.platform, str):
                self.platform = BundleIdPlatform(self.platform)
            if isinstance(self.status, str):
                self.status = DeviceStatus(self.status)
            if isinstance(self.addedDate, str):
                self.addedDate = Resource.from_iso_8601(self.addedDate)
