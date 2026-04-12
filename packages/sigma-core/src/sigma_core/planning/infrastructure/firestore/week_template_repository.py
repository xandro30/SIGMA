from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.value_objects import WeekTemplateId
from sigma_core.planning.infrastructure.firestore.mappers import (
    snapshot_data,
    week_template_from_dict,
    week_template_to_dict,
)
from sigma_core.shared_kernel.value_objects import SpaceId


class FirestoreWeekTemplateRepository:
    """Adaptador Firestore para `WeekTemplateRepository`.

    Índice requerido: `week_templates` → `space_id` para `list_by_space`.
    """

    COLLECTION = "week_templates"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    def _ref(self, template_id: str):
        return self._client.collection(self.COLLECTION).document(template_id)

    async def save(self, template: WeekTemplate) -> None:
        await self._ref(template.id.value).set(week_template_to_dict(template))

    async def get_by_id(
        self, template_id: WeekTemplateId
    ) -> WeekTemplate | None:
        doc = await self._ref(template_id.value).get()
        if not doc.exists:
            return None
        return week_template_from_dict(snapshot_data(doc))

    async def list_by_space(self, space_id: SpaceId) -> list[WeekTemplate]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .get()
        )
        return [week_template_from_dict(snapshot_data(doc)) for doc in docs]

    async def delete(self, template_id: WeekTemplateId) -> None:
        await self._ref(template_id.value).delete()
