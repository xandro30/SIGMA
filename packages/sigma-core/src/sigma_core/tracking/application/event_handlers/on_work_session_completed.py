"""Handler del evento WorkSessionCompleted — registra trabajo en la card."""
from __future__ import annotations

from sigma_core.shared_kernel.events import WorkSessionCompleted
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.value_objects import WorkLogEntry


class OnWorkSessionCompletedHandler:
    """Reacciona a una sesión completada añadiendo un WorkLogEntry a la card.

    Si la card no existe en el repositorio (baja, migración), ignora el evento
    sin lanzar excepción para no bloquear el flujo del tracking BC.
    """

    def __init__(self, card_repo: CardRepository) -> None:
        self._card_repo = card_repo

    async def __call__(self, event: WorkSessionCompleted) -> None:
        card = await self._card_repo.get_by_id(event.card_id)
        if card is None:
            return

        entry = WorkLogEntry(
            log=event.description,
            minutes=event.minutes,
            logged_at=event.occurred_at,
        )
        card.add_work_log(entry)
        await self._card_repo.save(card)
