from dataclasses import dataclass
from sigma_core.task_management.domain.aggregates.space import FINISH_STATE_ID
from sigma_core.task_management.domain.errors import (
    CardNotFoundError,
    InvalidTransitionError,
)
from sigma_core.shared_kernel.value_objects import CardId
from sigma_core.task_management.domain.ports.card_repository import CardRepository


@dataclass
class ArchiveCardCommand:
    card_id: CardId


class ArchiveCard:
    def __init__(self, card_repo: CardRepository) -> None:
        self._card_repo = card_repo

    async def execute(self, cmd: ArchiveCardCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        if card.workflow_state_id is None:
            raise InvalidTransitionError(
                "Card must be in workflow to be archived"
            )

        card.move_to_workflow_state(FINISH_STATE_ID)
        await self._card_repo.save(card)