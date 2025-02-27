from typing import Optional

from .xml_resource import XmlResource


class Strings(XmlResource):
    """
    https://developer.android.com/guide/topics/resources/string-resource
    Android String resources are saved in strings.xml file that have the following contents:

    <?xml version="1.0" encoding="utf-8"?>
    <resources>
        <string name="hello">Hello!</string>
    </resources>
    """

    def get_value(self, name) -> Optional[str]:
        for string in self._iter_tags("string"):
            if self._get_attribute_value(string, "name") == name:
                return string.text
        return None
