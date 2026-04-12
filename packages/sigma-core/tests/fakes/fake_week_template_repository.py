from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.value_objects import WeekTemplateId
from sigma_core.shared_kernel.value_objects import SpaceId


class FakeWeekTemplateRepository:
    def __init__(self) -> None:
        self._store: dict[str, WeekTemplate] = {}

    async def save(self, template: WeekTemplate) -> None:
        self._store[template.id.value] = template

    async def get_by_id(
        self, template_id: WeekTemplateId
    ) -> WeekTemplate | None:
        return self._store.get(template_id.value)

    async def list_by_space(self, space_id: SpaceId) -> list[WeekTemplate]:
        return [t for t in self._store.values() if t.space_id == space_id]

    async def delete(self, template_id: WeekTemplateId) -> None:
        self._store.pop(template_id.value, None)
