from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleState
from sigma_core.planning.domain.value_objects import CycleId
from sigma_core.shared_kernel.value_objects import SpaceId


class FakeCycleRepository:
    def __init__(self) -> None:
        self._store: dict[str, Cycle] = {}

    async def save(self, cycle: Cycle) -> None:
        self._store[cycle.id.value] = cycle

    async def get_by_id(self, cycle_id: CycleId) -> Cycle | None:
        return self._store.get(cycle_id.value)

    async def get_active_by_space(self, space_id: SpaceId) -> Cycle | None:
        for c in self._store.values():
            if c.space_id == space_id and c.state == CycleState.ACTIVE:
                return c
        return None

    async def list_by_space(self, space_id: SpaceId) -> list[Cycle]:
        return [c for c in self._store.values() if c.space_id == space_id]

    async def delete(self, cycle_id: CycleId) -> None:
        self._store.pop(cycle_id.value, None)
