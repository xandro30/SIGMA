from dataclasses import dataclass

from sigma_core.task_management.domain.errors import (
    CardNotFoundError,
    SpaceHasActiveTimerError,
)
from sigma_core.shared_kernel.value_objects import CardId, Timestamp
from sigma_core.task_management.domain.ports.card_repository import CardRepository


@dataclass
class StartTimerCommand:
    card_id: CardId
    now: Timestamp


class StartTimer:
    """
    Inicia el timer de una card.

    Invariantes:
    - TimerAlreadyRunningError: la propia card ya tiene un timer corriendo
      (validado en el agregado Card.start_timer).
    - SpaceHasActiveTimerError: otra card del mismo Space ya tiene un timer
      activo (máximo 1 timer activo por Space).
    """

    def __init__(self, card_repo: CardRepository) -> None:
        self._card_repo = card_repo

    async def execute(self, cmd: StartTimerCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        space_cards = await self._card_repo.get_by_space(card.space_id)
        for other in space_cards:
            if other.id == card.id:
                continue
            if other.timer_started_at is not None:
                raise SpaceHasActiveTimerError(
                    space_id=card.space_id.value,
                    active_card_id=other.id.value,
                )

        card.start_timer(cmd.now)
        await self._card_repo.save(card)
