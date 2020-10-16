import enum
import re
from distutils.version import LooseVersion
from functools import total_ordering


@total_ordering
class Runtime:
    class Name(enum.Enum):
        I_OS = 'iOS'
        TV_OS = 'tvOS'
        WATCH_OS = 'watchOS'

        def __str__(self):
            return str(self.value)

    def __init__(self, runtime_name):
        self._raw_name = runtime_name

    def __repr__(self):
        return f'{self.__class__.__name__}({self._raw_name!r})'

    def __str__(self):
        return f'{self.runtime_name.value} {self.runtime_version}'

    def __hash__(self):
        return hash(str(self))

    @property
    def runtime_version(self) -> LooseVersion:
        version = re.search(r'(\d+[.-]?)+', self._raw_name).group()
        return LooseVersion(version.replace('-', '.'))

    @property
    def runtime_name(self) -> Name:
        for runtime_name in Runtime.Name:
            if runtime_name.value.lower() in self._raw_name.lower():
                return runtime_name
        raise ValueError(f'Invalid runtime {self._raw_name!r}')

    def __eq__(self, other):
        if isinstance(other, str):
            other = Runtime(other)
        elif isinstance(other, Runtime):
            pass
        else:
            raise ValueError(f'Cannot compare {self.__class__.__name__} with {other.__class__.__name__}')

        return self.runtime_name == other.runtime_name and self.runtime_version == other.runtime_version

    def __lt__(self, other):
        if isinstance(other, str):
            other = Runtime(other)
        elif isinstance(other, Runtime):
            pass
        else:
            raise ValueError(f'Cannot compare {self.__class__.__name__} with {other.__class__.__name__}')

        if self.runtime_name == other.runtime_name:
            return self.runtime_version < other.runtime_version
        else:
            return self.runtime_name.value < other.runtime_name.value
