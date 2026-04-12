from __future__ import annotations

from datetime import date
from typing import Protocol

from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.value_objects import DateRange, DayId
from sigma_core.shared_kernel.value_objects import SpaceId


class DayRepository(Protocol):
    async def save(self, day: Day) -> None: ...

    async def get_by_id(self, day_id: DayId) -> Day | None: ...

    async def get_by_space_and_date(
        self, space_id: SpaceId, target_date: date
    ) -> Day | None: ...

    async def list_by_space_and_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[Day]: ...

    async def delete(self, day_id: DayId) -> None: ...
