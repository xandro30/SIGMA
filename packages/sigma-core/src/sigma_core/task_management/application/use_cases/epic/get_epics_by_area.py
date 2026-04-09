import asyncio
from dataclasses import dataclass

from sigma_core.task_management.domain.entities.epic import Epic
from sigma_core.task_management.domain.value_objects import AreaId
from sigma_core.task_management.domain.ports.project_repository import ProjectRepository
from sigma_core.task_management.domain.ports.epic_repository import EpicRepository


@dataclass
class GetEpicsByAreaQuery:
    area_id: AreaId


class GetEpicsByArea:
    def __init__(self, project_repo: ProjectRepository, epic_repo: EpicRepository) -> None:
        self._project_repo = project_repo
        self._epic_repo = epic_repo

    async def execute(self, query: GetEpicsByAreaQuery) -> list[Epic]:
        projects = await self._project_repo.get_by_area(query.area_id)
        if not projects:
            return []
        epics_per_project = await asyncio.gather(
            *[self._epic_repo.get_by_project(p.id) for p in projects]
        )
        return [epic for epics in epics_per_project for epic in epics]
