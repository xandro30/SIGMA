from dataclasses import dataclass
from datetime import datetime, timezone

from sigma_core.task_management.domain.errors import CardNotFoundError
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.value_objects import WorkLogEntry
from sigma_core.shared_kernel.value_objects import CardId, Timestamp


@dataclass
class AddWorkLogEntryCommand:
    card_id: CardId
    description: str
    minutes: int


class AddWorkLogEntry:
    def __init__(self, card_repo: CardRepository) -> None:
        self._card_repo = card_repo

    async def execute(self, cmd: AddWorkLogEntryCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)
        entry = WorkLogEntry(
            log=cmd.description,
            minutes=cmd.minutes,
            logged_at=Timestamp(datetime.now(timezone.utc)),
        )
        card.add_work_log(entry)
        await self._card_repo.save(card)
