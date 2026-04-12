from dataclasses import dataclass

from sigma_core.planning.domain.errors import DayTemplateNotFoundError
from sigma_core.planning.domain.ports.day_template_repository import (
    DayTemplateRepository,
)
from sigma_core.planning.domain.value_objects import DayTemplateId


@dataclass
class DeleteDayTemplateCommand:
    template_id: DayTemplateId


class DeleteDayTemplate:
    def __init__(self, day_template_repo: DayTemplateRepository) -> None:
        self._repo = day_template_repo

    async def execute(self, cmd: DeleteDayTemplateCommand) -> None:
        template = await self._repo.get_by_id(cmd.template_id)
        if template is None:
            raise DayTemplateNotFoundError(
                f"DayTemplate {cmd.template_id.value} not found"
            )
        await self._repo.delete(cmd.template_id)
