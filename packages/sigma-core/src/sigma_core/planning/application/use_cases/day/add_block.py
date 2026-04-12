from dataclasses import dataclass

from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.errors import DayNotFoundError
from sigma_core.planning.domain.ports.day_repository import DayRepository
from sigma_core.planning.domain.value_objects import BlockId, DayId
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, Timestamp


@dataclass
class AddBlockToDayCommand:
    day_id: DayId
    start_at: Timestamp
    duration: Minutes
    area_id: AreaId | None
    notes: str = ""


class AddBlockToDay:
    def __init__(self, day_repo: DayRepository) -> None:
        self._day_repo = day_repo

    async def execute(self, cmd: AddBlockToDayCommand) -> BlockId:
        day = await self._day_repo.get_by_id(cmd.day_id)
        if day is None:
            raise DayNotFoundError(f"Day {cmd.day_id.value} not found")
        block = TimeBlock(
            id=BlockId.generate(),
            start_at=cmd.start_at,
            duration=cmd.duration,
            area_id=cmd.area_id,
            notes=cmd.notes,
        )
        day.add_block(block)
        await self._day_repo.save(day)
        return block.id
