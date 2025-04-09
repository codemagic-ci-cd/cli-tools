import abc
import pathlib
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log


class AbstractPackage(StringConverterMixin, metaclass=abc.ABCMeta):
    def __init__(self, path: Union[pathlib.Path, AnyStr]):
        self._logger = log.get_file_logger(self.__class__)
        if isinstance(path, (bytes, str)):
            self.path = pathlib.Path(self._str(path))
        else:
            self.path = path
        self._validate_package()

    @abc.abstractmethod
    def _validate_package(self):
        pass

    @abc.abstractmethod
    def get_summary(self) -> Dict[str, Any]:
        pass

    def get_text_summary(self) -> str:
        summary: List[str] = []
        for property_name, property_value in self.get_summary().items():
            name = property_name.replace("_", " ").capitalize().replace(" os ", " OS ")
            value: Optional[str] = None

            if isinstance(property_value, bool):
                value = "Yes" if property_value else "No"
            elif isinstance(property_value, list):
                if not property_value:
                    pass
                elif len(property_value) == 1:
                    # Show single value on the same line as property name
                    value = property_value[0]
                else:
                    # Multiple values are spanned over indented lines
                    lines = "\n".join(f"\t{v}" for v in property_value)
                    value = f"\n{lines}"
            else:
                value = str(property_value)
            summary.append(f"{name}: {'N/A' if value is None else value}")

        return "\n".join(sorted(summary))

    @classmethod
    def _format_name(cls, certificate_name_components: Dict[str, str]) -> str:
        from codemagic.models.certificate import CERTIFICATE_NAME_COMPONENT_TRANSFORMATION

        parts = (
            f"{CERTIFICATE_NAME_COMPONENT_TRANSFORMATION[k]}: {v}"
            for k, v in certificate_name_components.items()
            if k in CERTIFICATE_NAME_COMPONENT_TRANSFORMATION
        )
        return ", ".join(parts)
