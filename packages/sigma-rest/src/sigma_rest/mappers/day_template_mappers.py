from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_rest.schemas.day_template_schemas import (
    DayTemplateBlockResponse,
    DayTemplateResponse,
    TimeOfDaySchema,
)


def day_template_block_to_response(
    block: DayTemplateBlock,
) -> DayTemplateBlockResponse:
    return DayTemplateBlockResponse(
        id=block.id.value,
        start_at=TimeOfDaySchema(
            hour=block.start_at.hour,
            minute=block.start_at.minute,
        ),
        duration=block.duration.value,
        area_id=block.area_id.value if block.area_id is not None else None,
        notes=block.notes,
    )


def day_template_to_response(template: DayTemplate) -> DayTemplateResponse:
    return DayTemplateResponse(
        id=template.id.value,
        space_id=template.space_id.value,
        name=template.name,
        blocks=[day_template_block_to_response(b) for b in template.blocks],
        created_at=template.created_at.value.isoformat(),
        updated_at=template.updated_at.value.isoformat(),
    )
