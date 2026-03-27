from dataclasses import dataclass
from sigma_core.task_management.domain.errors import CardNotFoundError
from sigma_core.task_management.domain.value_objects import CardId
from sigma_core.task_management.domain.ports.card_repository import CardRepository


@dataclass
class DeleteCardCommand:
    card_id: CardId


class DeleteCard:
    def __init__(self, card_repo: CardRepository) -> None:
        self._card_repo = card_repo

    async def execute(self, cmd: DeleteCardCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        await self._card_repo.delete(cmd.card_id)