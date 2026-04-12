from dataclasses import dataclass

from sigma_core.planning.domain.enums import DayOfWeek
from sigma_core.planning.domain.errors import WeekTemplateNotFoundError
from sigma_core.planning.domain.ports.week_template_repository import (
    WeekTemplateRepository,
)
from sigma_core.planning.domain.value_objects import WeekTemplateId


@dataclass
class ClearWeekTemplateSlotCommand:
    week_template_id: WeekTemplateId
    day: DayOfWeek


class ClearWeekTemplateSlot:
    def __init__(self, week_template_repo: WeekTemplateRepository) -> None:
        self._repo = week_template_repo

    async def execute(self, cmd: ClearWeekTemplateSlotCommand) -> None:
        week_template = await self._repo.get_by_id(cmd.week_template_id)
        if week_template is None:
            raise WeekTemplateNotFoundError(
                f"WeekTemplate {cmd.week_template_id.value} not found"
            )
        week_template.clear_slot(cmd.day)
        await self._repo.save(week_template)
