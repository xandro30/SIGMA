from dataclasses import dataclass
from sigma_core.task_management.domain.errors import AreaNotFoundError
from sigma_core.task_management.domain.value_objects import AreaId
from sigma_core.task_management.domain.ports.area_repository import AreaRepository


@dataclass
class UpdateAreaCommand:
    area_id: AreaId
    name: str | None = None
    description: str | None = None
    objectives: str | None = None
    color_id: str | None = None


class UpdateArea:
    def __init__(self, area_repo: AreaRepository) -> None:
        self._area_repo = area_repo

    async def execute(self, cmd: UpdateAreaCommand) -> None:
        area = await self._area_repo.get_by_id(cmd.area_id)
        if area is None:
            raise AreaNotFoundError(cmd.area_id)

        if cmd.name is not None:
            area.rename(cmd.name)
        if cmd.description is not None:
            area.update_description(cmd.description)
        if cmd.objectives is not None:
            area.update_objectives(cmd.objectives)
        if cmd.color_id is not None:
            area.update_color(cmd.color_id)

        await self._area_repo.save(area)