from dataclasses import dataclass

from sigma_core.planning.domain.errors import (
    CycleAlreadyActiveError,
    CycleNotFoundError,
)
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.value_objects import CycleId


@dataclass
class ActivateCycleCommand:
    cycle_id: CycleId


class ActivateCycle:
    """Activa un ciclo en estado DRAFT.

    Restriccion: un Space no puede tener mas de un ciclo ACTIVE **del
    mismo tipo** simultaneamente. Distintos tipos (sprint + quarter)
    pueden coexistir activos.
    """

    def __init__(self, cycle_repo: CycleRepository) -> None:
        self._cycle_repo = cycle_repo

    async def execute(self, cmd: ActivateCycleCommand) -> None:
        cycle = await self._cycle_repo.get_by_id(cmd.cycle_id)
        if cycle is None:
            raise CycleNotFoundError(
                f"Cycle {cmd.cycle_id.value} not found"
            )

        # Check for existing active cycle of the SAME type
        active = await self._cycle_repo.get_active_by_space(
            cycle.space_id, cycle.cycle_type
        )
        if active is not None and active.id != cycle.id:
            raise CycleAlreadyActiveError(
                space_id=cycle.space_id.value,
                active_cycle_id=active.id.value,
            )

        cycle.activate()
        await self._cycle_repo.save(cycle)
