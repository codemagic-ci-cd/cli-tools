from __future__ import annotations

import dataclasses
from typing import Optional
from typing import get_type_hints


@dataclasses.dataclass
class ResultBase:
    @classmethod
    def create(cls, source: dict):
        known_fields = {}
        for field in dataclasses.fields(cls):
            for alias in [*field.metadata.get("aliases", []), field.metadata.get("alias"), field.name]:
                if alias:
                    known_fields[alias] = field

        hints = get_type_hints(cls)
        create_kwargs = {}
        for name, value in source.items():
            try:
                field = known_fields[name]
            except KeyError:
                continue

            hint = hints[field.name]
            if isinstance(hint, type(list[ResultBase])):
                hint_args = hint.__args__  # type: ignore
                _cls = next((h for h in hint_args if isinstance(h, type) and issubclass(h, ResultBase)), None)
                if _cls and value:
                    value = [v if isinstance(v, _cls) else _cls.create(v) for v in value]
            elif isinstance(hint, type) and issubclass(hint, ResultBase):
                value = hint.create(value)
            elif isinstance(hint, type(Optional[ResultBase])):
                hint_args = hint.__args__  # type: ignore
                _cls = next((h for h in hint_args if isinstance(h, type) and issubclass(h, ResultBase)), None)
                if _cls and value and not isinstance(value, _cls):
                    value = _cls.create(value)

            create_kwargs[field.name] = value

        return cls(**create_kwargs)


@dataclasses.dataclass
class UserInfo(ResultBase):
    description: str = dataclasses.field(metadata={"alias": "NSLocalizedDescription"})
    failure_reason: str = dataclasses.field(metadata={"alias": "NSLocalizedFailureReason"})
    recovery_suggestion: Optional[str] = dataclasses.field(
        default=None,
        metadata={"alias": "NSLocalizedRecoverySuggestion"},
    )

    code: Optional[str] = dataclasses.field(default=None)
    detail: Optional[str] = dataclasses.field(default=None)
    id: Optional[str] = dataclasses.field(default=None)
    meta: Optional[str] = dataclasses.field(default=None)
    source: Optional[str] = dataclasses.field(default=None)
    status: Optional[str] = dataclasses.field(default=None)
    title: Optional[str] = dataclasses.field(default=None)

    underlying_error: Optional[str] = dataclasses.field(default=None, metadata={"alias": "NSUnderlyingError"})
    iris_code: Optional[str] = dataclasses.field(default=None, metadata={"alias": "iris-code"})


@dataclasses.dataclass
class DeliveryDetails(ResultBase):
    delivery_uuid: str = dataclasses.field(metadata={"alias": "delivery-uuid"})
    transferred: str = dataclasses.field()


@dataclasses.dataclass
class ProductError(ResultBase):
    message: str = dataclasses.field()
    code: int = dataclasses.field()
    user_info: Optional[UserInfo] = dataclasses.field(
        default=None,
        metadata={
            "aliases": [
                "user-info",
                "userInfo",  # Appears in Xcode 16.x outputs
            ],
        },
    )
    underlying_errors: list[ProductError] = dataclasses.field(
        default_factory=list,
        metadata={"alias": "underlying-errors"},
    )


@dataclasses.dataclass
class AltoolResult(ResultBase):
    os_version: str = dataclasses.field(metadata={"alias": "os-version"})
    tool_version: str = dataclasses.field(metadata={"alias": "tool-version"})
    tool_path: str = dataclasses.field(metadata={"alias": "tool-path"})

    success_message: str = dataclasses.field(default="", metadata={"alias": "success-message"})
    details: Optional[DeliveryDetails] = dataclasses.field(default=None)

    product_errors: list[ProductError] = dataclasses.field(default_factory=list, metadata={"alias": "product-errors"})
    warnings: list[ProductError] = dataclasses.field(default_factory=list)
