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
    """
    Activa un ciclo en estado DRAFT.

    Enforcement a nivel de use case: un Space no puede tener más de un
    ciclo ACTIVE simultáneo. Si ya existe otro ciclo activo en el mismo
    Space, se lanza `CycleAlreadyActiveError`.
    """

    def __init__(self, cycle_repo: CycleRepository) -> None:
        self._cycle_repo = cycle_repo

    async def execute(self, cmd: ActivateCycleCommand) -> None:
        cycle = await self._cycle_repo.get_by_id(cmd.cycle_id)
        if cycle is None:
            raise CycleNotFoundError(
                f"Cycle {cmd.cycle_id.value} not found"
            )

        active = await self._cycle_repo.get_active_by_space(cycle.space_id)
        if active is not None and active.id != cycle.id:
            raise CycleAlreadyActiveError(
                space_id=cycle.space_id.value,
                active_cycle_id=active.id.value,
            )

        cycle.activate()
        await self._cycle_repo.save(cycle)
