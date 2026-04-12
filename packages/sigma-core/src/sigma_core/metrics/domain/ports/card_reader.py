from __future__ import annotations

from typing import Protocol

from sigma_core.metrics.domain.value_objects import CardSnapshot
from sigma_core.planning.domain.value_objects import DateRange
from sigma_core.shared_kernel.value_objects import SpaceId


class MetricsCardReader(Protocol):
    async def list_completed_in_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[CardSnapshot]: ...
