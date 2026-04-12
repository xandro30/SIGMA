from dataclasses import dataclass

from sigma_core.planning.domain.enums import DayOfWeek
from sigma_core.planning.domain.errors import (
    CrossSpaceReferenceError,
    DayTemplateNotFoundError,
    WeekTemplateNotFoundError,
)
from sigma_core.planning.domain.ports.day_template_repository import (
    DayTemplateRepository,
)
from sigma_core.planning.domain.ports.week_template_repository import (
    WeekTemplateRepository,
)
from sigma_core.planning.domain.value_objects import (
    DayTemplateId,
    WeekTemplateId,
)


@dataclass
class SetWeekTemplateSlotCommand:
    week_template_id: WeekTemplateId
    day: DayOfWeek
    day_template_id: DayTemplateId


class SetWeekTemplateSlot:
    """Asigna un `DayTemplate` a un slot semanal validando que exista."""

    def __init__(
        self,
        week_template_repo: WeekTemplateRepository,
        day_template_repo: DayTemplateRepository,
    ) -> None:
        self._week_repo = week_template_repo
        self._day_template_repo = day_template_repo

    async def execute(self, cmd: SetWeekTemplateSlotCommand) -> None:
        week_template = await self._week_repo.get_by_id(cmd.week_template_id)
        if week_template is None:
            raise WeekTemplateNotFoundError(
                f"WeekTemplate {cmd.week_template_id.value} not found"
            )
        day_template = await self._day_template_repo.get_by_id(
            cmd.day_template_id
        )
        if day_template is None:
            raise DayTemplateNotFoundError(
                f"DayTemplate {cmd.day_template_id.value} not found"
            )
        if day_template.space_id != week_template.space_id:
            raise CrossSpaceReferenceError(
                source_kind="WeekTemplate",
                source_space_id=week_template.space_id.value,
                target_kind="DayTemplate",
                target_space_id=day_template.space_id.value,
            )
        week_template.set_slot(cmd.day, cmd.day_template_id)
        await self._week_repo.save(week_template)
