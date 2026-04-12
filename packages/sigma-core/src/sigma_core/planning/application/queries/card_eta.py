from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from math import ceil

from sigma_core.planning.domain.errors import (
    BudgetNotFoundError,
    CycleNotFoundError,
    InvalidCardForEtaError,
    PlanningCardNotFoundError,
)
from sigma_core.planning.domain.ports.card_reader import CardReader
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.ports.space_reader import SpaceReader
from sigma_core.shared_kernel.value_objects import CardId


WORKDAYS_PER_WEEK = 5  # lunes-viernes
DAILY_CAPACITY_DIVISOR = 5  # budget semanal → diario


@dataclass(frozen=True)
class GetCardEtaQuery:
    card_id: CardId
    reference_date: date


@dataclass(frozen=True)
class CardEtaResult:
    card_id: CardId
    estimated_minutes: int
    daily_capacity_minutes: int
    raw_completion_date: date
    buffered_completion_date: date


class GetCardEta:
    """Read-model puro: estima fecha de finalización de una card.

    Lee la card y su space vía los ports propios del planning BC
    (`CardReader`, `SpaceReader`) — no importa aggregates de task_management.

    Asume semana laboral de 5 días (lun-vie). El buffer del cycle se aplica
    sobre los días brutos (no sobre los minutos) para absorber imprevistos.
    """

    def __init__(
        self,
        cycle_repo: CycleRepository,
        card_reader: CardReader,
        space_reader: SpaceReader,
    ) -> None:
        self._cycle_repo = cycle_repo
        self._card_reader = card_reader
        self._space_reader = space_reader

    async def execute(self, query: GetCardEtaQuery) -> CardEtaResult:
        card = await self._card_reader.get_by_id(query.card_id)
        if card is None:
            raise PlanningCardNotFoundError(
                f"Card {query.card_id.value} not found"
            )
        if card.size is None or card.area_id is None:
            raise InvalidCardForEtaError(
                f"Card {card.id.value} requires both size and area_id"
            )

        space_view = await self._space_reader.get_by_id(card.space_id)
        if space_view is None or space_view.size_mapping is None:
            raise InvalidCardForEtaError(
                f"Space {card.space_id.value} missing size_mapping for ETA"
            )
        estimated_minutes = space_view.size_mapping.get_minutes(card.size).value

        cycle = await self._cycle_repo.get_active_by_space(card.space_id)
        if cycle is None:
            raise CycleNotFoundError(
                f"Space {card.space_id.value} has no active cycle"
            )

        area_budget = cycle.area_budgets.get(card.area_id)
        if area_budget is None:
            raise BudgetNotFoundError(
                f"Area {card.area_id.value} has no budget in cycle "
                f"{cycle.id.value}"
            )

        daily_capacity = area_budget.value // DAILY_CAPACITY_DIVISOR
        if daily_capacity <= 0:
            raise InvalidCardForEtaError(
                f"Cycle {cycle.id.value} budget for area "
                f"{card.area_id.value} is too small to produce daily capacity"
            )

        raw_days = ceil(estimated_minutes / daily_capacity)
        buffered_days = ceil(raw_days * (100 + cycle.buffer_percentage) / 100)

        raw_completion = _add_workdays(query.reference_date, raw_days)
        buffered_completion = _add_workdays(query.reference_date, buffered_days)

        return CardEtaResult(
            card_id=card.id,
            estimated_minutes=estimated_minutes,
            daily_capacity_minutes=daily_capacity,
            raw_completion_date=raw_completion,
            buffered_completion_date=buffered_completion,
        )


def _add_workdays(start: date, workdays: int) -> date:
    """Suma N días laborables (lun-vie) sobre `start`, sin contar `start`."""
    current = start
    remaining = workdays
    while remaining > 0:
        current = current + timedelta(days=1)
        if current.weekday() < WORKDAYS_PER_WEEK:
            remaining -= 1
    return current
