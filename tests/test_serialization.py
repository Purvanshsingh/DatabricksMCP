from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

import pytest

from databricks_mcp.serialization import to_json_value


class State(Enum):
    READY = "ready"


@dataclass
class Record:
    name: str
    state: State


class SdkRecord:
    def as_dict(self) -> dict[str, object]:
        return {"id": "abc", "created_at": datetime(2026, 7, 12, tzinfo=UTC)}


def test_converts_sdk_and_python_values() -> None:
    assert to_json_value(SdkRecord()) == {
        "id": "abc",
        "created_at": "2026-07-12T00:00:00+00:00",
    }
    assert to_json_value(Record("warehouse", State.READY)) == {
        "name": "warehouse",
        "state": "ready",
    }


def test_rejects_unknown_types() -> None:
    with pytest.raises(TypeError, match="Unsupported response type"):
        to_json_value(object())
