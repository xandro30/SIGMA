from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sigma_core.shared_kernel.config import get_app_timezone
from sigma_core.shared_kernel.enums import CardSize


# ── Identifier helpers ────────────────────────────────────────────


def _validate_uuid4(value: str, class_name: str) -> None:
    try:
        parsed = uuid.UUID(value, version=4)
        if str(parsed) != value:
            raise ValueError()
    except ValueError:
        raise ValueError(f"{class_name} inválido: {value!r} — debe ser un UUID v4")


# ── Identifiers ───────────────────────────────────────────────────


@dataclass(frozen=True)
class CardId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "CardId")

    @classmethod
    def generate(cls) -> CardId:
        return cls(str(uuid.uuid4()))


@dataclass(frozen=True)
class SpaceId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "SpaceId")

    @classmethod
    def generate(cls) -> SpaceId:
        return cls(str(uuid.uuid4()))


@dataclass(frozen=True)
class AreaId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "AreaId")

    @classmethod
    def generate(cls) -> AreaId:
        return cls(str(uuid.uuid4()))


# ── Temporal ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class Timestamp:
    """Instante temporal con zona horaria, anclado a Europe/Madrid en
    construcciones automáticas (``Timestamp.now``). Siempre timezone-aware."""

    value: datetime

    def __post_init__(self):
        if self.value.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware")

    @classmethod
    def now(cls) -> Timestamp:
        return cls(datetime.now(get_app_timezone()))


# ── Estimation ────────────────────────────────────────────────────


@dataclass(frozen=True)
class Minutes:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError(f"Minutes no puede ser negativo: {self.value}")

    def __add__(self, other: Minutes) -> Minutes:
        return Minutes(self.value + other.value)


@dataclass(frozen=True)
class SizeMapping:
    entries: dict[CardSize, Minutes]

    def __post_init__(self) -> None:
        missing = set(CardSize) - set(self.entries.keys())
        if missing:
            raise ValueError(
                f"SizeMapping incompleto, faltan entradas: {sorted(m.value for m in missing)}"
            )

    def get_minutes(self, size: CardSize) -> Minutes:
        return self.entries[size]

    def to_primitive(self) -> dict[str, int]:
        """Canonical primitive representation, ordered by CardSize enum."""
        return {size.value: self.entries[size].value for size in CardSize}

    @classmethod
    def from_primitive(cls, data: dict[str, int]) -> SizeMapping:
        """Build a SizeMapping from a primitive dict. Raises ValueError on invalid input."""
        return cls(
            entries={CardSize(k): Minutes(v) for k, v in data.items()},
        )

    @classmethod
    def default(cls) -> SizeMapping:
        return cls(entries={
            CardSize.XXS: Minutes(60),
            CardSize.XS: Minutes(120),
            CardSize.S: Minutes(240),
            CardSize.M: Minutes(480),
            CardSize.L: Minutes(960),
            CardSize.XL: Minutes(1920),
            CardSize.XXL: Minutes(3840),
        })
