from dataclasses import dataclass
from sigma_core.task_management.domain.aggregates.space import Space
from sigma_core.task_management.domain.value_objects import SpaceId, SpaceName
from sigma_core.task_management.domain.ports.space_repository import SpaceRepository


@dataclass
class CreateSpaceCommand:
    name: SpaceName


class CreateSpace:
    def __init__(self, space_repo: SpaceRepository) -> None:
        self._space_repo = space_repo

    async def execute(self, cmd: CreateSpaceCommand) -> SpaceId:
        space = Space(id=SpaceId.generate(), name=cmd.name)
        await self._space_repo.save(space)
        return space.id