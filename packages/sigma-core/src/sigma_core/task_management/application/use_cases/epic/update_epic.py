from dataclasses import dataclass
from sigma_core.task_management.domain.errors import EpicNotFoundError
from sigma_core.task_management.domain.value_objects import EpicId
from sigma_core.task_management.domain.ports.epic_repository import EpicRepository


@dataclass
class UpdateEpicCommand:
    epic_id: EpicId
    name: str | None = None
    description: str | None = None


class UpdateEpic:
    def __init__(self, epic_repo: EpicRepository) -> None:
        self._epic_repo = epic_repo

    async def execute(self, cmd: UpdateEpicCommand) -> None:
        epic = await self._epic_repo.get_by_id(cmd.epic_id)
        if epic is None:
            raise EpicNotFoundError(cmd.epic_id)

        if cmd.name is not None:
            epic.rename(cmd.name)
        if cmd.description is not None:
            epic.update_description(cmd.description)

        await self._epic_repo.save(epic)