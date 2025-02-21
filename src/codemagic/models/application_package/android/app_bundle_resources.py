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

    Package 'biz.ontime.taxi.polotrip.driver':
    0x7f010000 - anim/abc_fade_in
        (default) - [FILE] res/anim/abc_fade_in.xml
    0x7f010001 - anim/abc_fade_out
        (default) - [FILE] res/anim/abc_fade_out.xml
    0x7f010002 - anim/abc_grow_fade_in_from_bottom
        (default) - [FILE] res/anim/abc_grow_fade_in_from_bottom.xml
    0x7f020027 - attr/alpha
        (default) - [ATTR] {}
    0x7f020028 - attr/alphabeticModifiers
        (default) - [ATTR] {id/ALT=2, id/CTRL=4096, id/FUNCTION=8, id/META=65536, id/SHIFT=1, id/SYM=4}
    0x7f020029 - attr/ambientEnabled
        (default) - [ATTR] {}
    0x7f0d0000 - string/abc_action_bar_home_description
        (default) - [STR] "Navigate home"
        locale: "ca" - [STR] "Navega a la pàgina d'inici"
        locale: "da" - [STR] "Find hjem"
        locale: "fa" - [STR] "پیمایش به صفحه اصلی"
        locale: "ja" - [STR] "ホームに戻る"
        locale: "ka" - [STR] "მთავარზე გადასვლა"
        locale: "pa" - [STR] "ਹੋਮ 'ਤੇ ਜਾਓ"
    0x7f0e004f - style/Base.ThemeOverlay.AppCompat.Dialog.Alert
        (default) - [STYLE] [@dimen/abc_dialog_min_width_major, @dimen/abc_dialog_min_width_minor]
    0x7f0e0050 - style/Base.ThemeOverlay.AppCompat.Light
        (default) - [STYLE] [
            @color/background_material_light,
            @color/foreground_material_light,
            @color/foreground_material_dark,
            @color/background_material_light,
            @color/background_floating_material_light,
            @color/abc_primary_text_material_light,
            @color/abc_primary_text_material_dark,
            @color/abc_secondary_text_material_light,
            @color/abc_secondary_text_material_dark,
            @color/abc_secondary_text_material_light,
            @color/abc_secondary_text_material_dark,
            @color/abc_primary_text_disable_only_material_light,
            @color/abc_hint_foreground_material_light,
            @color/abc_hint_foreground_material_dark,
            @color/highlighted_text_material_light,
            ?android:attr/textColorSecondary,
            @color/ripple_material_light,
            @color/button_material_light,
            @color/switch_thumb_material_light,
            true,
            @color/abc_primary_text_disable_only_material_dark,
            @color/abc_background_cache_hint_selector_material_light,
        ]
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
