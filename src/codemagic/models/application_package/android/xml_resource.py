from typing import AnyStr
from typing import Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


class XmlResource:
    def __init__(self, xml: AnyStr):
        self._et = ElementTree.fromstring(xml)

    @classmethod
    def _get_attribute_value(cls, element, attribute_name, *, default: str = "") -> str:
        for attribute, value in element.attrib.items():
            if attribute.endswith(attribute_name):
                return value
        return default

    def _iter_tags(self, tag_name):
        for el in self._et.iter():
            if el.tag == tag_name:
                yield el

    def _find_tag(self, tag_name) -> Optional[Element]:
        return next(self._iter_tags(tag_name), None)
