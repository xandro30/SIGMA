"""Router para el BC tracking — sesiones de trabajo Pomodoro."""
from fastapi import APIRouter, Depends, Response

from sigma_core.shared_kernel.value_objects import AreaId, CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId
from sigma_core.tracking.application.use_cases.complete_round import CompleteRound
from sigma_core.tracking.application.use_cases.get_active_session import GetActiveSession
from sigma_core.tracking.application.use_cases.resume_from_break import ResumeFromBreak
from sigma_core.tracking.application.use_cases.start_work_session import (
    StartWorkSession,
    StartWorkSessionCommand,
)
from sigma_core.tracking.application.use_cases.stop_work_session import (
    StopWorkSession,
    StopWorkSessionCommand,
)
from sigma_core.tracking.domain.value_objects.timer import Timer, TimerTechnique
from sigma_rest.dependencies import (
    get_event_bus,
    get_tracking_entry_repo,
    get_work_session_repo,
)
from sigma_rest.mappers.tracking_mappers import work_session_to_response
from sigma_rest.schemas.tracking_schemas import StartWorkSessionRequest, WorkSessionResponse

router = APIRouter(tags=["tracking"])


@router.post(
    "/spaces/{space_id}/tracking/sessions",
    response_model=WorkSessionResponse,
    status_code=201,
)
async def start_work_session(
    space_id: str,
    body: StartWorkSessionRequest,
    session_repo=Depends(get_work_session_repo),
):
    timer = Timer(
        technique=TimerTechnique(body.timer.technique),
        work_minutes=body.timer.work_minutes,
        break_minutes=body.timer.break_minutes,
        num_rounds=body.timer.num_rounds,
    )
    cmd = StartWorkSessionCommand(
        space_id=SpaceId(space_id),
        card_id=CardId(body.card_id),
        area_id=AreaId(body.area_id) if body.area_id else None,
        project_id=ProjectId(body.project_id) if body.project_id else None,
        epic_id=EpicId(body.epic_id) if body.epic_id else None,
        description=body.description,
        timer=timer,
        now=Timestamp.now(),
    )
    session = await StartWorkSession(session_repo).execute(cmd)
    return work_session_to_response(session)


@router.get(
    "/spaces/{space_id}/tracking/sessions/active",
    responses={
        200: {"model": WorkSessionResponse},
        204: {"description": "No active session"},
    },
)
async def get_active_session(
    space_id: str,
    session_repo=Depends(get_work_session_repo),
):
    session = await GetActiveSession(session_repo).execute(SpaceId(space_id))
    if session is None:
        return Response(status_code=204)
    return work_session_to_response(session)


@router.post(
    "/spaces/{space_id}/tracking/sessions/rounds",
    response_model=WorkSessionResponse,
)
async def complete_round(
    space_id: str,
    session_repo=Depends(get_work_session_repo),
    event_bus=Depends(get_event_bus),
):
    session = await CompleteRound(session_repo, event_bus).execute(
        SpaceId(space_id), Timestamp.now()
    )
    return work_session_to_response(session)


@router.post(
    "/spaces/{space_id}/tracking/sessions/resume",
    response_model=WorkSessionResponse,
)
async def resume_from_break(
    space_id: str,
    session_repo=Depends(get_work_session_repo),
):
    session = await ResumeFromBreak(session_repo).execute(
        SpaceId(space_id), Timestamp.now()
    )
    return work_session_to_response(session)


@router.delete(
    "/spaces/{space_id}/tracking/sessions",
    status_code=204,
)
async def stop_work_session(
    space_id: str,
    save: bool = True,
    session_repo=Depends(get_work_session_repo),
    entry_repo=Depends(get_tracking_entry_repo),
    event_bus=Depends(get_event_bus),
):
    cmd = StopWorkSessionCommand(
        space_id=SpaceId(space_id),
        save=save,
        now=Timestamp.now(),
    )
    await StopWorkSession(session_repo, entry_repo, event_bus).execute(cmd)
    return Response(status_code=204)
