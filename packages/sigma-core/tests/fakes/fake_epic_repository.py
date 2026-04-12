from sigma_core.task_management.domain.entities.epic import Epic
from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId


class FakeEpicRepository:
    def __init__(self) -> None:
        self._store: dict[str, Epic] = {}

    async def save(self, epic: Epic) -> None:
        self._store[epic.id.value] = epic

    async def get_by_id(self, epic_id: EpicId) -> Epic | None:
        return self._store.get(epic_id.value)

    async def get_by_space(self, space_id: SpaceId) -> list[Epic]:
        return [e for e in self._store.values() if e.space_id == space_id]

    async def get_by_project(self, project_id: ProjectId) -> list[Epic]:
        return [e for e in self._store.values() if e.project_id == project_id]

    async def delete(self, epic_id: EpicId) -> None:
        self._store.pop(epic_id.value, None)