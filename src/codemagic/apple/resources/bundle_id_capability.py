from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Optional

from .enums import CapabilityOptionKey
from .enums import CapabilitySettingAllowedInstance
from .enums import CapabilitySettingKey
from .enums import CapabilityType
from .resource import AppleDictSerializable
from .resource import Relationship
from .resource import Resource


@dataclass
class CapabilityOption(AppleDictSerializable):
    description: str
    enabled: bool
    enabledByDefault: bool
    key: CapabilityOptionKey
    name: str
    supportsWildcard: bool

    def __post_init__(self):
        if isinstance(self.key, str):
            self.key = CapabilityOptionKey(self.key)


@dataclass
class CapabilitySetting(AppleDictSerializable):
    allowedInstances: CapabilitySettingAllowedInstance
    description: str
    enabledByDefault: bool
    key: CapabilitySettingKey
    name: str
    options: Optional[CapabilityOption]
    visible: bool
    minInstances: int

    def __post_init__(self):
        if isinstance(self.allowedInstances, str):
            self.allowedInstances = CapabilitySettingAllowedInstance(self.allowedInstances)
        if isinstance(self.options, dict):
            self.options = CapabilityOption(**self.options)


class BundleIdCapability(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/bundleidcapability
    """

    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        capabilityType: CapabilityType
        settings: Optional[CapabilitySetting]

        def __post_init__(self):
            if isinstance(self.capabilityType, str):
                self.capabilityType = CapabilityType(self.capabilityType)
            if isinstance(self.settings, dict):
                self.settings = CapabilitySetting(**self.settings)

    @dataclass
    class Relationships(Resource.Relationships):
        bundleId: Relationship

    def _format_attribute_value(self, attribute_name: str, value: Any) -> Any:
        if attribute_name == "capabilityType":
            # In case we get an unknown capability type from API response, then this is stored as
            # a runtime-created fallback enumeration `GracefulCapabilityType` which does not have
            # the properties and methods that `CapabilityType` has.
            if isinstance(self.attributes.capabilityType, CapabilityType):
                return self.attributes.capabilityType.display_name
            return CapabilityType.get_default_display_name(self.attributes.capabilityType.value)
        return super()._format_attribute_value(attribute_name, value)
