from dataclasses import dataclass

from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleType
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.value_objects import SpaceId


@dataclass
class CreateCycleCommand:
    space_id: SpaceId
    name: str
    date_range: DateRange
    cycle_type: CycleType = CycleType.SPRINT


class CreateCycle:
    def __init__(self, cycle_repo: CycleRepository) -> None:
        self._cycle_repo = cycle_repo

    async def execute(self, cmd: CreateCycleCommand) -> CycleId:
        cycle = Cycle(
            id=CycleId.generate(),
            space_id=cmd.space_id,
            name=cmd.name,
            date_range=cmd.date_range,
            cycle_type=cmd.cycle_type,
        )
        await self._cycle_repo.save(cycle)
        return cycle.id
