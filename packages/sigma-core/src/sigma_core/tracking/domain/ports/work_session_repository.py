"""Port: WorkSessionRepository."""
from __future__ import annotations

from typing import Protocol

from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.tracking.domain.aggregates.work_session import WorkSession


class WorkSessionRepository(Protocol):
    async def save(self, session: WorkSession) -> None: ...
    async def get_by_space(self, space_id: SpaceId) -> WorkSession | None: ...
    async def delete(self, space_id: SpaceId) -> None: ...
