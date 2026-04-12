from fastapi import APIRouter, Depends, Response

from sigma_core.planning.application.use_cases.day_template.apply_template_to_day import (
    ApplyDayTemplateToDay,
    ApplyDayTemplateToDayCommand,
)
from sigma_core.planning.application.use_cases.day_template.create_day_template import (
    CreateDayTemplate,
    CreateDayTemplateCommand,
    DayTemplateBlockSpec,
)
from sigma_core.planning.application.use_cases.day_template.delete_day_template import (
    DeleteDayTemplate,
    DeleteDayTemplateCommand,
)
from sigma_core.planning.application.use_cases.day_template.update_day_template import (
    UpdateDayTemplate,
    UpdateDayTemplateCommand,
)
from sigma_core.planning.domain.value_objects import (
    DayTemplateId,
    TimeOfDay,
)
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId
from sigma_rest.dependencies import get_day_repo, get_day_template_repo
from sigma_rest.mappers.day_template_mappers import day_template_to_response
from sigma_rest.routers._helpers import require_day_template
from sigma_rest.schemas.day_template_schemas import (
    ApplyDayTemplateRequest,
    CreateDayTemplateRequest,
    DayTemplateBlockSpecSchema,
    UpdateDayTemplateRequest,
)


router = APIRouter(
    prefix="/spaces/{space_id}/day-templates", tags=["day-templates"]
)


def _specs(
    specs: list[DayTemplateBlockSpecSchema],
) -> list[DayTemplateBlockSpec]:
    return [
        DayTemplateBlockSpec(
            start_at=TimeOfDay(hour=s.start_at.hour, minute=s.start_at.minute),
            duration=Minutes(s.duration),
            area_id=AreaId(s.area_id) if s.area_id else None,
            notes=s.notes,
        )
        for s in specs
    ]


@router.post("", status_code=201)
async def create_day_template(
    space_id: str,
    body: CreateDayTemplateRequest,
    day_template_repo=Depends(get_day_template_repo),
):
    use_case = CreateDayTemplate(day_template_repo)
    template_id = await use_case.execute(
        CreateDayTemplateCommand(
            space_id=SpaceId(space_id),
            name=body.name,
            blocks=_specs(body.blocks),
        )
    )
    template = await require_day_template(day_template_repo, template_id)
    return day_template_to_response(template)


@router.get("")
async def list_day_templates(
    space_id: str,
    day_template_repo=Depends(get_day_template_repo),
):
    templates = await day_template_repo.list_by_space(SpaceId(space_id))
    return {"templates": [day_template_to_response(t) for t in templates]}


@router.get("/{template_id}")
async def get_day_template(
    space_id: str,
    template_id: str,
    day_template_repo=Depends(get_day_template_repo),
):
    template = await require_day_template(
        day_template_repo, DayTemplateId(template_id)
    )
    return day_template_to_response(template)


@router.put("/{template_id}")
async def update_day_template(
    space_id: str,
    template_id: str,
    body: UpdateDayTemplateRequest,
    day_template_repo=Depends(get_day_template_repo),
):
    use_case = UpdateDayTemplate(day_template_repo)
    await use_case.execute(
        UpdateDayTemplateCommand(
            template_id=DayTemplateId(template_id),
            name=body.name,
            blocks=_specs(body.blocks),
        )
    )
    template = await require_day_template(
        day_template_repo, DayTemplateId(template_id)
    )
    return day_template_to_response(template)


@router.delete("/{template_id}", status_code=204)
async def delete_day_template(
    space_id: str,
    template_id: str,
    day_template_repo=Depends(get_day_template_repo),
):
    use_case = DeleteDayTemplate(day_template_repo)
    await use_case.execute(
        DeleteDayTemplateCommand(template_id=DayTemplateId(template_id))
    )
    return Response(status_code=204)


@router.post("/{template_id}/apply")
async def apply_day_template(
    space_id: str,
    template_id: str,
    body: ApplyDayTemplateRequest,
    day_template_repo=Depends(get_day_template_repo),
    day_repo=Depends(get_day_repo),
):
    use_case = ApplyDayTemplateToDay(day_template_repo, day_repo)
    day_id = await use_case.execute(
        ApplyDayTemplateToDayCommand(
            template_id=DayTemplateId(template_id),
            space_id=SpaceId(space_id),
            target_date=body.target_date,
            replace_existing=body.replace_existing,
        )
    )
    return {"day_id": day_id.value}
