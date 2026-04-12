from dataclasses import dataclass

from sigma_core.task_management.domain.errors import CardNotFoundError
from sigma_core.shared_kernel.value_objects import CardId, Timestamp
from sigma_core.task_management.domain.ports.card_repository import CardRepository


@dataclass
class StopTimerCommand:
    card_id: CardId
    now: Timestamp


class StopTimer:
    def __init__(self, card_repo: CardRepository) -> None:
        self._card_repo = card_repo

    async def execute(self, cmd: StopTimerCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        card.stop_timer(cmd.now)
        await self._card_repo.save(card)
