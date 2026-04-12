from dataclasses import dataclass

from sigma_core.planning.domain.errors import CycleNotFoundError
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.value_objects import CycleId
from sigma_core.shared_kernel.value_objects import AreaId


@dataclass
class RemoveAreaBudgetCommand:
    cycle_id: CycleId
    area_id: AreaId


class RemoveAreaBudget:
    """Elimina el presupuesto asignado a un area dentro de un ciclo.

    Si el area no tenia presupuesto, el agregado lanza `BudgetNotFoundError`.
    """

    def __init__(self, cycle_repo: CycleRepository) -> None:
        self._cycle_repo = cycle_repo

    async def execute(self, cmd: RemoveAreaBudgetCommand) -> None:
        cycle = await self._cycle_repo.get_by_id(cmd.cycle_id)
        if cycle is None:
            raise CycleNotFoundError(
                f"Cycle {cmd.cycle_id.value} not found"
            )
        cycle.remove_area_budget(cmd.area_id)
        await self._cycle_repo.save(cycle)
