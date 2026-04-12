from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_rest.schemas.cycle_schemas import (
    AreaBudgetResponse,
    CycleResponse,
    DateRangeSchema,
)


def cycle_to_response(cycle: Cycle) -> CycleResponse:
    return CycleResponse(
        id=cycle.id.value,
        space_id=cycle.space_id.value,
        name=cycle.name,
        cycle_type=cycle.cycle_type.value,
        date_range=DateRangeSchema(
            start=cycle.date_range.start, end=cycle.date_range.end
        ),
        state=cycle.state.value,
        area_budgets=[
            AreaBudgetResponse(area_id=a.value, minutes=m.value)
            for a, m in cycle.area_budgets.items()
        ],
        buffer_percentage=cycle.buffer_percentage,
        created_at=cycle.created_at.value.isoformat(),
        updated_at=cycle.updated_at.value.isoformat(),
        closed_at=(
            cycle.closed_at.value.isoformat()
            if cycle.closed_at is not None
            else None
        ),
    )
