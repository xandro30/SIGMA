"""Use case: reanudar trabajo tras un break."""
from __future__ import annotations

from sigma_core.shared_kernel.value_objects import SpaceId, Timestamp
from sigma_core.tracking.domain.aggregates.work_session import WorkSession
from sigma_core.tracking.domain.errors import WorkSessionNotFoundError
from sigma_core.tracking.domain.ports.work_session_repository import WorkSessionRepository


class ResumeFromBreak:
    def __init__(self, session_repo: WorkSessionRepository) -> None:
        self._session_repo = session_repo

    async def execute(self, space_id: SpaceId, now: Timestamp) -> WorkSession:
        session = await self._session_repo.get_by_space(space_id)
        if session is None:
            raise WorkSessionNotFoundError(f"No active session for space {space_id.value}")

        session.resume_from_break(now)
        await self._session_repo.save(session)
        return session
