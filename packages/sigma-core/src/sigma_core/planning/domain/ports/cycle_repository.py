from typing import Protocol

from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleType
from sigma_core.planning.domain.value_objects import CycleId
from sigma_core.shared_kernel.value_objects import SpaceId


class CycleRepository(Protocol):
    async def save(self, cycle: Cycle) -> None: ...

    async def get_by_id(self, cycle_id: CycleId) -> Cycle | None: ...

    async def get_active_by_space(
        self, space_id: SpaceId, cycle_type: CycleType | None = None
    ) -> Cycle | None:
        """If cycle_type is None, returns any active cycle (backward compat).
        If cycle_type is given, returns the active cycle of that type only."""
        ...

    async def list_active_by_space(self, space_id: SpaceId) -> list[Cycle]:
        """Returns all active cycles of any type for the space."""
        ...

    async def list_by_space(self, space_id: SpaceId) -> list[Cycle]: ...

    async def delete(self, cycle_id: CycleId) -> None: ...
