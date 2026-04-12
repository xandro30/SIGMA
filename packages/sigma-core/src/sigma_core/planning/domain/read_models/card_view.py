from __future__ import annotations

from dataclasses import dataclass

from sigma_core.shared_kernel.enums import CardSize
from sigma_core.shared_kernel.value_objects import (
    AreaId,
    CardId,
    Minutes,
    SpaceId,
    Timestamp,
)


@dataclass(frozen=True)
class CardView:
    """Planning BC view of a Card.

    Projection with only the fields planning queries need.
    Does not depend on the task_management `Card` aggregate — this
    keeps the planning BC decoupled from task_management domain types.

    The underlying value objects (`CardId`, `SpaceId`, `AreaId`, `Minutes`,
    `Timestamp`, `CardSize`) are shared-kernel primitives: pure identifiers
    and measurements with no BC-specific behaviour.
    """

    id: CardId
    space_id: SpaceId
    area_id: AreaId | None
    size: CardSize | None
    actual_time: Minutes
    completed_at: Timestamp | None
