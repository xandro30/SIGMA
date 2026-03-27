from dataclasses import dataclass
from sigma_core.task_management.domain.entities.epic import Epic
from sigma_core.task_management.domain.errors import ProjectNotFoundError
from sigma_core.task_management.domain.value_objects import EpicId, SpaceId, ProjectId
from sigma_core.task_management.domain.ports.epic_repository import EpicRepository
from sigma_core.task_management.domain.ports.project_repository import ProjectRepository


@dataclass
class CreateEpicCommand:
    space_id: SpaceId
    project_id: ProjectId
    name: str
    description: str | None = None


class CreateEpic:
    def __init__(self, epic_repo: EpicRepository, project_repo: ProjectRepository) -> None:
        self._epic_repo = epic_repo
        self._project_repo = project_repo

    async def execute(self, cmd: CreateEpicCommand) -> EpicId:
        project = await self._project_repo.get_by_id(cmd.project_id)
        if project is None:
            raise ProjectNotFoundError(cmd.project_id)

        epic = Epic(
            id=EpicId.generate(),
            space_id=cmd.space_id,
            project_id=cmd.project_id,
            area_id=project.area_id,
            name=cmd.name,
            description=cmd.description,
        )
        await self._epic_repo.save(epic)
        return epic.id