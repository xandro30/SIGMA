from dataclasses import dataclass
from sigma_core.task_management.domain.errors import SpaceNotFoundError
from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.task_management.domain.value_objects import WorkflowStateId
from sigma_core.task_management.domain.ports.space_repository import SpaceRepository


@dataclass
class AddTransitionCommand:
    space_id: SpaceId
    from_id: WorkflowStateId
    to_id: WorkflowStateId


class AddTransition:
    def __init__(self, space_repo: SpaceRepository) -> None:
        self._space_repo = space_repo

    async def execute(self, cmd: AddTransitionCommand) -> None:
        space = await self._space_repo.get_by_id(cmd.space_id)
        if space is None:
            raise SpaceNotFoundError(cmd.space_id)

        space.add_transition(cmd.from_id, cmd.to_id)
        await self._space_repo.save(space)