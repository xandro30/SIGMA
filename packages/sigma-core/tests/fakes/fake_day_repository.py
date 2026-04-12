from datetime import date

from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.value_objects import DateRange, DayId
from sigma_core.shared_kernel.value_objects import SpaceId


class FakeDayRepository:
    def __init__(self) -> None:
        self._store: dict[str, Day] = {}

    async def save(self, day: Day) -> None:
        self._store[day.id.value] = day

    async def get_by_id(self, day_id: DayId) -> Day | None:
        return self._store.get(day_id.value)

    async def get_by_space_and_date(
        self, space_id: SpaceId, target_date: date
    ) -> Day | None:
        for d in self._store.values():
            if d.space_id == space_id and d.date == target_date:
                return d
        return None

    async def list_by_space_and_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[Day]:
        return [
            d
            for d in self._store.values()
            if d.space_id == space_id
            and date_range.start <= d.date <= date_range.end
        ]

    async def delete(self, day_id: DayId) -> None:
        self._store.pop(day_id.value, None)
