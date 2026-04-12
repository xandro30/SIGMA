from datetime import date, datetime

from pydantic import BaseModel, Field

from sigma_rest.schemas._limits import MAX_NOTES_LENGTH, UUID_STRING_LENGTH


class CreateDayRequest(BaseModel):
    date: date


class TimeBlockResponse(BaseModel):
    id: str
    start_at: str
    duration: int
    area_id: str | None = None
    notes: str = ""


class DayResponse(BaseModel):
    id: str
    space_id: str
    date: date
    blocks: list[TimeBlockResponse]
    created_at: str
    updated_at: str


class AddBlockRequest(BaseModel):
    start_at: datetime
    duration: int = Field(gt=0)
    area_id: str | None = Field(default=None, max_length=UUID_STRING_LENGTH)
    notes: str = Field(default="", max_length=MAX_NOTES_LENGTH)


class UpdateBlockRequest(BaseModel):
    start_at: datetime | None = None
    duration: int | None = Field(default=None, gt=0)
    # `area_id_set` permite distinguir "no tocar" de "poner a None"
    area_id_set: bool = False
    area_id: str | None = Field(default=None, max_length=UUID_STRING_LENGTH)
    notes: str | None = Field(default=None, max_length=MAX_NOTES_LENGTH)
