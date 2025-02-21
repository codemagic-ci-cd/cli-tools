from typing import Optional

from .xml_resource import XmlResource


class AndroidManifest(XmlResource):
    @property
    def version_name(self) -> str:
        return self._get_attribute_value(self._et, "versionName")

    @property
    def version_code(self) -> str:
        return self._get_attribute_value(self._et, "versionCode")

    @property
    def app_label(self) -> str:
        application = self._find_tag("application")
        return self._get_attribute_value(application, "label")

    @property
    def package_name(self) -> str:
        return self._get_attribute_value(self._et, "package")

    @property
    def min_sdk_version(self) -> str:
        uses_sdk = self._find_tag("uses-sdk")
        return self._get_attribute_value(uses_sdk, "minSdkVersion")

    @property
    def target_sdk_version(self) -> str:
        uses_sdk = self._find_tag("uses-sdk")
        return self._get_attribute_value(uses_sdk, "targetSdkVersion")

    @property
    def debuggable(self) -> Optional[str]:
        application = self._find_tag("application")
        return self._get_attribute_value(application, "debuggable")
