from dataclasses import dataclass
from datetime import date, datetime, time

from sigma_core.planning.application.use_cases.day_template.create_day_template import (
    DayTemplateBlockSpec,  # re-exported for REST consumers
)
from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.errors import (
    DayNotEmptyError,
    DayTemplateNotFoundError,
)
from sigma_core.planning.domain.ports.day_repository import DayRepository
from sigma_core.planning.domain.ports.day_template_repository import (
    DayTemplateRepository,
)
from sigma_core.planning.domain.value_objects import BlockId, DayId, DayTemplateId
from sigma_core.shared_kernel.config import get_app_timezone
from sigma_core.shared_kernel.value_objects import SpaceId, Timestamp


__all__ = [
    "ApplyDayTemplateToDay",
    "ApplyDayTemplateToDayCommand",
    "DayTemplateBlockSpec",
]


@dataclass
class ApplyDayTemplateToDayCommand:
    template_id: DayTemplateId
    space_id: SpaceId
    target_date: date
    replace_existing: bool = False


class ApplyDayTemplateToDay:
    """Forka los bloques de una `DayTemplate` sobre un `Day` concreto.

    - Si no existe `Day` para `(space_id, target_date)`, lo crea vacío.
    - Si `replace_existing=False` y el day tiene bloques → `DayNotEmptyError`.
    - Si `replace_existing=True`, limpia los bloques existentes antes de aplicar.
    - Cada bloque de la plantilla se materializa con un `BlockId` nuevo y una
      `start_at` absoluta construida a partir de `target_date` + `TimeOfDay`.
    """

    def __init__(
        self,
        day_template_repo: DayTemplateRepository,
        day_repo: DayRepository,
    ) -> None:
        self._template_repo = day_template_repo
        self._day_repo = day_repo

    async def execute(self, cmd: ApplyDayTemplateToDayCommand) -> DayId:
        template = await self._template_repo.get_by_id(cmd.template_id)
        if template is None:
            raise DayTemplateNotFoundError(
                f"DayTemplate {cmd.template_id.value} not found"
            )

        day_id = DayId.for_space_and_date(cmd.space_id, cmd.target_date)
        day = await self._day_repo.get_by_id(day_id)
        if day is None:
            day = Day(
                id=day_id,
                space_id=cmd.space_id,
                date=cmd.target_date,
            )

        if day.blocks:
            if not cmd.replace_existing:
                raise DayNotEmptyError(
                    f"Day {day.id.value} already has blocks; "
                    "set replace_existing=True to overwrite"
                )
            day.clear_blocks()

        for template_block in template.blocks:
            start_at = Timestamp(
                datetime.combine(
                    cmd.target_date,
                    time(
                        hour=template_block.start_at.hour,
                        minute=template_block.start_at.minute,
                    ),
                    tzinfo=get_app_timezone(),
                )
            )
            day.add_block(
                TimeBlock(
                    id=BlockId.generate(),
                    start_at=start_at,
                    duration=template_block.duration,
                    area_id=template_block.area_id,
                    notes=template_block.notes,
                )
            )

        await self._day_repo.save(day)
        return day.id
