from dataclasses import dataclass, field

from sigma_core.planning.application.use_cases.day_template.create_day_template import (
    DayTemplateBlockSpec,
)
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.errors import DayTemplateNotFoundError
from sigma_core.planning.domain.ports.day_template_repository import (
    DayTemplateRepository,
)
from sigma_core.planning.domain.value_objects import BlockId, DayTemplateId


@dataclass
class UpdateDayTemplateCommand:
    template_id: DayTemplateId
    name: str
    blocks: list[DayTemplateBlockSpec] = field(default_factory=list)


class UpdateDayTemplate:
    """Reemplaza atomicamente nombre y lista de bloques de un `DayTemplate`."""

    def __init__(self, day_template_repo: DayTemplateRepository) -> None:
        self._repo = day_template_repo

    async def execute(self, cmd: UpdateDayTemplateCommand) -> None:
        template = await self._repo.get_by_id(cmd.template_id)
        if template is None:
            raise DayTemplateNotFoundError(
                f"DayTemplate {cmd.template_id.value} not found"
            )
        new_blocks = [
            DayTemplateBlock(
                id=BlockId.generate(),
                start_at=spec.start_at,
                duration=spec.duration,
                area_id=spec.area_id,
                notes=spec.notes,
            )
            for spec in cmd.blocks
        ]
        template.rename(cmd.name)
        template.replace_blocks(new_blocks)
        await self._repo.save(template)
