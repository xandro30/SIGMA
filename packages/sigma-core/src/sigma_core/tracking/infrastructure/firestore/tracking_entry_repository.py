"""Firestore repository para TrackingEntry."""
from __future__ import annotations

from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.tracking.domain.aggregates.tracking_entry import TrackingEntry
from sigma_core.tracking.infrastructure.firestore.mappers import (
    snapshot_data,
    tracking_entry_from_dict,
    tracking_entry_to_dict,
)


class FirestoreTrackingEntryRepository:
    COLLECTION = "tracking_entries"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    def _ref(self, entry_id: str):
        return self._client.collection(self.COLLECTION).document(entry_id)

    async def save(self, entry: TrackingEntry) -> None:
        await self._ref(entry.id.value).set(tracking_entry_to_dict(entry))

    async def list_by_space(self, space_id: SpaceId) -> list[TrackingEntry]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .get()
        )
        return [tracking_entry_from_dict(snapshot_data(doc)) for doc in docs]
