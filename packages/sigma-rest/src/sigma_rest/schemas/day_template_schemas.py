from datetime import date

from pydantic import BaseModel, Field

from sigma_rest.schemas._limits import (
    MAX_NAME_LENGTH,
    MAX_NOTES_LENGTH,
    MIN_NAME_LENGTH,
    UUID_STRING_LENGTH,
)


class TimeOfDaySchema(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)


class DayTemplateBlockSpecSchema(BaseModel):
    start_at: TimeOfDaySchema
    duration: int = Field(gt=0)
    area_id: str | None = Field(default=None, max_length=UUID_STRING_LENGTH)
    notes: str = Field(default="", max_length=MAX_NOTES_LENGTH)


class DayTemplateBlockResponse(BaseModel):
    id: str
    start_at: TimeOfDaySchema
    duration: int
    area_id: str | None = None
    notes: str = ""


class CreateDayTemplateRequest(BaseModel):
    name: str = Field(min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    blocks: list[DayTemplateBlockSpecSchema] = Field(default_factory=list)


class UpdateDayTemplateRequest(BaseModel):
    name: str = Field(min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    blocks: list[DayTemplateBlockSpecSchema] = Field(default_factory=list)


class ApplyDayTemplateRequest(BaseModel):
    target_date: date
    replace_existing: bool = False


class DayTemplateResponse(BaseModel):
    id: str
    space_id: str
    name: str
    blocks: list[DayTemplateBlockResponse]
    created_at: str
    updated_at: str
