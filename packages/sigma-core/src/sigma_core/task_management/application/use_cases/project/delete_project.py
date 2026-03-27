from dataclasses import dataclass
from sigma_core.task_management.domain.errors import ProjectNotFoundError
from sigma_core.task_management.domain.value_objects import ProjectId
from sigma_core.task_management.domain.ports.project_repository import ProjectRepository
from sigma_core.task_management.domain.ports.card_repository import CardRepository


@dataclass
class DeleteProjectCommand:
    project_id: ProjectId


class DeleteProject:
    def __init__(
        self,
        project_repo: ProjectRepository,
        card_repo: CardRepository,
    ) -> None:
        self._project_repo = project_repo
        self._card_repo = card_repo

    async def execute(self, cmd: DeleteProjectCommand) -> None:
        project = await self._project_repo.get_by_id(cmd.project_id)
        if project is None:
            raise ProjectNotFoundError(cmd.project_id)

        cards = await self._card_repo.get_by_project(cmd.project_id)
        for card in cards:
            card.project_id = None
            await self._card_repo.save(card)

        await self._project_repo.delete(cmd.project_id)