"""Query para obtener el CycleSnapshot raw de un ciclo cerrado."""
from __future__ import annotations

from dataclasses import dataclass

from sigma_core.metrics.domain.aggregates.cycle_snapshot import CycleSnapshot
from sigma_core.metrics.domain.errors import CycleSnapshotNotFoundError
from sigma_core.metrics.domain.ports.cycle_snapshot_repository import (
    CycleSnapshotRepository,
)
from sigma_core.planning.domain.value_objects import CycleId


@dataclass
class GetSnapshotQuery:
    cycle_id: CycleId


class GetSnapshot:
    def __init__(self, snapshot_repo: CycleSnapshotRepository) -> None:
        self._snapshot_repo = snapshot_repo

    async def execute(self, query: GetSnapshotQuery) -> CycleSnapshot:
        snapshot = await self._snapshot_repo.get_by_cycle_id(query.cycle_id)
        if snapshot is None:
            raise CycleSnapshotNotFoundError(
                f"CycleSnapshot for cycle {query.cycle_id.value} not found"
            )
        return snapshot
