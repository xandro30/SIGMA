from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.value_objects import DayTemplateId
from sigma_core.planning.infrastructure.firestore.mappers import (
    day_template_from_dict,
    day_template_to_dict,
    snapshot_data,
)
from sigma_core.shared_kernel.value_objects import SpaceId


class FirestoreDayTemplateRepository:
    """Adaptador Firestore para `DayTemplateRepository`.

    Índice requerido: `day_templates` → `space_id` para `list_by_space`.
    """

    COLLECTION = "day_templates"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    def _ref(self, template_id: str):
        return self._client.collection(self.COLLECTION).document(template_id)

    async def save(self, template: DayTemplate) -> None:
        await self._ref(template.id.value).set(day_template_to_dict(template))

    async def get_by_id(
        self, template_id: DayTemplateId
    ) -> DayTemplate | None:
        doc = await self._ref(template_id.value).get()
        if not doc.exists:
            return None
        return day_template_from_dict(snapshot_data(doc))

    async def list_by_space(self, space_id: SpaceId) -> list[DayTemplate]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .get()
        )
        return [day_template_from_dict(snapshot_data(doc)) for doc in docs]

    async def delete(self, template_id: DayTemplateId) -> None:
        await self._ref(template_id.value).delete()
