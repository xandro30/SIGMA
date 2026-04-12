"""CycleSnapshot — aggregate inmutable con raw copy de datos del ciclo."""
from __future__ import annotations

from dataclasses import dataclass

from sigma_core.metrics.domain.value_objects import CardSnapshot, CycleSnapshotId
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.value_objects import AreaId, SpaceId, Timestamp


@dataclass(frozen=True)
class CycleSnapshot:
    """Raw copy de los datos del ciclo al momento de cerrarlo.

    Contiene todas las cards completadas en el rango como ``CardSnapshot``
    (projections con los campos relevantes para metricas). Permite
    recalcular metricas futuras sin depender de que las cards/spaces
    sigan existiendo o no hayan cambiado.
    """

    id: CycleSnapshotId
    cycle_id: CycleId
    space_id: SpaceId
    date_range: DateRange
    buffer_percentage: int
    area_budgets: dict[AreaId, int]
    size_mapping: dict[str, int] | None
    cards: list[CardSnapshot]
    created_at: Timestamp
