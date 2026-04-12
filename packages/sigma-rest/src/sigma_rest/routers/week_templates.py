from fastapi import APIRouter, Depends, HTTPException, Response

from sigma_core.planning.application.use_cases.week_template.clear_slot import (
    ClearWeekTemplateSlot,
    ClearWeekTemplateSlotCommand,
)
from sigma_core.planning.application.use_cases.week_template.create_week_template import (
    CreateWeekTemplate,
    CreateWeekTemplateCommand,
)
from sigma_core.planning.application.use_cases.week_template.delete_week_template import (
    DeleteWeekTemplate,
    DeleteWeekTemplateCommand,
)
from sigma_core.planning.application.use_cases.week_template.set_slot import (
    SetWeekTemplateSlot,
    SetWeekTemplateSlotCommand,
)
from sigma_core.planning.domain.value_objects import (
    DayTemplateId,
    WeekTemplateId,
)
from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_rest.dependencies import (
    get_day_template_repo,
    get_week_template_repo,
)
from sigma_rest.mappers.week_template_mappers import (
    DOW_FROM_NAME,
    week_template_to_response,
)
from sigma_rest.routers._helpers import require_week_template
from sigma_rest.schemas.week_template_schemas import (
    CreateWeekTemplateRequest,
    SetWeekSlotRequest,
)


router = APIRouter(
    prefix="/spaces/{space_id}/week-templates", tags=["week-templates"]
)


def _parse_dow(weekday: str):
    try:
        return DOW_FROM_NAME[weekday.lower()]
    except KeyError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "invalid_weekday",
                "message": f"weekday must be one of {list(DOW_FROM_NAME)}",
            },
        ) from exc


@router.post("", status_code=201)
async def create_week_template(
    space_id: str,
    body: CreateWeekTemplateRequest,
    week_template_repo=Depends(get_week_template_repo),
):
    use_case = CreateWeekTemplate(week_template_repo)
    template_id = await use_case.execute(
        CreateWeekTemplateCommand(
            space_id=SpaceId(space_id),
            name=body.name,
        )
    )
    template = await require_week_template(week_template_repo, template_id)
    return week_template_to_response(template)


@router.get("")
async def list_week_templates(
    space_id: str,
    week_template_repo=Depends(get_week_template_repo),
):
    templates = await week_template_repo.list_by_space(SpaceId(space_id))
    return {"templates": [week_template_to_response(t) for t in templates]}


@router.get("/{template_id}")
async def get_week_template(
    space_id: str,
    template_id: str,
    week_template_repo=Depends(get_week_template_repo),
):
    template = await require_week_template(
        week_template_repo, WeekTemplateId(template_id)
    )
    return week_template_to_response(template)


@router.delete("/{template_id}", status_code=204)
async def delete_week_template(
    space_id: str,
    template_id: str,
    week_template_repo=Depends(get_week_template_repo),
):
    use_case = DeleteWeekTemplate(week_template_repo)
    await use_case.execute(
        DeleteWeekTemplateCommand(template_id=WeekTemplateId(template_id))
    )
    return Response(status_code=204)


@router.put("/{template_id}/slots/{weekday}")
async def set_week_slot(
    space_id: str,
    template_id: str,
    weekday: str,
    body: SetWeekSlotRequest,
    week_template_repo=Depends(get_week_template_repo),
    day_template_repo=Depends(get_day_template_repo),
):
    dow = _parse_dow(weekday)
    use_case = SetWeekTemplateSlot(week_template_repo, day_template_repo)
    await use_case.execute(
        SetWeekTemplateSlotCommand(
            week_template_id=WeekTemplateId(template_id),
            day=dow,
            day_template_id=DayTemplateId(body.day_template_id),
        )
    )
    template = await require_week_template(
        week_template_repo, WeekTemplateId(template_id)
    )
    return week_template_to_response(template)


@router.delete("/{template_id}/slots/{weekday}")
async def clear_week_slot(
    space_id: str,
    template_id: str,
    weekday: str,
    week_template_repo=Depends(get_week_template_repo),
):
    dow = _parse_dow(weekday)
    use_case = ClearWeekTemplateSlot(week_template_repo)
    await use_case.execute(
        ClearWeekTemplateSlotCommand(
            week_template_id=WeekTemplateId(template_id),
            day=dow,
        )
    )
    template = await require_week_template(
        week_template_repo, WeekTemplateId(template_id)
    )
    return week_template_to_response(template)


# Nota: la antigua ruta POST /week-templates/{id}/apply se ha eliminado.
# La aplicación de un WeekTemplate pasa ahora por el agregado Week:
# POST /v1/spaces/{space_id}/weeks/{week_start}/apply-template
# (ver ``routers/weeks.py``).
