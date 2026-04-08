from sigma_core.task_management.domain.entities.area import Area
from sigma_rest.schemas.area_schemas import AreaResponse


def area_to_response(area: Area) -> AreaResponse:
    return AreaResponse(
        id=area.id.value,
        name=area.name,
        description=area.description,
        objectives=area.objectives,
        created_at=area.created_at.value.isoformat(),
        updated_at=area.updated_at.value.isoformat(),
    )