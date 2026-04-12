from sigma_core.planning.domain.aggregates.week import Week
from sigma_core.planning.domain.value_objects import WeekId


class FakeWeekRepository:
    def __init__(self) -> None:
        self._store: dict[str, Week] = {}

    async def save(self, week: Week) -> None:
        self._store[week.id.value] = week

    async def get_by_id(self, week_id: WeekId) -> Week | None:
        return self._store.get(week_id.value)

    async def delete(self, week_id: WeekId) -> None:
        self._store.pop(week_id.value, None)
