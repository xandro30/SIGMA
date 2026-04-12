from dataclasses import dataclass, field

from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.ports.day_template_repository import (
    DayTemplateRepository,
)
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DayTemplateId,
    TimeOfDay,
)
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId


@dataclass
class DayTemplateBlockSpec:
    start_at: TimeOfDay
    duration: Minutes
    area_id: AreaId | None
    notes: str = ""


@dataclass
class CreateDayTemplateCommand:
    space_id: SpaceId
    name: str
    blocks: list[DayTemplateBlockSpec] = field(default_factory=list)


class CreateDayTemplate:
    def __init__(self, day_template_repo: DayTemplateRepository) -> None:
        self._repo = day_template_repo

    async def execute(self, cmd: CreateDayTemplateCommand) -> DayTemplateId:
        template = DayTemplate(
            id=DayTemplateId.generate(),
            space_id=cmd.space_id,
            name=cmd.name,
        )
        blocks = [
            DayTemplateBlock(
                id=BlockId.generate(),
                start_at=spec.start_at,
                duration=spec.duration,
                area_id=spec.area_id,
                notes=spec.notes,
            )
            for spec in cmd.blocks
        ]
        template.replace_blocks(blocks)
        await self._repo.save(template)
        return template.id
