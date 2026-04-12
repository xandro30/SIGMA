from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.value_objects import DayTemplateId
from sigma_core.shared_kernel.value_objects import SpaceId


class FakeDayTemplateRepository:
    def __init__(self) -> None:
        self._store: dict[str, DayTemplate] = {}

    async def save(self, template: DayTemplate) -> None:
        self._store[template.id.value] = template

    async def get_by_id(
        self, template_id: DayTemplateId
    ) -> DayTemplate | None:
        return self._store.get(template_id.value)

    async def list_by_space(self, space_id: SpaceId) -> list[DayTemplate]:
        return [t for t in self._store.values() if t.space_id == space_id]

    async def delete(self, template_id: DayTemplateId) -> None:
        self._store.pop(template_id.value, None)
