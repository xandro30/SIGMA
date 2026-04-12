from __future__ import annotations

from typing import Protocol

from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.value_objects import DayTemplateId
from sigma_core.shared_kernel.value_objects import SpaceId


class DayTemplateRepository(Protocol):
    async def save(self, template: DayTemplate) -> None: ...

    async def get_by_id(
        self, template_id: DayTemplateId
    ) -> DayTemplate | None: ...

    async def list_by_space(self, space_id: SpaceId) -> list[DayTemplate]: ...

    async def delete(self, template_id: DayTemplateId) -> None: ...
