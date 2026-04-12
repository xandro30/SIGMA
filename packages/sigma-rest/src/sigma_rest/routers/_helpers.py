"""Helpers compartidos entre routers de planning.

Centralizan la lógica de "recuperar agregado o lanzar error de dominio"
que aparece duplicada en todos los routers. Al lanzar errores de dominio
(no ``HTTPException``) delegamos el mapping HTTP a los exception handlers
registrados en ``sigma_rest.main``.
"""
from __future__ import annotations

from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.aggregates.week import Week
from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.errors import (
    CycleNotFoundError,
    DayNotFoundError,
    DayTemplateNotFoundError,
    WeekNotFoundError,
    WeekTemplateNotFoundError,
)
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.ports.day_repository import DayRepository
from sigma_core.planning.domain.ports.day_template_repository import (
    DayTemplateRepository,
)
from sigma_core.planning.domain.ports.week_repository import WeekRepository
from sigma_core.planning.domain.ports.week_template_repository import (
    WeekTemplateRepository,
)
from sigma_core.planning.domain.value_objects import (
    CycleId,
    DayId,
    DayTemplateId,
    WeekId,
    WeekTemplateId,
)


async def require_cycle(repo: CycleRepository, cycle_id: CycleId) -> Cycle:
    cycle = await repo.get_by_id(cycle_id)
    if cycle is None:
        raise CycleNotFoundError(f"Cycle {cycle_id.value} not found")
    return cycle


async def require_day(repo: DayRepository, day_id: DayId) -> Day:
    day = await repo.get_by_id(day_id)
    if day is None:
        raise DayNotFoundError(f"Day {day_id.value} not found")
    return day


async def require_day_template(
    repo: DayTemplateRepository, template_id: DayTemplateId
) -> DayTemplate:
    template = await repo.get_by_id(template_id)
    if template is None:
        raise DayTemplateNotFoundError(
            f"DayTemplate {template_id.value} not found"
        )
    return template


async def require_week(repo: WeekRepository, week_id: WeekId) -> Week:
    week = await repo.get_by_id(week_id)
    if week is None:
        raise WeekNotFoundError(f"Week {week_id.value} not found")
    return week


async def require_week_template(
    repo: WeekTemplateRepository, template_id: WeekTemplateId
) -> WeekTemplate:
    template = await repo.get_by_id(template_id)
    if template is None:
        raise WeekTemplateNotFoundError(
            f"WeekTemplate {template_id.value} not found"
        )
    return template
