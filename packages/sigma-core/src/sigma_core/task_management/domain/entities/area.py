from dataclasses import dataclass, field
from sigma_core.shared_kernel.value_objects import AreaId, Timestamp


@dataclass
class Area:
    id: AreaId
    name: str
    description: str | None = None
    objectives: str | None = None
    color_id: str | None = None
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

    def update_objectives(self, objectives: str | None) -> None:
        self.objectives = objectives
        self.updated_at = Timestamp.now()

    def update_color(self, color_id: str | None) -> None:
        self.color_id = color_id
        self.updated_at = Timestamp.now()