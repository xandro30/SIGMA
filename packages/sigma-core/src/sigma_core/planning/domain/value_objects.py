from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from sigma_core.planning.domain.errors import InvalidDateRangeError


if TYPE_CHECKING:
    from sigma_core.shared_kernel.value_objects import SpaceId


# ── UUID helpers (propios del BC, no importados de task_management) ──


def _validate_uuid4(value: str, class_name: str) -> None:
    try:
        parsed = uuid.UUID(value, version=4)
        if str(parsed) != value:
            raise ValueError(f"UUID canonical form mismatch: {value!r}")
    except ValueError as err:
        raise ValueError(
            f"{class_name} inválido: {value!r} — debe ser un UUID v4"
        ) from err


def _validate_uuid_v4_or_v5(value: str, class_name: str) -> None:
    """Acepta UUID canónico en versiones 4 o 5. Se usa en DayId, que
    soporta ambos: v5 para IDs deterministas derivados de (space, date)
    y v4 para construcción ad-hoc en tests."""
    try:
        parsed = uuid.UUID(value)
        if parsed.version not in (4, 5):
            raise ValueError(
                f"UUID version {parsed.version} not supported (expected 4 or 5)"
            )
        if str(parsed) != value:
            raise ValueError(f"UUID canonical form mismatch: {value!r}")
    except ValueError as err:
        raise ValueError(
            f"{class_name} inválido: {value!r} — debe ser un UUID v4 o v5"
        ) from err


# Namespace estable para DayId determinista. No cambiar NUNCA este valor:
# los IDs ya persistidos dependen de él.
_DAY_ID_NAMESPACE = uuid.UUID("0b1c7f3e-5a2d-4c8e-9f6b-8d1a7e5c3b49")


# Namespace estable para WeekId determinista. Distinto del de DayId para
# que (space_id, date) produzca IDs distintos en cada agregado aunque la
# semilla coincida. No cambiar NUNCA este valor.
_WEEK_ID_NAMESPACE = uuid.UUID("4a2e3b1c-7d8f-4e9a-b6c5-2d1e8f7a9b34")


# ── Identifiers ──────────────────────────────────────────────────


@dataclass(frozen=True)
class CycleId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "CycleId")

    @classmethod
    def generate(cls) -> CycleId:
        return cls(str(uuid.uuid4()))


@dataclass(frozen=True)
class DayId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid_v4_or_v5(self.value, "DayId")

    @classmethod
    def generate(cls) -> DayId:
        return cls(str(uuid.uuid4()))

    @classmethod
    def for_space_and_date(
        cls, space_id: "SpaceId", target_date: date
    ) -> DayId:
        """Construye un DayId determinista a partir de ``(space_id, date)``.

        Garantiza que dos llamadas con los mismos argumentos produzcan el
        mismo UUID, lo que permite que ``CreateDay`` sea race-safe: en
        concurrencia ambos writers escriben el mismo documento Firestore
        y el segundo sobrescribe sin duplicar.
        """
        key = f"{space_id.value}:{target_date.isoformat()}"
        return cls(str(uuid.uuid5(_DAY_ID_NAMESPACE, key)))


@dataclass(frozen=True)
class DayTemplateId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "DayTemplateId")

    @classmethod
    def generate(cls) -> DayTemplateId:
        return cls(str(uuid.uuid4()))


@dataclass(frozen=True)
class WeekTemplateId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "WeekTemplateId")

    @classmethod
    def generate(cls) -> WeekTemplateId:
        return cls(str(uuid.uuid4()))


@dataclass(frozen=True)
class WeekId:
    """Identificador del agregado Week.

    Determinista a partir de ``(space_id, week_start)``: permite que
    ``CreateWeek`` sea race-safe de la misma forma que ``CreateDay``.
    Acepta UUID v4 (construcción ad-hoc en tests) y v5 (constructor
    determinista ``for_space_and_week_start``).
    """

    value: str

    def __post_init__(self) -> None:
        _validate_uuid_v4_or_v5(self.value, "WeekId")

    @classmethod
    def generate(cls) -> WeekId:
        return cls(str(uuid.uuid4()))

    @classmethod
    def for_space_and_week_start(
        cls, space_id: "SpaceId", week_start: date
    ) -> WeekId:
        key = f"{space_id.value}:{week_start.isoformat()}"
        return cls(str(uuid.uuid5(_WEEK_ID_NAMESPACE, key)))


@dataclass(frozen=True)
class BlockId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "BlockId")

    @classmethod
    def generate(cls) -> BlockId:
        return cls(str(uuid.uuid4()))


# ── DateRange ────────────────────────────────────────────────────


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise InvalidDateRangeError(
                f"DateRange inválido: start {self.start} > end {self.end}"
            )

    def contains(self, d: date) -> bool:
        return self.start <= d <= self.end

    def days_count(self) -> int:
        return (self.end - self.start).days + 1


# ── TimeOfDay ────────────────────────────────────────────────────


@dataclass(frozen=True)
class TimeOfDay:
    hour: int
    minute: int

    def __post_init__(self) -> None:
        if not 0 <= self.hour <= 23:
            raise ValueError(f"TimeOfDay.hour fuera de rango 0..23: {self.hour}")
        if not 0 <= self.minute <= 59:
            raise ValueError(f"TimeOfDay.minute fuera de rango 0..59: {self.minute}")

    def to_minutes(self) -> int:
        return self.hour * 60 + self.minute
