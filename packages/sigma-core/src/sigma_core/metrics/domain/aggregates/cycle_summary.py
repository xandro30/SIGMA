"""CycleSummary — aggregate inmutable con metricas precalculadas jerarquicas."""
from __future__ import annotations

from dataclasses import dataclass

from sigma_core.metrics.domain.value_objects import (
    AreaMetrics,
    CycleSummaryId,
    MetricsBlock,
)
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.value_objects import AreaId, SpaceId, Timestamp


@dataclass(frozen=True)
class CycleSummary:
    """Metricas precalculadas de un ciclo cerrado.

    Estructura jerarquica PARA: global → area → project → epic.
    Inmutable — se genera una vez al cerrar el ciclo y no se modifica.
    """

    id: CycleSummaryId
    cycle_id: CycleId
    space_id: SpaceId
    date_range: DateRange
    global_metrics: MetricsBlock
    areas: dict[AreaId, AreaMetrics]
    created_at: Timestamp
