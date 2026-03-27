from dataclasses import dataclass
from sigma_core.task_management.domain.errors import (
    CardNotFoundError, SpaceNotFoundError,
    InvalidTransitionError, StateNotFoundError,
)
from sigma_core.task_management.domain.value_objects import CardId, WorkflowStateId
from sigma_core.task_management.domain.aggregates.space import BEGIN_STATE_ID
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.ports.space_repository import SpaceRepository


@dataclass
class PromoteToWorkflowCommand:
    card_id: CardId
    target_state_id: WorkflowStateId | None = None


class PromoteToWorkflow:
    def __init__(self, card_repo: CardRepository, space_repo: SpaceRepository) -> None:
        self._card_repo = card_repo
        self._space_repo = space_repo

    async def execute(self, cmd: PromoteToWorkflowCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        if card.pre_workflow_stage is None:
            raise InvalidTransitionError(
                "Card is already in workflow"
            )

        space = await self._space_repo.get_by_id(card.space_id)
        if space is None:
            raise SpaceNotFoundError(card.space_id)

        target_id = cmd.target_state_id or BEGIN_STATE_ID

        if not space._state_exists(target_id):
            raise StateNotFoundError(target_id)

        card.move_to_workflow_state(target_id)
        await self._card_repo.save(card)