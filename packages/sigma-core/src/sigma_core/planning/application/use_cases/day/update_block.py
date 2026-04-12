from dataclasses import dataclass

from sigma_core.planning.domain.aggregates.day import UNSET
from sigma_core.planning.domain.errors import DayNotFoundError
from sigma_core.planning.domain.ports.day_repository import DayRepository
from sigma_core.planning.domain.value_objects import BlockId, DayId
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, Timestamp


@dataclass
class UpdateBlockInDayCommand:
    day_id: DayId
    block_id: BlockId
    start_at: Timestamp | None
    duration: Minutes | None
    area_id_set: bool
    area_id: AreaId | None
    notes: str | None


class UpdateBlockInDay:
    """Actualiza parcialmente un bloque de un día.

    `area_id_set=True` permite distinguir "no tocar" (False) de "poner a None"
    (True con `area_id=None`).
    """

    def __init__(self, day_repo: DayRepository) -> None:
        self._day_repo = day_repo

    async def execute(self, cmd: UpdateBlockInDayCommand) -> None:
        day = await self._day_repo.get_by_id(cmd.day_id)
        if day is None:
            raise DayNotFoundError(f"Day {cmd.day_id.value} not found")
        day.update_block(
            cmd.block_id,
            start_at=cmd.start_at,
            duration=cmd.duration,
            area_id=cmd.area_id if cmd.area_id_set else UNSET,
            notes=cmd.notes,
        )
        await self._day_repo.save(day)
