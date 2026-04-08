from sigma_core.task_management.domain.entities.epic import Epic
from sigma_rest.schemas.epic_schemas import EpicResponse


def epic_to_response(epic: Epic) -> EpicResponse:
    return EpicResponse(
        id=epic.id.value,
        space_id=epic.space_id.value,
        project_id=epic.project_id.value,
        area_id=epic.area_id.value,
        name=epic.name,
        description=epic.description,
        created_at=epic.created_at.value.isoformat(),
        updated_at=epic.updated_at.value.isoformat(),
    )