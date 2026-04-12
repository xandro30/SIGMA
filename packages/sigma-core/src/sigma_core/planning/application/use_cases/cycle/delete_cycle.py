from dataclasses import dataclass

from sigma_core.planning.domain.enums import CycleState
from sigma_core.planning.domain.errors import (
    CycleNotFoundError,
    InvalidCycleTransitionError,
)
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.value_objects import CycleId


@dataclass
class DeleteCycleCommand:
    cycle_id: CycleId


class DeleteCycle:
    """Borra un ciclo. Solo permitido en estado DRAFT."""

    def __init__(self, cycle_repo: CycleRepository) -> None:
        self._cycle_repo = cycle_repo

    async def execute(self, cmd: DeleteCycleCommand) -> None:
        cycle = await self._cycle_repo.get_by_id(cmd.cycle_id)
        if cycle is None:
            raise CycleNotFoundError(
                f"Cycle {cmd.cycle_id.value} not found"
            )
        if cycle.state != CycleState.DRAFT:
            raise InvalidCycleTransitionError(
                from_state=cycle.state.value,
                to_state="deleted",
            )
        await self._cycle_repo.delete(cmd.cycle_id)
