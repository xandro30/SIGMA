from dataclasses import dataclass
from sigma_core.task_management.domain.errors import (
    CardNotFoundError, EpicNotFoundError, InvalidEpicSpaceError,
)
from sigma_core.task_management.domain.value_objects import CardId, EpicId
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.ports.epic_repository import EpicRepository


@dataclass
class AssignEpicCommand:
    card_id: CardId
    epic_id: EpicId | None


class AssignEpic:
    def __init__(self, card_repo: CardRepository, epic_repo: EpicRepository) -> None:
        self._card_repo = card_repo
        self._epic_repo = epic_repo

    async def execute(self, cmd: AssignEpicCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        if cmd.epic_id is not None:
            epic = await self._epic_repo.get_by_id(cmd.epic_id)
            if epic is None:
                raise EpicNotFoundError(cmd.epic_id)
            if epic.space_id != card.space_id:
                raise InvalidEpicSpaceError(
                    "Epic belongs to a different Space"
                )
            card.epic_id = cmd.epic_id
        else:
            card.epic_id = None

        await self._card_repo.save(card)