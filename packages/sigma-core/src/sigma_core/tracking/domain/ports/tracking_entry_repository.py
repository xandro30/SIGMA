"""Port: TrackingEntryRepository."""
from __future__ import annotations

from typing import Protocol

from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.tracking.domain.aggregates.tracking_entry import TrackingEntry


class TrackingEntryRepository(Protocol):
    async def save(self, entry: TrackingEntry) -> None: ...
    async def list_by_space(self, space_id: SpaceId) -> list[TrackingEntry]: ...
