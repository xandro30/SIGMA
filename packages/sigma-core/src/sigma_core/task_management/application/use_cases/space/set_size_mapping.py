from dataclasses import dataclass

from sigma_core.task_management.domain.errors import SpaceNotFoundError
from sigma_core.shared_kernel.value_objects import SpaceId, SizeMapping
from sigma_core.task_management.domain.ports.space_repository import SpaceRepository


@dataclass
class SetSizeMappingCommand:
    space_id: SpaceId
    mapping: SizeMapping | None


class SetSizeMapping:
    def __init__(self, space_repo: SpaceRepository) -> None:
        self._space_repo = space_repo

    async def execute(self, cmd: SetSizeMappingCommand) -> None:
        space = await self._space_repo.get_by_id(cmd.space_id)
        if space is None:
            raise SpaceNotFoundError(cmd.space_id)

        space.set_size_mapping(cmd.mapping)
        await self._space_repo.save(space)
