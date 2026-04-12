from dataclasses import dataclass

from sigma_core.planning.domain.errors import WeekTemplateNotFoundError
from sigma_core.planning.domain.ports.week_template_repository import (
    WeekTemplateRepository,
)
from sigma_core.planning.domain.value_objects import WeekTemplateId


@dataclass
class DeleteWeekTemplateCommand:
    template_id: WeekTemplateId


class DeleteWeekTemplate:
    def __init__(self, week_template_repo: WeekTemplateRepository) -> None:
        self._repo = week_template_repo

    async def execute(self, cmd: DeleteWeekTemplateCommand) -> None:
        template = await self._repo.get_by_id(cmd.template_id)
        if template is None:
            raise WeekTemplateNotFoundError(
                f"WeekTemplate {cmd.template_id.value} not found"
            )
        await self._repo.delete(cmd.template_id)
