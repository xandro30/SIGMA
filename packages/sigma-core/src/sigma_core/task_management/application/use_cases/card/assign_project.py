from dataclasses import dataclass
from sigma_core.task_management.domain.errors import (
    CardNotFoundError,
    ProjectNotFoundError,
)
from sigma_core.shared_kernel.value_objects import CardId
from sigma_core.task_management.domain.value_objects import ProjectId
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.ports.project_repository import ProjectRepository


@dataclass
class AssignProjectCommand:
    card_id: CardId
    project_id: ProjectId | None


class AssignProject:
    def __init__(self, card_repo: CardRepository,project_repo: ProjectRepository) -> None:
        self._card_repo = card_repo
        self._project_repo = project_repo

    async def execute(self, cmd: AssignProjectCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        if cmd.project_id is not None:
            project = await self._project_repo.get_by_id(cmd.project_id)
            if project is None:
                raise ProjectNotFoundError(cmd.project_id)
            card.project_id = cmd.project_id
            card.area_id = project.area_id
        else:
            card.project_id = None

        await self._card_repo.save(card)