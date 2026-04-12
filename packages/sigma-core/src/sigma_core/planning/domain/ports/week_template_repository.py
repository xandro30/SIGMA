from __future__ import annotations

from typing import Protocol

from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.value_objects import WeekTemplateId
from sigma_core.shared_kernel.value_objects import SpaceId


class WeekTemplateRepository(Protocol):
    async def save(self, template: WeekTemplate) -> None: ...

    async def get_by_id(
        self, template_id: WeekTemplateId
    ) -> WeekTemplate | None: ...

    async def list_by_space(self, space_id: SpaceId) -> list[WeekTemplate]: ...

    async def delete(self, template_id: WeekTemplateId) -> None: ...
