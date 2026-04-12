from sigma_core.planning.domain.aggregates.week import Week
from sigma_rest.schemas.week_schemas import WeekResponse


def week_to_response(week: Week) -> WeekResponse:
    return WeekResponse(
        id=week.id.value,
        space_id=week.space_id.value,
        week_start=week.week_start,
        applied_template_id=(
            week.applied_template_id.value
            if week.applied_template_id is not None
            else None
        ),
        notes=week.notes,
        created_at=week.created_at.value.isoformat(),
        updated_at=week.updated_at.value.isoformat(),
    )
