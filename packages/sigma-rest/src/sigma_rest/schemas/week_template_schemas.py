from pydantic import BaseModel, Field

from sigma_rest.schemas._limits import (
    MAX_NAME_LENGTH,
    MIN_NAME_LENGTH,
    UUID_STRING_LENGTH,
)


class CreateWeekTemplateRequest(BaseModel):
    name: str = Field(min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)


class SetWeekSlotRequest(BaseModel):
    day_template_id: str = Field(max_length=UUID_STRING_LENGTH)


class WeekTemplateResponse(BaseModel):
    id: str
    space_id: str
    name: str
    slots: dict[str, str | None]
    created_at: str
    updated_at: str
