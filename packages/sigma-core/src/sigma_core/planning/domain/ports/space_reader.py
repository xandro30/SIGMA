from __future__ import annotations

from typing import Protocol

from sigma_core.planning.domain.read_models.space_view import SpaceView
from sigma_core.shared_kernel.value_objects import SpaceId


class SpaceReader(Protocol):
    """Port for reading Space projections from within the planning BC.

    The concrete implementation lives in `planning.infrastructure` and
    maps persistence data to `SpaceView` DTOs — planning.domain/application
    never touches the task_management Space aggregate.
    """

    async def get_by_id(self, space_id: SpaceId) -> SpaceView | None:
        ...
