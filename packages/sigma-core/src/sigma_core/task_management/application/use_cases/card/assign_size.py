from dataclasses import dataclass

from sigma_core.shared_kernel.enums import CardSize
from sigma_core.task_management.domain.errors import CardNotFoundError
from sigma_core.shared_kernel.value_objects import CardId
from sigma_core.task_management.domain.ports.card_repository import CardRepository


@dataclass
class AssignSizeCommand:
    card_id: CardId
    size: CardSize | None


class AssignSize:
    def __init__(self, card_repo: CardRepository) -> None:
        self._card_repo = card_repo

    async def execute(self, cmd: AssignSizeCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        card.assign_size(cmd.size)
        await self._card_repo.save(card)
