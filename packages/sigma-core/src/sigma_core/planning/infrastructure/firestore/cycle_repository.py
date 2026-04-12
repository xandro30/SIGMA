from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleState
from sigma_core.planning.domain.value_objects import CycleId
from sigma_core.planning.infrastructure.firestore.mappers import (
    cycle_from_dict,
    cycle_to_dict,
    snapshot_data,
)
from sigma_core.shared_kernel.value_objects import SpaceId


class FirestoreCycleRepository:
    """Adaptador Firestore para `CycleRepository`.

    Índice compuesto requerido: `cycles` → `space_id + state` para
    `get_active_by_space` (ADR-002: un único cycle activo por space).
    """

    COLLECTION = "cycles"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    def _ref(self, cycle_id: str):
        return self._client.collection(self.COLLECTION).document(cycle_id)

    async def save(self, cycle: Cycle) -> None:
        await self._ref(cycle.id.value).set(cycle_to_dict(cycle))

    async def get_by_id(self, cycle_id: CycleId) -> Cycle | None:
        doc = await self._ref(cycle_id.value).get()
        if not doc.exists:
            return None
        return cycle_from_dict(snapshot_data(doc))

    async def get_active_by_space(self, space_id: SpaceId) -> Cycle | None:
        query = (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .where(filter=FieldFilter("state", "==", CycleState.ACTIVE.value))
            .limit(1)
        )
        docs = await query.get()
        if not docs:
            return None
        return cycle_from_dict(snapshot_data(docs[0]))

    async def list_by_space(self, space_id: SpaceId) -> list[Cycle]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .get()
        )
        return [cycle_from_dict(snapshot_data(doc)) for doc in docs]

    async def delete(self, cycle_id: CycleId) -> None:
        await self._ref(cycle_id.value).delete()
