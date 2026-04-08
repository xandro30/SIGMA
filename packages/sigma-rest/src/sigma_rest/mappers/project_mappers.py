from sigma_core.task_management.domain.entities.project import Project
from sigma_rest.schemas.project_schemas import ProjectResponse


def project_to_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id.value,
        name=project.name,
        description=project.description,
        objectives=project.objectives,
        area_id=project.area_id.value,
        status=project.status.value,
        created_at=project.created_at.value.isoformat(),
        updated_at=project.updated_at.value.isoformat(),
    )