"""Safe conversion of SDK responses into MCP-compatible JSON values."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, TypeAlias, cast

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


def to_json_value(value: object) -> JsonValue:
    """Convert supported SDK and Python values to plain JSON-compatible values."""
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Enum):
        return to_json_value(value.value)
    if isinstance(value, date | datetime):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): to_json_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [to_json_value(item) for item in value]

    as_dict = getattr(value, "as_dict", None)
    if callable(as_dict):
        return to_json_value(cast(Any, as_dict)())
    if is_dataclass(value) and not isinstance(value, type):
        return to_json_value(asdict(value))

    raise TypeError(f"Unsupported response type: {type(value).__name__}")
