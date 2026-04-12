from __future__ import annotations

from dataclasses import dataclass

from sigma_core.planning.domain.errors import InvalidTimeBlockError
from sigma_core.planning.domain.value_objects import BlockId, TimeOfDay
from sigma_core.shared_kernel.value_objects import AreaId, Minutes


@dataclass
class DayTemplateBlock:
    """Bloque de plantilla diaria con hora relativa al día (sin fecha)."""

    id: BlockId
    start_at: TimeOfDay
    duration: Minutes
    area_id: AreaId | None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.duration.value <= 0:
            raise InvalidTimeBlockError(
                f"DayTemplateBlock.duration must be > 0, got {self.duration.value}"
            )

    def end_minutes(self) -> int:
        return self.start_at.to_minutes() + self.duration.value

    def overlaps(self, other: DayTemplateBlock) -> bool:
        return (
            self.start_at.to_minutes() < other.end_minutes()
            and other.start_at.to_minutes() < self.end_minutes()
        )
