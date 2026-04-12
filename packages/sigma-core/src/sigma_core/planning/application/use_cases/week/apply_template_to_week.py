from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.enums import DayOfWeek
from sigma_core.planning.domain.errors import (
    CrossSpaceReferenceError,
    DayNotEmptyError,
    DayTemplateNotFoundError,
    WeekNotFoundError,
    WeekTemplateNotFoundError,
)
from sigma_core.planning.domain.ports.day_repository import DayRepository
from sigma_core.planning.domain.ports.day_template_repository import (
    DayTemplateRepository,
)
from sigma_core.planning.domain.ports.week_repository import WeekRepository
from sigma_core.planning.domain.ports.week_template_repository import (
    WeekTemplateRepository,
)
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DayId,
    WeekId,
    WeekTemplateId,
)
from sigma_core.shared_kernel.config import get_app_timezone
from sigma_core.shared_kernel.value_objects import Timestamp


@dataclass
class ApplyTemplateToWeekCommand:
    week_id: WeekId
    template_id: WeekTemplateId
    replace_existing: bool = False


class ApplyTemplateToWeek:
    """Materializa un ``WeekTemplate`` sobre un ``Week`` concreto.

    Responsabilidades:
      1. Valida existencia del ``Week`` y del ``WeekTemplate``.
      2. Valida que ambos pertenezcan al mismo Space (no se permiten
         referencias cruzadas entre spaces).
      3. Pre-resuelve todos los ``DayTemplate`` referenciados y falla fast
         si alguno no existe — así no materializamos parcialmente.
      4. Para cada slot relleno, materializa un ``Day`` determinista
         ``DayId.for_space_and_date(space_id, target_date)`` con los
         ``TimeBlock`` correspondientes al ``DayTemplate``.
      5. Registra en el agregado ``Week`` que el template se aplicó.

    Atomicidad: si falla cualquier paso de validación (2-3), no se escribe
    ningún Day ni se modifica el Week. La escritura de los Days y del Week
    debería hacerse en una transacción Firestore en el repo real; el flujo
    aquí garantiza el orden (validar todo → escribir todo).
    """

    def __init__(
        self,
        week_repo: WeekRepository,
        week_template_repo: WeekTemplateRepository,
        day_template_repo: DayTemplateRepository,
        day_repo: DayRepository,
    ) -> None:
        self._week_repo = week_repo
        self._week_template_repo = week_template_repo
        self._day_template_repo = day_template_repo
        self._day_repo = day_repo

    async def execute(
        self, cmd: ApplyTemplateToWeekCommand
    ) -> list[DayId]:
        week = await self._week_repo.get_by_id(cmd.week_id)
        if week is None:
            raise WeekNotFoundError(f"Week {cmd.week_id.value} not found")

        week_template = await self._week_template_repo.get_by_id(
            cmd.template_id
        )
        if week_template is None:
            raise WeekTemplateNotFoundError(
                f"WeekTemplate {cmd.template_id.value} not found"
            )

        if week_template.space_id != week.space_id:
            raise CrossSpaceReferenceError(
                source_kind="Week",
                source_space_id=week.space_id.value,
                target_kind="WeekTemplate",
                target_space_id=week_template.space_id.value,
            )

        # Pre-resolución: recoger los DayTemplates referenciados por slots
        # no vacíos y fallar fast si alguno falta.
        slot_resolutions: list[tuple[DayOfWeek, date, list[TimeBlock]]] = []
        tz = get_app_timezone()
        for dow in DayOfWeek:
            day_template_id = week_template.slots.get(dow)
            if day_template_id is None:
                continue
            day_template = await self._day_template_repo.get_by_id(
                day_template_id
            )
            if day_template is None:
                raise DayTemplateNotFoundError(
                    f"DayTemplate {day_template_id.value} referenced by slot "
                    f"{dow.name} not found"
                )
            target_date = week.week_start + timedelta(days=dow.value)
            blocks = _materialize_blocks(day_template, target_date, tz)
            slot_resolutions.append((dow, target_date, blocks))

        # Aplicación: crear/actualizar los Days deterministas
        touched: list[DayId] = []
        for _dow, target_date, blocks in slot_resolutions:
            day_id = DayId.for_space_and_date(week.space_id, target_date)
            existing = await self._day_repo.get_by_id(day_id)
            if existing is not None:
                if existing.blocks and not cmd.replace_existing:
                    raise DayNotEmptyError(
                        f"Day {day_id.value} already has blocks; "
                        "set replace_existing=True to overwrite"
                    )
                existing.clear_blocks()
                day = existing
            else:
                day = Day(
                    id=day_id,
                    space_id=week.space_id,
                    date=target_date,
                )
            for block in blocks:
                day.add_block(block)
            await self._day_repo.save(day)
            touched.append(day_id)

        # Registrar en el Week que este template se aplicó
        week.record_template_applied(cmd.template_id)
        await self._week_repo.save(week)

        return touched


def _materialize_blocks(day_template, target_date: date, tz) -> list[TimeBlock]:
    """Convierte los ``DayTemplateBlock`` (relativos) en ``TimeBlock``
    absolutos anclados a ``target_date`` en la zona horaria de aplicación."""
    materialized: list[TimeBlock] = []
    for template_block in day_template.blocks:
        start_at = Timestamp(
            datetime.combine(
                target_date,
                time(
                    hour=template_block.start_at.hour,
                    minute=template_block.start_at.minute,
                ),
                tzinfo=tz,
            )
        )
        materialized.append(
            TimeBlock(
                id=BlockId.generate(),
                start_at=start_at,
                duration=template_block.duration,
                area_id=template_block.area_id,
                notes=template_block.notes,
            )
        )
    return materialized
