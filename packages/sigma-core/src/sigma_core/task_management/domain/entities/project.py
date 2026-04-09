from dataclasses import dataclass, field
from sigma_core.task_management.domain.enums import ProjectStatus
from sigma_core.task_management.domain.value_objects import (
    ProjectId, AreaId, Timestamp,
)


@dataclass
class Project:
    id: ProjectId
    name: str
    area_id: AreaId
    status: ProjectStatus
    description: str | None = None
    objectives: str | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)


    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Project name cannot be empty")

    def rename(self, name: str) -> None:
        if not name.strip():
            raise ValueError("Project name cannot be empty")
        self.name = name.strip()
        self.updated_at = Timestamp.now()

    def update_description(self, description: str | None) -> None:
        self.description = description
        self.updated_at = Timestamp.now()

    def update_objectives(self, objectives: str | None) -> None:
        self.objectives = objectives
        self.updated_at = Timestamp.now()

    def change_status(self, status: ProjectStatus) -> None:
        self.status = status
        self.updated_at = Timestamp.now()

    def reassign_area(self, area_id: AreaId) -> None:
        self.area_id = area_id
        self.updated_at = Timestamp.now()