from dataclasses import dataclass
from sigma_core.task_management.domain.errors import CardNotFoundError, AreaNotFoundError
from sigma_core.task_management.domain.value_objects import CardId, AreaId
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.ports.area_repository import AreaRepository


@dataclass
class AssignAreaCommand:
    card_id: CardId
    area_id: AreaId | None


class AssignArea:
    def __init__(self, card_repo: CardRepository, area_repo: AreaRepository) -> None:
        self._card_repo = card_repo
        self._area_repo = area_repo

    async def execute(self, cmd: AssignAreaCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        if cmd.area_id is not None:
            area = await self._area_repo.get_by_id(cmd.area_id)
            if area is None:
                raise AreaNotFoundError(cmd.area_id)

        card.area_id = cmd.area_id
        await self._card_repo.save(card)