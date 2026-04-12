from __future__ import annotations

from dataclasses import dataclass

from sigma_core.shared_kernel.value_objects import SizeMapping, SpaceId


@dataclass(frozen=True)
class SpaceView:
    """Planning BC view of a Space.

    Projection with only the fields planning queries need (currently
    `size_mapping` for ETA / capacity calculations). Does not depend on
    the task_management `Space` aggregate.
    """

    id: SpaceId
    size_mapping: SizeMapping | None
