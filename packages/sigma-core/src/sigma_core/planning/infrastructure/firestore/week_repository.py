from google.cloud.firestore import AsyncClient

from sigma_core.planning.domain.aggregates.week import Week
from sigma_core.planning.domain.value_objects import WeekId
from sigma_core.planning.infrastructure.firestore.mappers import (
    snapshot_data,
    week_from_dict,
    week_to_dict,
)


class FirestoreWeekRepository:
    """Persistencia de ``Week`` en Firestore.

    Cada documento se almacena con ``week.id.value`` como ``document_id``,
    que es determinista (``WeekId.for_space_and_week_start``). Esto hace
    que ``save`` sea idempotente por definición: dos writers concurrentes
    escriben el mismo documento y el segundo sobrescribe el primero con
    el mismo contenido.
    """

    COLLECTION = "weeks"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    def _doc_ref(self, week_id: str):
        return self._client.collection(self.COLLECTION).document(week_id)

    async def save(self, week: Week) -> None:
        await self._doc_ref(week.id.value).set(week_to_dict(week))

    async def get_by_id(self, week_id: WeekId) -> Week | None:
        doc = await self._doc_ref(week_id.value).get()
        if not doc.exists:
            return None
        return week_from_dict(snapshot_data(doc))

    async def delete(self, week_id: WeekId) -> None:
        await self._doc_ref(week_id.value).delete()
