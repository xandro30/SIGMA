from dataclasses import dataclass
from sigma_core.task_management.domain.errors import SpaceNotFoundError
from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.task_management.domain.value_objects import WorkflowStateId
from sigma_core.task_management.domain.ports.space_repository import SpaceRepository


@dataclass
class RemoveWorkflowStateCommand:
    space_id: SpaceId
    state_id: WorkflowStateId


class RemoveWorkflowState:
    def __init__(self, space_repo: SpaceRepository) -> None:
        self._space_repo = space_repo

    async def execute(self, cmd: RemoveWorkflowStateCommand) -> None:
        space = await self._space_repo.get_by_id(cmd.space_id)
        if space is None:
            raise SpaceNotFoundError(cmd.space_id)

        space.remove_state(cmd.state_id)
        await self._space_repo.save(space)