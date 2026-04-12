from google.cloud.firestore import AsyncClient

from sigma_core.task_management.domain.entities.area import Area
from sigma_core.shared_kernel.value_objects import AreaId
from sigma_core.task_management.infrastructure.firestore.mappers import (
    area_to_dict, area_from_dict, snapshot_data,
)


class FirestoreAreaRepository:
    COLLECTION = "areas"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, area: Area) -> None:
        await self._client.collection(self.COLLECTION).document(area.id.value).set(area_to_dict(area))

    async def get_by_id(self, area_id: AreaId) -> Area | None:
        doc = await self._client.collection(self.COLLECTION).document(area_id.value).get()
        if not doc.exists:
            return None
        return area_from_dict(snapshot_data(doc))

    async def get_all(self) -> list[Area]:
        docs = await self._client.collection(self.COLLECTION).get()
        return [area_from_dict(snapshot_data(doc)) for doc in docs]

    async def delete(self, area_id: AreaId) -> None:
        await self._client.collection(self.COLLECTION).document(area_id.value).delete()
