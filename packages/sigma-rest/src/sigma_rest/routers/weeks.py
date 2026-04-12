from datetime import date as date_cls

from fastapi import APIRouter, Depends, Response

from sigma_core.planning.application.use_cases.week.apply_template_to_week import (
    ApplyTemplateToWeek,
    ApplyTemplateToWeekCommand,
)
from sigma_core.planning.application.use_cases.week.create_week import (
    CreateWeek,
    CreateWeekCommand,
)
from sigma_core.planning.application.use_cases.week.delete_week import (
    DeleteWeek,
    DeleteWeekCommand,
)
from sigma_core.planning.application.use_cases.week.get_week import (
    GetWeek,
    GetWeekQuery,
)
from sigma_core.planning.application.use_cases.week.set_week_notes import (
    SetWeekNotes,
    SetWeekNotesCommand,
)
from sigma_core.planning.domain.value_objects import WeekId, WeekTemplateId
from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_rest.dependencies import (
    get_day_repo,
    get_day_template_repo,
    get_week_repo,
    get_week_template_repo,
)
from sigma_rest.mappers.week_mappers import week_to_response
from sigma_rest.schemas.week_schemas import (
    ApplyTemplateToWeekRequest,
    CreateWeekRequest,
    SetWeekNotesRequest,
)


router = APIRouter(prefix="/spaces/{space_id}/weeks", tags=["weeks"])


def _week_id(space_id: str, week_start: date_cls) -> WeekId:
    return WeekId.for_space_and_week_start(SpaceId(space_id), week_start)


@router.post("", status_code=201)
async def create_week(
    space_id: str,
    body: CreateWeekRequest,
    week_repo=Depends(get_week_repo),
):
    use_case = CreateWeek(week_repo=week_repo)
    week_id = await use_case.execute(
        CreateWeekCommand(
            space_id=SpaceId(space_id),
            week_start=body.week_start,
        )
    )
    week = await GetWeek(week_repo=week_repo).execute(
        GetWeekQuery(week_id=week_id)
    )
    return week_to_response(week)


@router.get("/{week_start}")
async def get_week(
    space_id: str,
    week_start: date_cls,
    week_repo=Depends(get_week_repo),
):
    use_case = GetWeek(week_repo=week_repo)
    week = await use_case.execute(
        GetWeekQuery(week_id=_week_id(space_id, week_start))
    )
    return week_to_response(week)


@router.put("/{week_start}/notes")
async def set_week_notes(
    space_id: str,
    week_start: date_cls,
    body: SetWeekNotesRequest,
    week_repo=Depends(get_week_repo),
):
    week_id = _week_id(space_id, week_start)
    await SetWeekNotes(week_repo=week_repo).execute(
        SetWeekNotesCommand(week_id=week_id, notes=body.notes)
    )
    week = await GetWeek(week_repo=week_repo).execute(
        GetWeekQuery(week_id=week_id)
    )
    return week_to_response(week)


@router.post("/{week_start}/apply-template")
async def apply_template_to_week(
    space_id: str,
    week_start: date_cls,
    body: ApplyTemplateToWeekRequest,
    week_repo=Depends(get_week_repo),
    week_template_repo=Depends(get_week_template_repo),
    day_template_repo=Depends(get_day_template_repo),
    day_repo=Depends(get_day_repo),
):
    week_id = _week_id(space_id, week_start)
    use_case = ApplyTemplateToWeek(
        week_repo=week_repo,
        week_template_repo=week_template_repo,
        day_template_repo=day_template_repo,
        day_repo=day_repo,
    )
    day_ids = await use_case.execute(
        ApplyTemplateToWeekCommand(
            week_id=week_id,
            template_id=WeekTemplateId(body.template_id),
            replace_existing=body.replace_existing,
        )
    )
    week = await GetWeek(week_repo=week_repo).execute(
        GetWeekQuery(week_id=week_id)
    )
    return {
        "week": week_to_response(week),
        "day_ids": [d.value for d in day_ids],
    }


@router.delete("/{week_start}", status_code=204)
async def delete_week(
    space_id: str,
    week_start: date_cls,
    week_repo=Depends(get_week_repo),
    day_repo=Depends(get_day_repo),
):
    use_case = DeleteWeek(week_repo=week_repo, day_repo=day_repo)
    await use_case.execute(
        DeleteWeekCommand(week_id=_week_id(space_id, week_start))
    )
    return Response(status_code=204)
