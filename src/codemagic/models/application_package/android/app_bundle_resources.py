from __future__ import annotations

import re
from collections import defaultdict
from functools import cached_property
from typing import Dict
from typing import List
from typing import Optional
from typing import cast


class _ResourceValue:
    _PATT = re.compile(r"^\s*(\(\w+\)) - (\[\w+\]) (.+)$")

    def __init__(self, locale: str, resource_type: str, value: str):
        self.locale = locale.lstrip("(").rstrip(")")
        self.resource_type = resource_type.lstrip("[").rstrip("]")
        self.value = value[1:-1] if value.startswith('"') and value.endswith('"') else value

    @classmethod
    def from_bundletool_output(cls, raw_output_line: str) -> _ResourceValue:
        match = cls._PATT.match(raw_output_line)
        if not match:
            raise ValueError("Not a resource value line")
        locale = match.group(1)
        resource_type = match.group(2)
        value = match.group(3)
        return cls(locale, resource_type, value)

    def is_default(self):
        return self.locale.lower() == "default"


class AppBundleResources:
    """
    Parse output from `bundletool dump resources --bundle app.aab --values`
    Example output is as follows:

    Package 'io.codemagic.cli_tools_google_play':
    0x7f010000 - attr/alpha
        (default) - [ATTR] {}
    0x7f010001 - attr/font
        (default) - [ATTR] {}
    0x7f010005 - attr/fontProviderFetchStrategy
        (default) - [ATTR] {id/blocking=0, id/async=1}
    0x7f020000 - color/androidx_core_ripple_material_light
        (default) - [COLOR_ARGB8] #1f000000
    0x7f020001 - color/androidx_core_secondary_text_default_material_light
        (default) - [COLOR_ARGB8] #8a000000
    0x7f020002 - color/black
        (default) - [COLOR_ARGB8] #ff000000
    0x7f020005 - color/notification_action_color_filter
        (default) - [REF] @color/androidx_core_secondary_text_default_material_light
    0x7f02000c - color/vector_tint_color
        (default) - [FILE] res/color/vector_tint_color.xml
    0x7f02000d - color/vector_tint_theme_color
        (default) - [FILE] res/color/vector_tint_theme_color.xml
    ...
    """

    def __init__(self, dump_output: str):
        self._dump_output = dump_output

    @classmethod
    def _is_resource_name_line(cls, line):
        try:
            int(line.split(" - ")[0], 16)
        except ValueError:
            return False
        return True

    def _parse_all_values(self) -> Dict[str, List[_ResourceValue]]:
        all_values = defaultdict(list)
        current_resource_name = None
        for line in self._dump_output.splitlines():
            if self._is_resource_name_line(line):
                current_resource_name = line.split(" - ")[-1]
            else:
                try:
                    value = _ResourceValue.from_bundletool_output(line)
                    all_values[current_resource_name].append(value)
                except ValueError:
                    pass
        return cast(dict, all_values)

    @classmethod
    def _choose_default_values(cls, all_values: Dict[str, List[_ResourceValue]]) -> Dict[str, str]:
        values = {}
        for resource_name, resource_values in all_values.items():
            if not resource_values:
                continue
            resource_value = next((rv for rv in resource_values if rv.is_default()), resource_values[0])
            values[resource_name] = resource_value.value
        return values

    @cached_property
    def _values(self) -> Dict[str, str]:
        all_values = self._parse_all_values()
        return self._choose_default_values(all_values)

    def get_resource(self, resource_name: str) -> Optional[str]:
        return self._values.get(resource_name)
