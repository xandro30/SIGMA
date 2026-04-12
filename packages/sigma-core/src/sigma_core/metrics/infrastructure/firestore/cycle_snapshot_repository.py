from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.metrics.domain.aggregates.cycle_snapshot import CycleSnapshot
from sigma_core.metrics.infrastructure.firestore.mappers import (
    cycle_snapshot_from_dict,
    cycle_snapshot_to_dict,
    snapshot_data,
)
from sigma_core.planning.domain.value_objects import CycleId


class FirestoreCycleSnapshotRepository:
    COLLECTION = "cycle_snapshots"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, snapshot: CycleSnapshot) -> None:
        await (
            self._client.collection(self.COLLECTION)
            .document(snapshot.id.value)
            .set(cycle_snapshot_to_dict(snapshot))
        )

    async def get_by_cycle_id(self, cycle_id: CycleId) -> CycleSnapshot | None:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("cycle_id", "==", cycle_id.value))
            .limit(1)
            .get()
        )
        if not docs:
            return None
        return cycle_snapshot_from_dict(snapshot_data(docs[0]))
