"""TrackingEntry aggregate — registro permanente de un bloque de tiempo."""
from __future__ import annotations

from dataclasses import dataclass

from sigma_core.shared_kernel.value_objects import AreaId, CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId
from sigma_core.tracking.domain.value_objects.entry_type import EntryType
from sigma_core.tracking.domain.value_objects.ids import TrackingEntryId


@dataclass(frozen=True)
class TrackingEntry:
    """Registro permanente de un bloque de tiempo trabajado.

    Inmutable una vez creado. El campo ``minutes`` incluye descansos
    (tiempo total del bloque), alineado con los budgets de ciclo.
    """

    id: TrackingEntryId
    space_id: SpaceId
    card_id: CardId | None
    area_id: AreaId | None
    project_id: ProjectId | None
    epic_id: EpicId | None
    entry_type: EntryType
    description: str
    minutes: int
    logged_at: Timestamp
