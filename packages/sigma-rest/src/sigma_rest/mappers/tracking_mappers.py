"""Mappers dominio → response para tracking."""
from sigma_core.tracking.domain.aggregates.work_session import WorkSession
from sigma_rest.schemas.tracking_schemas import TimerResponse, WorkSessionResponse


def work_session_to_response(session: WorkSession) -> WorkSessionResponse:
    return WorkSessionResponse(
        id=session.id.value,
        space_id=session.space_id.value,
        card_id=session.card_id.value,
        area_id=session.area_id.value if session.area_id else None,
        project_id=session.project_id.value if session.project_id else None,
        epic_id=session.epic_id.value if session.epic_id else None,
        description=session.description,
        timer=TimerResponse(
            technique=session.timer.technique.value,
            work_minutes=session.timer.work_minutes,
            break_minutes=session.timer.break_minutes,
            num_rounds=session.timer.num_rounds,
        ),
        completed_rounds=session.completed_rounds,
        state=session.state.value,
        session_started_at=session.session_started_at.value.isoformat(),
        current_started_at=session.current_started_at.value.isoformat(),
    )
