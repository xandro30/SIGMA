from dataclasses import dataclass

from sigma_core.planning.domain.errors import CycleNotFoundError
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.value_objects import CycleId
from sigma_core.shared_kernel.events import EventBus
from sigma_core.shared_kernel.value_objects import Timestamp


@dataclass
class CloseCycleCommand:
    cycle_id: CycleId
    now: Timestamp


class CloseCycle:
    """Cierra un Cycle y despacha los domain events acumulados.

    El Cycle emite ``CycleClosed`` en su metodo ``close()``. Este use case
    persiste el estado cerrado y luego despacha los eventos via ``EventBus``
    para que los handlers (ej: metrics) reaccionen.

    Si un handler falla, la excepcion propaga (fallo atomico). El Cycle
    ya esta cerrado en Firestore — retry manual si es necesario.
    """

    def __init__(
        self, cycle_repo: CycleRepository, event_bus: EventBus
    ) -> None:
        self._cycle_repo = cycle_repo
        self._event_bus = event_bus

    async def execute(self, cmd: CloseCycleCommand) -> None:
        cycle = await self._cycle_repo.get_by_id(cmd.cycle_id)
        if cycle is None:
            raise CycleNotFoundError(
                f"Cycle {cmd.cycle_id.value} not found"
            )
        cycle.close(cmd.now)
        await self._cycle_repo.save(cycle)
        for event in cycle.collect_events():
            await self._event_bus.publish(event)
