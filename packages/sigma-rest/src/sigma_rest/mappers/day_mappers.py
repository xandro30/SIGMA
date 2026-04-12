from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_rest.schemas.day_schemas import DayResponse, TimeBlockResponse


def time_block_to_response(block: TimeBlock) -> TimeBlockResponse:
    return TimeBlockResponse(
        id=block.id.value,
        start_at=block.start_at.value.isoformat(),
        duration=block.duration.value,
        area_id=block.area_id.value if block.area_id is not None else None,
        notes=block.notes,
    )


def day_to_response(day: Day) -> DayResponse:
    return DayResponse(
        id=day.id.value,
        space_id=day.space_id.value,
        date=day.date,
        blocks=[time_block_to_response(b) for b in day.blocks],
        created_at=day.created_at.value.isoformat(),
        updated_at=day.updated_at.value.isoformat(),
    )
