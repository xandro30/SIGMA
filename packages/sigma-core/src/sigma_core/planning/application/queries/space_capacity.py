from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sigma_core.planning.domain.errors import CycleNotFoundError
from sigma_core.planning.domain.ports.card_reader import CardReader
from sigma_core.planning.domain.ports.cycle_repository import CycleRepository
from sigma_core.planning.domain.ports.space_reader import SpaceReader
from sigma_core.planning.domain.read_models.card_view import CardView
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SizeMapping, SpaceId


@dataclass(frozen=True)
class GetSpaceCapacityQuery:
    space_id: SpaceId
    reference_date: date | None = None


@dataclass(frozen=True)
class AreaCapacity:
    area_id: AreaId
    budget_minutes: int
    consumed_minutes: int
    remaining_minutes: int  # puede ser negativo cuando se excede el budget


@dataclass(frozen=True)
class SpaceCapacityResult:
    cycle_id: CycleId
    date_range: DateRange
    buffer_percentage: int
    areas: list[AreaCapacity]


class GetSpaceCapacity:
    """Read-model puro: calcula consumo y remaining por area sobre el cycle activo.

    Lee cards completadas (`completed_at` dentro del rango del cycle activo)
    vía el port `CardReader` propio del planning BC. No importa aggregates
    ni constantes de task_management — todo el acceso a datos de Card/Space
    pasa por proyecciones (`CardView`, `SpaceView`) definidas en este BC.
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

    async def execute(
        self, query: GetSpaceCapacityQuery
    ) -> SpaceCapacityResult:
        cycle = await self._cycle_repo.get_active_by_space(query.space_id)
        if cycle is None:
            raise CycleNotFoundError(
                f"Space {query.space_id.value} has no active cycle"
            )

        space_view = await self._space_reader.get_by_id(query.space_id)
        size_mapping = space_view.size_mapping if space_view is not None else None

        completed_cards = await self._card_reader.list_completed_in_range(
            query.space_id, cycle.date_range
        )

        consumed_by_area: dict[AreaId, int] = {
            area_id: 0 for area_id in cycle.area_budgets
        }
        for card in completed_cards:
            if card.area_id is None or card.area_id not in cycle.area_budgets:
                continue
            contribution = self._card_contribution_minutes(card, size_mapping)
            consumed_by_area[card.area_id] += contribution

        areas = [
            self._build_area_capacity(
                area_id=area_id,
                budget=budget,
                consumed=consumed_by_area.get(area_id, 0),
                buffer_percentage=cycle.buffer_percentage,
            )
            for area_id, budget in cycle.area_budgets.items()
        ]

        return SpaceCapacityResult(
            cycle_id=cycle.id,
            date_range=cycle.date_range,
            buffer_percentage=cycle.buffer_percentage,
            areas=areas,
        )

    @staticmethod
    def _card_contribution_minutes(
        card: CardView, size_mapping: SizeMapping | None
    ) -> int:
        if card.actual_time.value > 0:
            return card.actual_time.value
        if card.size is not None and size_mapping is not None:
            return size_mapping.get_minutes(card.size).value
        return 0

    @staticmethod
    def _build_area_capacity(
        *,
        area_id: AreaId,
        budget: Minutes,
        consumed: int,
        buffer_percentage: int,
    ) -> AreaCapacity:
        effective_budget = budget.value * (100 - buffer_percentage) // 100
        return AreaCapacity(
            area_id=area_id,
            budget_minutes=budget.value,
            consumed_minutes=consumed,
            remaining_minutes=effective_budget - consumed,
        )
