from dataclasses import dataclass

from sigma_core.planning.domain.errors import DayNotFoundError
from sigma_core.planning.domain.ports.day_repository import DayRepository
from sigma_core.planning.domain.value_objects import BlockId, DayId


@dataclass
class RemoveBlockFromDayCommand:
    day_id: DayId
    block_id: BlockId


class RemoveBlockFromDay:
    def __init__(self, day_repo: DayRepository) -> None:
        self._day_repo = day_repo

    async def execute(self, cmd: RemoveBlockFromDayCommand) -> None:
        day = await self._day_repo.get_by_id(cmd.day_id)
        if day is None:
            raise DayNotFoundError(f"Day {cmd.day_id.value} not found")
        day.remove_block(cmd.block_id)
        await self._day_repo.save(day)
