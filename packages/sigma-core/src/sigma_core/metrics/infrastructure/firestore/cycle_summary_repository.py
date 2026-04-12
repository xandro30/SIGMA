from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.metrics.domain.aggregates.cycle_summary import CycleSummary
from sigma_core.metrics.infrastructure.firestore.mappers import (
    cycle_summary_from_dict,
    cycle_summary_to_dict,
    snapshot_data,
)
from sigma_core.planning.domain.value_objects import CycleId


class FirestoreCycleSummaryRepository:
    COLLECTION = "cycle_summaries"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, summary: CycleSummary) -> None:
        await (
            self._client.collection(self.COLLECTION)
            .document(summary.id.value)
            .set(cycle_summary_to_dict(summary))
        )

    async def get_by_cycle_id(self, cycle_id: CycleId) -> CycleSummary | None:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("cycle_id", "==", cycle_id.value))
            .limit(1)
            .get()
        )
        if not docs:
            return None
        return cycle_summary_from_dict(snapshot_data(docs[0]))
