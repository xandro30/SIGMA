from datetime import date

from pydantic import BaseModel, Field

from sigma_rest.schemas._limits import (
    MAX_NAME_LENGTH,
    MIN_NAME_LENGTH,
    UUID_STRING_LENGTH,
)  # noqa: F401  (UUID_STRING_LENGTH usado abajo en SetAreaBudgetRequest)


class DateRangeSchema(BaseModel):
    start: date
    end: date


class CreateCycleRequest(BaseModel):
    name: str = Field(min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    date_range: DateRangeSchema
    buffer_percentage: int | None = Field(default=None, ge=0, le=100)


class SetAreaBudgetRequest(BaseModel):
    area_id: str = Field(max_length=UUID_STRING_LENGTH)
    minutes: int = Field(ge=0)


class SetBufferPercentageRequest(BaseModel):
    buffer_percentage: int = Field(ge=0, le=100)


class AreaBudgetResponse(BaseModel):
    area_id: str
    minutes: int


class CycleResponse(BaseModel):
    id: str
    space_id: str
    name: str
    date_range: DateRangeSchema
    state: str
    area_budgets: list[AreaBudgetResponse]
    buffer_percentage: int
    created_at: str
    updated_at: str
    closed_at: str | None = None
