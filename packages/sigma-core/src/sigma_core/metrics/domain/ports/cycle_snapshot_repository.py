from __future__ import annotations

from typing import Protocol

from sigma_core.metrics.domain.aggregates.cycle_snapshot import CycleSnapshot
from sigma_core.planning.domain.value_objects import CycleId


class CycleSnapshotRepository(Protocol):
    async def save(self, snapshot: CycleSnapshot) -> None: ...

    async def get_by_cycle_id(self, cycle_id: CycleId) -> CycleSnapshot | None: ...
