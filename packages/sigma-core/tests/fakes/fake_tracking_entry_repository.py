from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.tracking.domain.aggregates.tracking_entry import TrackingEntry


class FakeTrackingEntryRepository:
    def __init__(self) -> None:
        self._store: list[TrackingEntry] = []

    async def save(self, entry: TrackingEntry) -> None:
        self._store.append(entry)

    async def list_by_space(self, space_id: SpaceId) -> list[TrackingEntry]:
        return [e for e in self._store if e.space_id == space_id]
