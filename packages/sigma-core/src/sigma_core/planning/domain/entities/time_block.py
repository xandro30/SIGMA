from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from sigma_core.planning.domain.errors import InvalidTimeBlockError
from sigma_core.planning.domain.value_objects import BlockId
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, Timestamp


@dataclass
class TimeBlock:
    """Bloque temporal absoluto dentro de un `Day`.

    Intervalo semi-abierto `[start_at, end_at)`. Bloques contiguos NO
    solapan (el instante final es exclusivo).
    """

    id: BlockId
    start_at: Timestamp
    duration: Minutes
    area_id: AreaId | None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.duration.value <= 0:
            raise InvalidTimeBlockError(
                f"TimeBlock.duration must be > 0, got {self.duration.value}"
            )

    @property
    def end_at(self) -> Timestamp:
        return Timestamp(
            self.start_at.value + timedelta(minutes=self.duration.value)
        )

    def overlaps(self, other: TimeBlock) -> bool:
        """Dos bloques solapan si sus intervalos [start, end) se intersectan."""
        return (
            self.start_at.value < other.end_at.value
            and other.start_at.value < self.end_at.value
        )
