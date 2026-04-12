from datetime import date

from pydantic import BaseModel, Field

from sigma_rest.schemas._limits import MAX_NOTES_LENGTH, UUID_STRING_LENGTH


class CreateWeekRequest(BaseModel):
    week_start: date


class SetWeekNotesRequest(BaseModel):
    notes: str = Field(max_length=MAX_NOTES_LENGTH)


class ApplyTemplateToWeekRequest(BaseModel):
    template_id: str = Field(max_length=UUID_STRING_LENGTH)
    replace_existing: bool = False


class WeekResponse(BaseModel):
    id: str
    space_id: str
    week_start: date
    applied_template_id: str | None = None
    notes: str
    created_at: str
    updated_at: str
