from __future__ import annotations

from typing import Protocol

from sigma_core.metrics.domain.aggregates.cycle_summary import CycleSummary
from sigma_core.planning.domain.value_objects import CycleId


class CycleSummaryRepository(Protocol):
    async def save(self, summary: CycleSummary) -> None: ...

    async def get_by_cycle_id(self, cycle_id: CycleId) -> CycleSummary | None: ...
