from sigma_core.task_management.domain.aggregates.space import Space
from sigma_core.shared_kernel.value_objects import SpaceId


class FakeSpaceRepository:
    def __init__(self) -> None:
        self._store: dict[str, Space] = {}

    async def save(self, space: Space) -> None:
        self._store[space.id.value] = space

    async def get_by_id(self, space_id: SpaceId) -> Space | None:
        return self._store.get(space_id.value)

    async def get_all(self) -> list[Space]:
        return list(self._store.values())

    async def delete(self, space_id: SpaceId) -> None:
        self._store.pop(space_id.value, None)