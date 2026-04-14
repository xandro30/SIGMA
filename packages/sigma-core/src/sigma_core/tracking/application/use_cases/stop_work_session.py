"""Use case: detener una sesión de trabajo."""
from __future__ import annotations

from dataclasses import dataclass

from sigma_core.shared_kernel.events import EventBus, WorkSessionCompleted
from sigma_core.shared_kernel.value_objects import SpaceId, Timestamp
from sigma_core.tracking.domain.aggregates.tracking_entry import TrackingEntry
from sigma_core.tracking.domain.errors import WorkSessionNotFoundError
from sigma_core.tracking.domain.ports.tracking_entry_repository import TrackingEntryRepository
from sigma_core.tracking.domain.ports.work_session_repository import WorkSessionRepository
from sigma_core.tracking.domain.value_objects.entry_type import EntryType
from sigma_core.tracking.domain.value_objects.ids import TrackingEntryId


@dataclass
class StopWorkSessionCommand:
    space_id: SpaceId
    save: bool
    now: Timestamp


class StopWorkSession:
    def __init__(
        self,
        session_repo: WorkSessionRepository,
        entry_repo: TrackingEntryRepository,
        event_bus: EventBus,
    ) -> None:
        self._session_repo = session_repo
        self._entry_repo = entry_repo
        self._event_bus = event_bus

    async def execute(self, cmd: StopWorkSessionCommand) -> None:
        session = await self._session_repo.get_by_space(cmd.space_id)
        if session is None:
            raise WorkSessionNotFoundError(
                f"No active session for space {cmd.space_id.value}"
            )

        session.stop(cmd.now, cmd.save)
        events = session.collect_events()

        if cmd.save:
            completed_event = next(
                (e for e in events if isinstance(e, WorkSessionCompleted)), None
            )
            minutes = completed_event.minutes if completed_event else 0
            entry = TrackingEntry(
                id=TrackingEntryId.generate(),
                space_id=session.space_id,
                card_id=session.card_id,
                area_id=session.area_id,
                project_id=session.project_id,
                epic_id=session.epic_id,
                entry_type=EntryType.WORK,
                description=session.description,
                minutes=minutes,
                logged_at=cmd.now,
            )
            await self._entry_repo.save(entry)

        for event in events:
            await self._event_bus.publish(event)

        await self._session_repo.delete(cmd.space_id)
