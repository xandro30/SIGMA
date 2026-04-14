"""Use case: iniciar una sesión de trabajo."""
from __future__ import annotations

from dataclasses import dataclass

from sigma_core.shared_kernel.value_objects import AreaId, CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId
from sigma_core.tracking.domain.aggregates.work_session import WorkSession, WorkSessionState
from sigma_core.tracking.domain.errors import WorkSessionAlreadyActiveError
from sigma_core.tracking.domain.ports.work_session_repository import WorkSessionRepository
from sigma_core.tracking.domain.value_objects.ids import WorkSessionId
from sigma_core.tracking.domain.value_objects.timer import Timer


@dataclass
class StartWorkSessionCommand:
    space_id: SpaceId
    card_id: CardId
    area_id: AreaId | None
    project_id: ProjectId | None
    epic_id: EpicId | None
    description: str
    timer: Timer
    now: Timestamp


class StartWorkSession:
    def __init__(self, session_repo: WorkSessionRepository) -> None:
        self._session_repo = session_repo

    async def execute(self, cmd: StartWorkSessionCommand) -> WorkSession:
        # NOTE: check-then-act sin transacción Firestore. En un contexto multi-usuario
        # habría race condition, pero SIGMA es una app personal de un solo usuario por
        # space — la probabilidad de requests simultáneos sobre el mismo space_id es
        # prácticamente nula. Decisión consciente: no añadir complejidad de transacción.
        existing = await self._session_repo.get_by_space(cmd.space_id)
        if existing is not None:
            raise WorkSessionAlreadyActiveError(
                f"Space {cmd.space_id.value} already has an active work session"
            )

        session = WorkSession(
            id=WorkSessionId.generate(),
            space_id=cmd.space_id,
            card_id=cmd.card_id,
            area_id=cmd.area_id,
            project_id=cmd.project_id,
            epic_id=cmd.epic_id,
            description=cmd.description,
            timer=cmd.timer,
            completed_rounds=0,
            state=WorkSessionState.WORKING,
            session_started_at=cmd.now,
            current_started_at=cmd.now,
        )
        await self._session_repo.save(session)
        return session
