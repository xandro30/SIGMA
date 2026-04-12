from pydantic import BaseModel


class CalibrationEntryResponse(BaseModel):
    card_id: str
    estimated_minutes: int
    actual_minutes: int


class MetricsBlockResponse(BaseModel):
    total_cards_completed: int
    avg_cycle_time_minutes: float | None = None
    avg_lead_time_minutes: float | None = None
    consumed_minutes: int
    calibration_entries: list[CalibrationEntryResponse]


class ProjectMetricsResponse(BaseModel):
    project_id: str
    metrics: MetricsBlockResponse
    epics: dict[str, MetricsBlockResponse]


class AreaMetricsResponse(BaseModel):
    area_id: str
    budget_minutes: int
    metrics: MetricsBlockResponse
    projects: dict[str, ProjectMetricsResponse]


class MetricsResponse(BaseModel):
    cycle_id: str
    space_id: str
    date_range: dict[str, str]
    computed_at: str
    source: str
    global_metrics: MetricsBlockResponse
    areas: dict[str, AreaMetricsResponse]


class CardSnapshotResponse(BaseModel):
    card_id: str
    area_id: str | None = None
    project_id: str | None = None
    epic_id: str | None = None
    size: str | None = None
    actual_time_minutes: int
    created_at: str
    entered_workflow_at: str | None = None
    completed_at: str


class SnapshotResponse(BaseModel):
    id: str
    cycle_id: str
    space_id: str
    date_range: dict[str, str]
    buffer_percentage: int
    area_budgets: dict[str, int]
    size_mapping: dict[str, int] | None = None
    cards: list[CardSnapshotResponse]
    created_at: str
