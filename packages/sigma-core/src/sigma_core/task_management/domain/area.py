from dataclasses import dataclass, field
from sigma_core.task_management.domain.value_objects import AreaId, Timestamp


@dataclass
class Area:
    id: AreaId
    name: str
    description: str | None = None
    objectives: list[str] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)


    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Area name cannot be empty")

    def rename(self, name: str) -> None:
        if not name.strip():
            raise ValueError("Area name cannot be empty")
        self.name = name.strip()
        self.updated_at = Timestamp.now()

    def update_description(self, description: str | None) -> None:
        self.description = description
        self.updated_at = Timestamp.now()

    def add_objective(self, objective: str) -> None:
        if objective not in self.objectives:
            self.objectives.append(objective)
            self.updated_at = Timestamp.now()

    def remove_objective(self, objective: str) -> None:
        self.objectives = [o for o in self.objectives if o != objective]
        self.updated_at = Timestamp.now()