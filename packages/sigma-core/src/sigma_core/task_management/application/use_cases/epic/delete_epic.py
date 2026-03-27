from dataclasses import dataclass
from sigma_core.task_management.domain.errors import EpicNotFoundError
from sigma_core.task_management.domain.value_objects import EpicId
from sigma_core.task_management.domain.ports.epic_repository import EpicRepository
from sigma_core.task_management.domain.ports.card_repository import CardRepository


@dataclass
class DeleteEpicCommand:
    epic_id: EpicId


class DeleteEpic:
    def __init__(self, epic_repo: EpicRepository, card_repo: CardRepository) -> None:
        self._epic_repo = epic_repo
        self._card_repo = card_repo

    async def execute(self, cmd: DeleteEpicCommand) -> None:
        epic = await self._epic_repo.get_by_id(cmd.epic_id)
        if epic is None:
            raise EpicNotFoundError(cmd.epic_id)

        cards = await self._card_repo.get_by_epic(cmd.epic_id)
        for card in cards:
            card.epic_id = None
            await self._card_repo.save(card)

        await self._epic_repo.delete(cmd.epic_id)