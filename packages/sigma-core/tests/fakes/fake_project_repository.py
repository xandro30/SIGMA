from sigma_core.task_management.domain.entities.project import Project
from sigma_core.shared_kernel.value_objects import AreaId
from sigma_core.task_management.domain.value_objects import ProjectId


class FakeProjectRepository:
    def __init__(self) -> None:
        self._store: dict[str, Project] = {}

    async def save(self, project: Project) -> None:
        self._store[project.id.value] = project

    async def get_by_id(self, project_id: ProjectId) -> Project | None:
        return self._store.get(project_id.value)

    async def get_by_area(self, area_id: AreaId) -> list[Project]:
        return [p for p in self._store.values() if p.area_id == area_id]

    async def get_all(self) -> list[Project]:
        return list(self._store.values())

    async def delete(self, project_id: ProjectId) -> None:
        self._store.pop(project_id.value, None)