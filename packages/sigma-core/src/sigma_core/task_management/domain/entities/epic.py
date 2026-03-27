from dataclasses import dataclass, field
from sigma_core.task_management.domain.value_objects import (
    EpicId, SpaceId, ProjectId, AreaId, Timestamp,
)


@dataclass
class Epic:
    id: EpicId
    space_id: SpaceId
    area_id: AreaId
    project_id: ProjectId
    name: str
    description: str | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)


    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Epic name cannot be empty")

    def rename(self, name: str) -> None:
        if not name.strip():
            raise ValueError("Epic name cannot be empty")
        self.name = name.strip()
        self.updated_at = Timestamp.now()

    def update_description(self, description: str | None) -> None:
        self.description = description
        self.updated_at = Timestamp.now()