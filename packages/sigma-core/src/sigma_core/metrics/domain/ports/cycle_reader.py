from __future__ import annotations

from typing import Protocol

from sigma_core.metrics.domain.value_objects import CycleView
from sigma_core.planning.domain.value_objects import CycleId
from sigma_core.shared_kernel.value_objects import SpaceId


class MetricsCycleReader(Protocol):
    async def get_by_id(self, cycle_id: CycleId) -> CycleView | None: ...

    async def get_active_by_space(self, space_id: SpaceId) -> CycleView | None: ...
