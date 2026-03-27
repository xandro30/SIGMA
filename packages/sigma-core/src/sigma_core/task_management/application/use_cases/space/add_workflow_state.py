from dataclasses import dataclass
from sigma_core.task_management.domain.aggregates.space import WorkflowState
from sigma_core.task_management.domain.errors import SpaceNotFoundError
from sigma_core.task_management.domain.value_objects import SpaceId, WorkflowStateId
from sigma_core.task_management.domain.ports.space_repository import SpaceRepository


@dataclass
class AddWorkflowStateCommand:
    space_id: SpaceId
    name: str
    order: int


class AddWorkflowState:
    def __init__(self, space_repo: SpaceRepository) -> None:
        self._space_repo = space_repo

    async def execute(self, cmd: AddWorkflowStateCommand) -> WorkflowStateId:
        space = await self._space_repo.get_by_id(cmd.space_id)
        if space is None:
            raise SpaceNotFoundError(cmd.space_id)

        state = WorkflowState(id=WorkflowStateId.generate(), name=cmd.name, order=cmd.order)
        space.add_state(state)
        await self._space_repo.save(space)
        return state.id