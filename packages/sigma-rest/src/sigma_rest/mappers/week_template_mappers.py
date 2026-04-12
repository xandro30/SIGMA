from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.enums import DayOfWeek
from sigma_rest.schemas.week_template_schemas import WeekTemplateResponse


_DOW_NAMES: dict[DayOfWeek, str] = {
    DayOfWeek.MONDAY: "mon",
    DayOfWeek.TUESDAY: "tue",
    DayOfWeek.WEDNESDAY: "wed",
    DayOfWeek.THURSDAY: "thu",
    DayOfWeek.FRIDAY: "fri",
    DayOfWeek.SATURDAY: "sat",
    DayOfWeek.SUNDAY: "sun",
}

DOW_FROM_NAME: dict[str, DayOfWeek] = {v: k for k, v in _DOW_NAMES.items()}


def week_template_to_response(template: WeekTemplate) -> WeekTemplateResponse:
    slots: dict[str, str | None] = {}
    for dow, name in _DOW_NAMES.items():
        slot = template.slots.get(dow)
        slots[name] = slot.value if slot is not None else None
    return WeekTemplateResponse(
        id=template.id.value,
        space_id=template.space_id.value,
        name=template.name,
        slots=slots,
        created_at=template.created_at.value.isoformat(),
        updated_at=template.updated_at.value.isoformat(),
    )
