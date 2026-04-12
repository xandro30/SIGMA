from dataclasses import dataclass

from sigma_core.planning.domain.errors import CycleNotFoundError
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.value_objects import CycleId
from sigma_core.shared_kernel.value_objects import AreaId, Minutes


@dataclass
class SetAreaBudgetCommand:
    cycle_id: CycleId
    area_id: AreaId
    minutes: Minutes


class SetAreaBudget:
    """Fija o actualiza el presupuesto de minutos de un area dentro de un ciclo."""

    def __init__(self, cycle_repo: CycleRepository) -> None:
        self._cycle_repo = cycle_repo

    async def execute(self, cmd: SetAreaBudgetCommand) -> None:
        cycle = await self._cycle_repo.get_by_id(cmd.cycle_id)
        if cycle is None:
            raise CycleNotFoundError(
                f"Cycle {cmd.cycle_id.value} not found"
            )
        cycle.set_area_budget(cmd.area_id, cmd.minutes)
        await self._cycle_repo.save(cycle)
