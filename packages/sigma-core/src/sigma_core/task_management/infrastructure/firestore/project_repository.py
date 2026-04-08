from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.task_management.domain.entities.project import Project
from sigma_core.task_management.domain.value_objects import ProjectId, AreaId
from sigma_core.task_management.infrastructure.firestore.mappers import (
    project_to_dict, project_from_dict,
)


class FirestoreProjectRepository:
    COLLECTION = "projects"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save(self, project: Project) -> None:
        await self._client.collection(self.COLLECTION).document(project.id.value).set(project_to_dict(project))

    async def get_by_id(self, project_id: ProjectId) -> Project | None:
        doc = await self._client.collection(self.COLLECTION).document(project_id.value).get()
        if not doc.exists:
            return None
        return project_from_dict(doc.to_dict())

    async def get_by_area(self, area_id: AreaId) -> list[Project]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("area_id", "==", area_id.value))
            .get()
        )
        return [project_from_dict(doc.to_dict()) for doc in docs]

    async def get_all(self) -> list[Project]:
        docs = await self._client.collection(self.COLLECTION).get()
        return [project_from_dict(doc.to_dict()) for doc in docs]

    async def delete(self, project_id: ProjectId) -> None:
        await self._client.collection(self.COLLECTION).document(project_id.value).delete()
