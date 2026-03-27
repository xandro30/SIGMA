from dataclasses import dataclass
from datetime import date
from sigma_core.task_management.domain.enums import Priority
from sigma_core.task_management.domain.errors import CardNotFoundError
from sigma_core.task_management.domain.value_objects import (
    CardId, CardTitle, AreaId, ProjectId, EpicId,
)
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.ports.area_repository import AreaRepository
from sigma_core.task_management.domain.ports.project_repository import ProjectRepository
from sigma_core.task_management.domain.ports.epic_repository import EpicRepository


@dataclass
class UpdateCardCommand:
    card_id: CardId
    title: CardTitle | None = None
    description: str | None = None
    priority: Priority | None = None
    due_date: date | None = None


class UpdateCard:
    def __init__(self, card_repo: CardRepository) -> None:
        self._card_repo = card_repo

    async def execute(self, cmd: UpdateCardCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        if cmd.title is not None:
            card.title = cmd.title
        if cmd.description is not None:
            card.description = cmd.description
        if cmd.priority is not None:
            card.priority = cmd.priority
        if cmd.due_date is not None:
            card.due_date = cmd.due_date

        await self._card_repo.save(card)