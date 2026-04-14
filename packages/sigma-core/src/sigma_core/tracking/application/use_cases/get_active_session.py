"""Use case: obtener la sesión activa de un space."""
from __future__ import annotations

from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.tracking.domain.aggregates.work_session import WorkSession, WorkSessionState
from sigma_core.tracking.domain.ports.work_session_repository import WorkSessionRepository

_ACTIVE_STATES = {WorkSessionState.WORKING, WorkSessionState.BREAK}


class GetActiveSession:
    def __init__(self, session_repo: WorkSessionRepository) -> None:
        self._session_repo = session_repo

    async def execute(self, space_id: SpaceId) -> WorkSession | None:
        session = await self._session_repo.get_by_space(space_id)
        if session is None or session.state not in _ACTIVE_STATES:
            return None
        return session
