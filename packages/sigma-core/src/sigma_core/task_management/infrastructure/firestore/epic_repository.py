from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.task_management.domain.entities.epic import Epic
from sigma_core.task_management.domain.value_objects import EpicId, SpaceId, ProjectId
from sigma_core.task_management.infrastructure.firestore.mappers import (
    epic_to_dict, epic_from_dict,
)


class FirestoreEpicRepository:
    COLLECTION = "epics"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, epic: Epic) -> None:
        await self._client.collection(self.COLLECTION).document(epic.id.value).set(epic_to_dict(epic))

    async def get_by_id(self, epic_id: EpicId) -> Epic | None:
        doc = await self._client.collection(self.COLLECTION).document(epic_id.value).get()
        if not doc.exists:
            return None
        return epic_from_dict(doc.to_dict())

    async def get_by_space(self, space_id: SpaceId) -> list[Epic]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .get()
        )
        return [epic_from_dict(doc.to_dict()) for doc in docs]

    async def get_by_project(self, project_id: ProjectId) -> list[Epic]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("project_id", "==", project_id.value))
            .get()
        )
        return [epic_from_dict(doc.to_dict()) for doc in docs]

    async def delete(self, epic_id: EpicId) -> None:
        await self._client.collection(self.COLLECTION).document(epic_id.value).delete()