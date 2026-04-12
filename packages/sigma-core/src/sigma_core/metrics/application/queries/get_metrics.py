"""Query unificada de metricas: snapshot (ciclo cerrado) u on-demand (activo)."""
from __future__ import annotations

from dataclasses import dataclass

from sigma_core.metrics.domain.aggregates.cycle_summary import CycleSummary
from sigma_core.metrics.domain.errors import (
    CycleSummaryNotFoundError,
    MetricsCycleNotFoundError,
)
from sigma_core.metrics.domain.ports.card_reader import MetricsCardReader
from sigma_core.metrics.domain.ports.cycle_reader import MetricsCycleReader
from sigma_core.metrics.domain.ports.cycle_summary_repository import (
    CycleSummaryRepository,
)
from sigma_core.metrics.domain.ports.space_reader import MetricsSpaceReader
from sigma_core.metrics.domain.services.metrics_calculator import MetricsCalculator
from sigma_core.metrics.domain.value_objects import (
    AreaMetrics,
    CycleSummaryId,
    CycleView,
    MetricsBlock,
)
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.value_objects import AreaId, SpaceId, Timestamp


@dataclass
class GetMetricsQuery:
    space_id: SpaceId
    cycle_id: CycleId | None = None


@dataclass(frozen=True)
class MetricsResult:
    cycle_id: CycleId
    space_id: SpaceId
    date_range: DateRange
    computed_at: Timestamp
    source: str  # "snapshot" | "on_demand"
    global_metrics: MetricsBlock
    areas: dict[AreaId, AreaMetrics]


class GetMetrics:
    """Devuelve metricas de un ciclo.

    - Si ``cycle_id`` apunta a ciclo cerrado → lee ``CycleSummary`` persistido.
    - Si apunta a ciclo activo → calcula on-demand con ``MetricsCalculator``.
    - Si ``cycle_id`` es None → busca el ciclo activo del Space.
    """

    def __init__(
        self,
        cycle_reader: MetricsCycleReader,
        summary_repo: CycleSummaryRepository,
        card_reader: MetricsCardReader,
        space_reader: MetricsSpaceReader,
    ) -> None:
        self._cycle_reader = cycle_reader
        self._summary_repo = summary_repo
        self._card_reader = card_reader
        self._space_reader = space_reader
        self._calculator = MetricsCalculator()

    async def execute(self, query: GetMetricsQuery) -> MetricsResult:
        cycle_view = await self._resolve_cycle(query)

        if cycle_view.state == "closed":
            return await self._from_snapshot(cycle_view)
        return await self._on_demand(cycle_view)

    async def _resolve_cycle(self, query: GetMetricsQuery) -> CycleView:
        if query.cycle_id is not None:
            cycle_view = await self._cycle_reader.get_by_id(query.cycle_id)
            if cycle_view is None:
                raise MetricsCycleNotFoundError(
                    f"Cycle {query.cycle_id.value} not found"
                )
            return cycle_view

        cycle_view = await self._cycle_reader.get_active_by_space(
            query.space_id
        )
        if cycle_view is None:
            raise MetricsCycleNotFoundError(
                f"Space {query.space_id.value} has no active cycle"
            )
        return cycle_view

    async def _from_snapshot(self, cycle_view: CycleView) -> MetricsResult:
        summary = await self._summary_repo.get_by_cycle_id(cycle_view.id)
        if summary is None:
            raise CycleSummaryNotFoundError(
                f"CycleSummary for cycle {cycle_view.id.value} not found "
                "(closed cycle without summary — inconsistency)"
            )
        return MetricsResult(
            cycle_id=summary.cycle_id,
            space_id=summary.space_id,
            date_range=summary.date_range,
            computed_at=summary.created_at,
            source="snapshot",
            global_metrics=summary.global_metrics,
            areas=summary.areas,
        )

    async def _on_demand(self, cycle_view: CycleView) -> MetricsResult:
        cards = await self._card_reader.list_completed_in_range(
            cycle_view.space_id, cycle_view.date_range
        )
        size_mapping = await self._space_reader.get_size_mapping(
            cycle_view.space_id
        )
        area_budgets_int = {
            aid: minutes
            for aid, minutes in cycle_view.area_budgets.items()
        }
        global_block, areas = self._calculator.calculate(
            cards, area_budgets_int, size_mapping
        )
        return MetricsResult(
            cycle_id=cycle_view.id,
            space_id=cycle_view.space_id,
            date_range=cycle_view.date_range,
            computed_at=Timestamp.now(),
            source="on_demand",
            global_metrics=global_block,
            areas=areas,
        )
