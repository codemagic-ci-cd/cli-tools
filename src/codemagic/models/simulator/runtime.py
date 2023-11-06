from __future__ import annotations

import enum
import re
from functools import total_ordering
from typing import Optional

from packaging.version import Version


@total_ordering
class Runtime:
    class Name(enum.Enum):
        I_OS = "iOS"
        TV_OS = "tvOS"
        WATCH_OS = "watchOS"
        VISION_OS = "visionOS"

        def __str__(self):
            return str(self.value)

    # visionOS is identified as xrOS in json output, so we need to search for it and adjust the name later
    _PATTERN = re.compile(r"((?P<name>iOS|tvOS|watchOS|visionOS|xrOS)[. -]?)(?P<version>(\d+[.-]?)+)")

    _VALIDATION_PATTERN = re.compile(r"((?P<name>iOS|tvOS|watchOS|visionOS|xrOS)[. -]?)?(?P<version>(\d+[.-]?)+)?")

    def __init__(self, raw_runtime_name: str):
        self.raw_name = raw_runtime_name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.raw_name!r})"

    def __str__(self):
        return f"{self.runtime_name.value} {self.runtime_version}"

    def __hash__(self):
        return hash(str(self))

    def validate(self):
        match = self._VALIDATION_PATTERN.search(self.raw_name)
        if not match:
            raise ValueError(f"Invalid runtime {self.raw_name!r}")
        elif not match.groupdict()["version"]:
            raise ValueError(f"Invalid runtime {self.raw_name!r}, missing runtime version")
        elif not match.groupdict()["name"]:
            raise ValueError(f"Invalid runtime {self.raw_name!r}, missing runtime name")

    @classmethod
    def parse(cls, string: str) -> Optional[Runtime]:
        match = cls._PATTERN.search(string)
        if match:
            return Runtime(match.group())
        return None

    @property
    def runtime_version(self) -> Version:
        match = self._PATTERN.search(self.raw_name)
        if not match:
            raise ValueError(f"Invalid runtime {self.raw_name!r}")
        return Version(match.groupdict()["version"].replace("-", "."))

    @property
    def runtime_name(self) -> Name:
        match = self._PATTERN.search(self.raw_name)
        if not match:
            raise ValueError(f"Invalid runtime {self.raw_name!r}")
        return Runtime.Name(match.groupdict()["name"].replace("xrOS", "visionOS"))

    def __eq__(self, other):
        if isinstance(other, str):
            other = Runtime(other)
        elif isinstance(other, Runtime):
            pass
        else:
            raise ValueError(f"Cannot compare {self.__class__.__name__} with {other.__class__.__name__}")

        return self.runtime_name == other.runtime_name and self.runtime_version == other.runtime_version

    def __lt__(self, other):
        if isinstance(other, str):
            other = Runtime(other)
        elif isinstance(other, Runtime):
            pass
        else:
            raise ValueError(f"Cannot compare {self.__class__.__name__} with {other.__class__.__name__}")

        if self.runtime_name == other.runtime_name:
            return self.runtime_version < other.runtime_version
        else:
            return self.runtime_name.value < other.runtime_name.value
