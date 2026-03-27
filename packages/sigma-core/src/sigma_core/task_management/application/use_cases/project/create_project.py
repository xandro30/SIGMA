from dataclasses import dataclass
from sigma_core.task_management.domain.entities.project import Project
from sigma_core.task_management.domain.enums import ProjectStatus
from sigma_core.task_management.domain.errors import AreaNotFoundError
from sigma_core.task_management.domain.value_objects import ProjectId, AreaId
from sigma_core.task_management.domain.ports.project_repository import ProjectRepository
from sigma_core.task_management.domain.ports.area_repository import AreaRepository


@dataclass
class CreateProjectCommand:
    name: str
    area_id: AreaId


class CreateProject:
    def __init__(self, project_repo: ProjectRepository, area_repo: AreaRepository) -> None:
        self._project_repo = project_repo
        self._area_repo = area_repo

    async def execute(self, cmd: CreateProjectCommand) -> ProjectId:
        area = await self._area_repo.get_by_id(cmd.area_id)
        if area is None:
            raise AreaNotFoundError(cmd.area_id)

        project = Project(
            id=ProjectId.generate(),
            name=cmd.name,
            area_id=cmd.area_id,
            status=ProjectStatus.ACTIVE,
        )
        await self._project_repo.save(project)
        return project.id