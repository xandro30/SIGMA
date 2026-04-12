from __future__ import annotations

from typing import Protocol

from sigma_core.planning.domain.aggregates.week import Week
from sigma_core.planning.domain.value_objects import WeekId


class WeekRepository(Protocol):
    async def save(self, week: Week) -> None: ...

    async def get_by_id(self, week_id: WeekId) -> Week | None: ...

    async def delete(self, week_id: WeekId) -> None: ...
