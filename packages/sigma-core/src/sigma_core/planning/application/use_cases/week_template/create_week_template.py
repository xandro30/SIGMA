from dataclasses import dataclass

from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.ports.week_template_repository import (
    WeekTemplateRepository,
)
from sigma_core.planning.domain.value_objects import WeekTemplateId
from sigma_core.shared_kernel.value_objects import SpaceId


@dataclass
class CreateWeekTemplateCommand:
    space_id: SpaceId
    name: str


class CreateWeekTemplate:
    def __init__(self, week_template_repo: WeekTemplateRepository) -> None:
        self._repo = week_template_repo

    async def execute(self, cmd: CreateWeekTemplateCommand) -> WeekTemplateId:
        template = WeekTemplate(
            id=WeekTemplateId.generate(),
            space_id=cmd.space_id,
            name=cmd.name,
        )
        await self._repo.save(template)
        return template.id
