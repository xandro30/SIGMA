from google.cloud.firestore import AsyncClient

from sigma_core.task_management.domain.aggregates.space import Space
from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.task_management.infrastructure.firestore.mappers import (
    space_to_dict, space_from_dict, snapshot_data,
)


class FirestoreSpaceRepository:
    COLLECTION = "spaces"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, space: Space) -> None:
        doc_ref = self._client.collection(self.COLLECTION).document(space.id.value)
        await doc_ref.set(space_to_dict(space))

    async def get_by_id(self, space_id: SpaceId) -> Space | None:
        doc = await self._client.collection(self.COLLECTION).document(space_id.value).get()
        if not doc.exists:
            return None
        return space_from_dict(snapshot_data(doc))

    async def get_all(self) -> list[Space]:
        docs = await self._client.collection(self.COLLECTION).get()
        return [space_from_dict(snapshot_data(doc)) for doc in docs]

    async def delete(self, space_id: SpaceId) -> None:
        await self._client.collection(self.COLLECTION).document(space_id.value).delete()