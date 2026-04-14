from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.tracking.domain.aggregates.work_session import WorkSession


class FakeWorkSessionRepository:
    def __init__(self) -> None:
        self._store: dict[str, WorkSession] = {}

    async def save(self, session: WorkSession) -> None:
        self._store[session.space_id.value] = session

    async def get_by_space(self, space_id: SpaceId) -> WorkSession | None:
        return self._store.get(space_id.value)

    async def delete(self, space_id: SpaceId) -> None:
        self._store.pop(space_id.value, None)
