from __future__ import annotations

import dataclasses
import enum
import re
from abc import ABC
from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Type
from typing import TypeVar
from typing import Union
from typing import overload

from dateutil.parser import parse
from dateutil.tz import tzutc

from codemagic.models import DictSerializable
from codemagic.models import JsonSerializable
from codemagic.models import JsonSerializableMeta
from codemagic.utilities import log

from .enums import ResourceType

LRD = TypeVar("LRD", bound="LinkedResourceData")
ResourceReference = Union["ResourceId", LRD]


class ResourceId(str):
    pass


class AppleDictSerializable(DictSerializable):
    @classmethod
    def _serialize(cls, obj):
        if isinstance(obj, datetime):
            return Resource.to_iso_8601(obj)
        return super()._serialize(obj)


@dataclass
class GracefulDataclassMixin(ABC):
    @classmethod
    def get_fields(cls) -> Set[str]:
        return {f.name for f in dataclasses.fields(cls)}

    @classmethod
    def get_defined_fields(cls, parent_class: Type, given_fields: Dict[str, Any]) -> Dict[str, Any]:
        logger = log.get_logger(cls, log_to_stream=False)
        defined_fields = cls.get_fields()
        fields = {}
        for field_name, field_value in given_fields.items():
            if field_name in defined_fields:
                fields[field_name] = field_value
            else:
                logger.warning("Unknown field %r for resource %s.%s", field_name, parent_class.__name__, cls.__name__)
        return fields


@dataclass
class PagingInformation(AppleDictSerializable):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/paginginformation
    """

    @dataclass
    class Paging(AppleDictSerializable):
        total: int
        limit: int

    paging: Paging

    def __post_init__(self):
        if isinstance(self.paging, dict):
            self.paging = PagingInformation.Paging(**self.paging)


@dataclass
class Links(AppleDictSerializable):
    _OMIT_IF_NONE_KEYS = ("self", "related")

    self: Optional[str] = None
    related: Optional[str] = None


@dataclass
class ResourceLinks(AppleDictSerializable):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/resourcelinks
    """

    self: str


@dataclass
class Data(AppleDictSerializable):
    id: str
    type: ResourceType

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = ResourceType(self.type)


@dataclass
class Relationship(AppleDictSerializable):
    _OMIT_IF_NONE_KEYS = ("data", "meta")

    links: Links
    data: Optional[Union[Data, List[Data]]] = None
    meta: Optional[PagingInformation] = None

    def __post_init__(self):
        if isinstance(self.links, dict):
            self.links = Links(**self.links)
        if isinstance(self.data, dict):
            self.data = Data(**self.data)
        elif isinstance(self.data, list):
            if self.data and isinstance(self.data[0], dict):
                self.data = [Data(**data) for data in self.data]
        if isinstance(self.meta, dict):
            self.meta = PagingInformation(**self.meta)


class LinkedResourceData(AppleDictSerializable, JsonSerializable):
    def __init__(self, api_response: Dict):
        self._raw = api_response
        self.type = ResourceType(api_response["type"])
        self.id: ResourceId = ResourceId(api_response["id"])

    def __str__(self):
        return "\n".join(
            [
                f"Id: {self.id}",
                f"Type: {self.type.value}",
            ],
        )


class PrettyNameMeta(JsonSerializableMeta):
    def __str__(cls):  # noqa: N805
        class_name = cls.__name__
        name = re.sub(r"([A-Z])", r" \1", class_name).lstrip(" ")
        return re.sub("Id", "ID", name)

    @property
    def s(cls) -> str:  # noqa: N805
        """Plural name of the object"""
        return cls.plural()

    def plural(cls, count: Optional[int] = None) -> str:  # noqa: N805
        """Optional plural name of the object depending on the count"""
        singular = str(cls)
        if count == 1:
            return singular
        if singular.endswith("y"):
            return f"{singular[:-1]}ies"
        return f"{singular}s"


# workaround for Inconsistent metaclass structure for "Resource" error
class PrettyNameAbcMeta(PrettyNameMeta, ABCMeta):
    pass


class Resource(LinkedResourceData, metaclass=PrettyNameAbcMeta):
    _OMIT_IF_NONE_KEYS = ("relationships",)

    def __init_subclass__(cls) -> None:
        """
        hack to work around the fact that we are overriding the `attributes` and ``relationships`` properties with
        variables instead of properties

        they are always given values in ``__init__``, but that runs after the check in ``ABCMeta``
        """
        cls.attributes = None  # type:ignore[assignment]
        cls.relationships = None  # type:ignore[assignment]
        super().__init_subclass__()

    @dataclass
    class Attributes(AppleDictSerializable, GracefulDataclassMixin):
        pass

    @dataclass
    class Relationships(AppleDictSerializable, GracefulDataclassMixin):
        def __post_init__(self):
            for field in self.__dict__:
                current_value = getattr(self, field)
                if current_value is None or isinstance(current_value, Relationship):
                    continue

                # Relationships should have at least 'links' attribute.
                # Set the value to none for empty relationships.
                updated_value = Relationship(**current_value) if current_value else None
                setattr(self, field, updated_value)

    @classmethod
    def _create_attributes(cls, api_response) -> Attributes:
        if cls.Attributes is Resource.Attributes:
            # In case the resource does not have attributes
            defined_fields = {}
        else:
            defined_fields = cls.Attributes.get_defined_fields(cls, api_response["attributes"])
        return cls.Attributes(**defined_fields)

    @classmethod
    def get_id(cls, resource_reference: ResourceReference) -> ResourceId:
        if isinstance(resource_reference, LinkedResourceData):
            return resource_reference.id
        return resource_reference

    @classmethod
    def _create_relationships(cls, api_response) -> Relationships:
        if cls.Relationships is Resource.Relationships:
            # In case the resource does not have relationships
            defined_fields = {}
        else:
            defined_fields = cls.Relationships.get_defined_fields(cls, api_response["relationships"])
        return cls.Relationships(**defined_fields)

    def __init__(self, api_response: Dict, created: bool = False):
        super().__init__(api_response)
        self._created = created
        self.links: ResourceLinks = ResourceLinks(**api_response["links"])
        self.attributes = self._create_attributes(api_response)
        if "relationships" in api_response:
            self.relationships = self._create_relationships(api_response)
        else:
            self.relationships = None

    @property
    @abstractmethod
    def attributes(self) -> Attributes: ...

    @attributes.setter
    def attributes(self, value: Attributes) -> None: ...

    @property
    @abstractmethod
    def relationships(self) -> Optional[Relationships]: ...

    @relationships.setter
    def relationships(self, value: Optional[Relationships]) -> None: ...

    @property
    def created(self) -> bool:
        return self._created

    @classmethod
    @overload
    def from_iso_8601(cls, iso_8601_timestamp: None) -> None: ...

    @classmethod
    @overload
    def from_iso_8601(cls, iso_8601_timestamp: str) -> datetime: ...

    @classmethod
    def from_iso_8601(cls, iso_8601_timestamp: Optional[str]):
        return parse(iso_8601_timestamp) if iso_8601_timestamp else None

    @classmethod
    @overload
    def to_iso_8601(cls, dt: None, with_fractional_seconds: bool = True) -> None: ...

    @classmethod
    @overload
    def to_iso_8601(cls, dt: datetime, with_fractional_seconds: bool = True) -> str: ...

    @classmethod
    def to_iso_8601(cls, dt: Optional[datetime], with_fractional_seconds: bool = True):
        if dt is None:
            return None
        if dt.tzinfo in (timezone.utc, tzutc()) and with_fractional_seconds:
            # while most of API responses contain timestamps as '2020-08-04T11:44:12.000+0000'
            # resolved to datetime.datetime(2020, 8, 4, 11, 44, 12, tzinfo=datetime.timezone.utc),
            # /builds endpoint returns timestamps as isoformat() '2021-01-28T06:01:32-08:00'
            # resolved to datetime.datetime(
            #   2021, 1, 28, 6, 1, 32, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=57600))
            # ).
            # So need to convert it to the initial form based on the presence of the explicit utc timezone
            return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"
        return dt.isoformat()

    def _format_attribute_name(self, name: str) -> str:
        type_prefix = self.type.value.rstrip("s")
        name = re.sub(f"{type_prefix}s?", "", name)
        name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
        name = name.lower().capitalize()
        return re.sub("(i|vision|mac) os ", r"\1OS", name)

    def _hide_attribute_value(self, attribute_name: str) -> bool:
        if not hasattr(self.attributes, "__dataclass_fields__"):
            return False
        field = self.attributes.__dataclass_fields__[attribute_name]
        return field.metadata.get("hide") is True

    def _format_attribute_value(self, attribute_name: str, value: Any) -> Any:
        if self._hide_attribute_value(attribute_name):
            return '"..."'
        if isinstance(value, enum.Enum):
            return value.value
        if isinstance(value, DictSerializable):
            lines = "\n".join(f"\t{self._format_attribute_name(k)}: {v}" for k, v in value.dict().items())
            return f"\n{lines}"
        return value

    def __str__(self) -> str:
        s = super().__str__()
        for attribute_name, value in self.attributes.__dict__.items():
            if value is None:
                continue
            name = self._format_attribute_name(attribute_name)
            value = self._format_attribute_value(attribute_name, value)
            s += f"\n{name}: {value}"
        return s

    def __repr__(self):
        return f'<{self.__class__.__name__}: "{self.id}">'
