"""Handler del evento CycleClosed — crea CycleSummary + CycleSnapshot."""
from __future__ import annotations

from sigma_core.metrics.domain.aggregates.cycle_snapshot import CycleSnapshot
from sigma_core.metrics.domain.aggregates.cycle_summary import CycleSummary
from sigma_core.metrics.domain.ports.card_reader import MetricsCardReader
from sigma_core.metrics.domain.ports.cycle_reader import MetricsCycleReader
from sigma_core.metrics.domain.ports.cycle_snapshot_repository import (
    CycleSnapshotRepository,
)
from sigma_core.metrics.domain.ports.cycle_summary_repository import (
    CycleSummaryRepository,
)
from sigma_core.metrics.domain.ports.space_reader import MetricsSpaceReader
from sigma_core.metrics.domain.services.metrics_calculator import MetricsCalculator
from sigma_core.metrics.domain.value_objects import CycleSnapshotId, CycleSummaryId
from sigma_core.shared_kernel.events import CycleClosed
from sigma_core.shared_kernel.value_objects import Timestamp


class OnCycleClosedHandler:
    """Reacciona al cierre de un ciclo creando los artefactos de metrics.

    Se registra como subscriber de ``CycleClosed`` en el ``EventBus``.
    Lee los datos necesarios via readers propios del BC, calcula metricas
    con ``MetricsCalculator`` y persiste ``CycleSummary`` + ``CycleSnapshot``.
    """

    def __init__(
        self,
        card_reader: MetricsCardReader,
        space_reader: MetricsSpaceReader,
        cycle_reader: MetricsCycleReader,
        summary_repo: CycleSummaryRepository,
        snapshot_repo: CycleSnapshotRepository,
    ) -> None:
        self._card_reader = card_reader
        self._space_reader = space_reader
        self._cycle_reader = cycle_reader
        self._summary_repo = summary_repo
        self._snapshot_repo = snapshot_repo
        self._calculator = MetricsCalculator()

    async def __call__(self, event: CycleClosed) -> None:
        cycle_view = await self._cycle_reader.get_by_id(event.cycle_id)
        if cycle_view is None:
            raise ValueError(
                f"Cycle {event.cycle_id.value} not found in reader "
                "(inconsistency: CycleClosed fired but cycle missing)"
            )

        cards = await self._card_reader.list_completed_in_range(
            event.space_id, event.date_range
        )
        size_mapping = await self._space_reader.get_size_mapping(
            event.space_id
        )

        area_budgets_int = {
            aid: minutes
            for aid, minutes in cycle_view.area_budgets.items()
        }

        global_block, areas = self._calculator.calculate(
            cards, area_budgets_int, size_mapping
        )

        now = Timestamp.now()

        summary = CycleSummary(
            id=CycleSummaryId.generate(),
            cycle_id=event.cycle_id,
            space_id=event.space_id,
            date_range=event.date_range,
            global_metrics=global_block,
            areas=areas,
            created_at=now,
        )
        await self._summary_repo.save(summary)

        snapshot = CycleSnapshot(
            id=CycleSnapshotId.generate(),
            cycle_id=event.cycle_id,
            space_id=event.space_id,
            date_range=event.date_range,
            buffer_percentage=cycle_view.buffer_percentage,
            area_budgets=area_budgets_int,
            size_mapping=size_mapping,
            cards=cards,
            created_at=now,
        )
        await self._snapshot_repo.save(snapshot)
