"""IDs del BC tracking."""
from __future__ import annotations

import uuid
from dataclasses import dataclass


def _validate_uuid4(value: str, class_name: str) -> None:
    try:
        parsed = uuid.UUID(value, version=4)
        if str(parsed) != value:
            raise ValueError()
    except ValueError:
        raise ValueError(f"{class_name} inválido: {value!r}")


@dataclass(frozen=True)
class WorkSessionId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "WorkSessionId")

    @classmethod
    def generate(cls) -> WorkSessionId:
        return cls(str(uuid.uuid4()))


@dataclass(frozen=True)
class TrackingEntryId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "TrackingEntryId")

    @classmethod
    def generate(cls) -> TrackingEntryId:
        return cls(str(uuid.uuid4()))
