from dataclasses import dataclass
from sigma_core.task_management.domain.entities.area import Area
from sigma_core.task_management.domain.value_objects import AreaId
from sigma_core.task_management.domain.ports.area_repository import AreaRepository


@dataclass
class CreateAreaCommand:
    name: str
    color_id: str | None = None


class CreateArea:
    def __init__(self, area_repo: AreaRepository) -> None:
        self._area_repo = area_repo

    async def execute(self, cmd: CreateAreaCommand) -> AreaId:
        area = Area(id=AreaId.generate(), name=cmd.name, color_id=cmd.color_id)
        await self._area_repo.save(area)
        return area.id