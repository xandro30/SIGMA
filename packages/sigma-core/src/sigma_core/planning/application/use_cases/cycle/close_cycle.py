from dataclasses import dataclass

from sigma_core.planning.domain.errors import CycleNotFoundError
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.value_objects import CycleId
from sigma_core.shared_kernel.value_objects import Timestamp


@dataclass
class CloseCycleCommand:
    cycle_id: CycleId
    now: Timestamp


class CloseCycle:
    def __init__(self, cycle_repo: CycleRepository) -> None:
        self._cycle_repo = cycle_repo

    async def execute(self, cmd: CloseCycleCommand) -> None:
        cycle = await self._cycle_repo.get_by_id(cmd.cycle_id)
        if cycle is None:
            raise CycleNotFoundError(
                f"Cycle {cmd.cycle_id.value} not found"
            )
        cycle.close(cmd.now)
        await self._cycle_repo.save(cycle)
