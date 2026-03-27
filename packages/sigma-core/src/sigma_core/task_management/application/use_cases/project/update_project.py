from dataclasses import dataclass
from sigma_core.task_management.domain.enums import ProjectStatus
from sigma_core.task_management.domain.errors import ProjectNotFoundError
from sigma_core.task_management.domain.value_objects import ProjectId
from sigma_core.task_management.domain.ports.project_repository import ProjectRepository


@dataclass
class UpdateProjectCommand:
    project_id: ProjectId
    name: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None


class UpdateProject:
    def __init__(self, project_repo: ProjectRepository) -> None:
        self._project_repo = project_repo

    async def execute(self, cmd: UpdateProjectCommand) -> None:
        project = await self._project_repo.get_by_id(cmd.project_id)
        if project is None:
            raise ProjectNotFoundError(cmd.project_id)

        if cmd.name is not None:
            project.rename(cmd.name)
        if cmd.description is not None:
            project.update_description(cmd.description)
        if cmd.status is not None:
            project.change_status(cmd.status)

        await self._project_repo.save(project)