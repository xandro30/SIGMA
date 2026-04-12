from pydantic import BaseModel


class AreaCapacityResponse(BaseModel):
    area_id: str
    budget_minutes: int
    consumed_minutes: int
    remaining_minutes: int


class SpaceCapacityResponse(BaseModel):
    cycle_id: str
    date_range: dict[str, str]
    buffer_percentage: int
    areas: list[AreaCapacityResponse]


class CardEtaResponse(BaseModel):
    card_id: str
    estimated_minutes: int
    daily_capacity_minutes: int
    raw_completion_date: str
    buffered_completion_date: str
