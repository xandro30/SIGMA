from sigma_core.task_management.domain.entities.area import Area
from sigma_core.task_management.domain.value_objects import AreaId


class FakeAreaRepository:
    def __init__(self) -> None:
        self._store: dict[str, Area] = {}

    async def save(self, area: Area) -> None:
        self._store[area.id.value] = area

    async def get_by_id(self, area_id: AreaId) -> Area | None:
        return self._store.get(area_id.value)

    async def get_all(self) -> list[Area]:
        return list(self._store.values())

    async def delete(self, area_id: AreaId) -> None:
        self._store.pop(area_id.value, None)