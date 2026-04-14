"""Use case: completar un round Pomodoro."""
from __future__ import annotations

from sigma_core.shared_kernel.events import EventBus
from sigma_core.shared_kernel.value_objects import SpaceId, Timestamp
from sigma_core.tracking.domain.aggregates.work_session import WorkSession
from sigma_core.tracking.domain.errors import WorkSessionNotFoundError
from sigma_core.tracking.domain.ports.work_session_repository import WorkSessionRepository


class CompleteRound:
    def __init__(self, session_repo: WorkSessionRepository, event_bus: EventBus) -> None:
        self._session_repo = session_repo
        self._event_bus = event_bus

    async def execute(self, space_id: SpaceId, now: Timestamp) -> WorkSession:
        session = await self._session_repo.get_by_space(space_id)
        if session is None:
            raise WorkSessionNotFoundError(f"No active session for space {space_id.value}")

        from sigma_core.tracking.domain.aggregates.work_session import WorkSessionState

        session.complete_round(now)

        if session.state == WorkSessionState.COMPLETED:
            for event in session.collect_events():
                await self._event_bus.publish(event)
            await self._session_repo.delete(space_id)
        else:
            await self._session_repo.save(session)

        return session
