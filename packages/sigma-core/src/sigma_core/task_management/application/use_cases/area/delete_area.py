from dataclasses import dataclass
from sigma_core.task_management.domain.errors import AreaNotFoundError
from sigma_core.task_management.domain.value_objects import AreaId
from sigma_core.task_management.domain.ports.area_repository import AreaRepository
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.ports.project_repository import ProjectRepository


@dataclass
class DeleteAreaCommand:
    area_id: AreaId


class DeleteArea:
    def __init__(self, area_repo: AreaRepository, card_repo: CardRepository, project_repo: ProjectRepository) -> None:
        self._area_repo = area_repo
        self._card_repo = card_repo
        self._project_repo = project_repo

    async def execute(self, cmd: DeleteAreaCommand) -> None:
        area = await self._area_repo.get_by_id(cmd.area_id)
        if area is None:
            raise AreaNotFoundError(cmd.area_id)

        cards = await self._card_repo.get_by_area(cmd.area_id)
        for card in cards:
            card.area_id = None
            card.project_id = None
            await self._card_repo.save(card)

        projects = await self._project_repo.get_by_area(cmd.area_id)
        for project in projects:
            await self._project_repo.delete(project.id)

        await self._area_repo.delete(cmd.area_id)