from datetime import date

from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.value_objects import DateRange, DayId
from sigma_core.planning.infrastructure.firestore.mappers import (
    day_from_dict,
    day_to_dict,
    snapshot_data,
)
from sigma_core.shared_kernel.value_objects import SpaceId


class FirestoreDayRepository:
    """Adaptador Firestore para `DayRepository`.

    Índice compuesto requerido: `days` → `space_id + date`.
    """

    COLLECTION = "days"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    def _ref(self, day_id: str):
        return self._client.collection(self.COLLECTION).document(day_id)

    async def save(self, day: Day) -> None:
        await self._ref(day.id.value).set(day_to_dict(day))

    async def get_by_id(self, day_id: DayId) -> Day | None:
        doc = await self._ref(day_id.value).get()
        if not doc.exists:
            return None
        return day_from_dict(snapshot_data(doc))

    async def get_by_space_and_date(
        self, space_id: SpaceId, target_date: date
    ) -> Day | None:
        query = (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .where(filter=FieldFilter("date", "==", target_date.isoformat()))
            .limit(1)
        )
        docs = await query.get()
        if not docs:
            return None
        return day_from_dict(snapshot_data(docs[0]))

    async def list_by_space_and_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[Day]:
        query = (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .where(
                filter=FieldFilter("date", ">=", date_range.start.isoformat())
            )
            .where(
                filter=FieldFilter("date", "<=", date_range.end.isoformat())
            )
        )
        docs = await query.get()
        return [day_from_dict(snapshot_data(doc)) for doc in docs]

    async def delete(self, day_id: DayId) -> None:
        await self._ref(day_id.value).delete()
