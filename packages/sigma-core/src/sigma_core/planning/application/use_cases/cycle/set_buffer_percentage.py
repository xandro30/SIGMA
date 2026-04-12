from dataclasses import dataclass

from sigma_core.planning.domain.errors import CycleNotFoundError
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.value_objects import CycleId


@dataclass
class SetBufferPercentageCommand:
    cycle_id: CycleId
    percentage: int


class SetBufferPercentage:
    """Ajusta el buffer de imprevistos del ciclo (0..100)."""

    def __init__(self, cycle_repo: CycleRepository) -> None:
        self._cycle_repo = cycle_repo

    async def execute(self, cmd: SetBufferPercentageCommand) -> None:
        cycle = await self._cycle_repo.get_by_id(cmd.cycle_id)
        if cycle is None:
            raise CycleNotFoundError(
                f"Cycle {cmd.cycle_id.value} not found"
            )
        cycle.set_buffer_percentage(cmd.percentage)
        await self._cycle_repo.save(cycle)
