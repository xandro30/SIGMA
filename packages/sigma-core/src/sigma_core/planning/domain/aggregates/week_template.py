from __future__ import annotations

from dataclasses import dataclass, field

from sigma_core.planning.domain.enums import DayOfWeek
from sigma_core.planning.domain.value_objects import DayTemplateId, WeekTemplateId
from sigma_core.shared_kernel.value_objects import SpaceId, Timestamp


@dataclass
class WeekTemplate:
    """Plantilla semanal con 7 slots (`DayOfWeek → DayTemplateId | None`)."""

    id: WeekTemplateId
    space_id: SpaceId
    name: str
    slots: dict[DayOfWeek, DayTemplateId | None] = field(default_factory=dict)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)

    def __post_init__(self) -> None:
        for dow in DayOfWeek:
            self.slots.setdefault(dow, None)

    def set_slot(self, day: DayOfWeek, template_id: DayTemplateId) -> None:
        self.slots[day] = template_id
        self._touch()

    def clear_slot(self, day: DayOfWeek) -> None:
        self.slots[day] = None
        self._touch()

    def rename(self, name: str) -> None:
        self.name = name
        self._touch()

    def _touch(self) -> None:
        self.updated_at = Timestamp.now()
