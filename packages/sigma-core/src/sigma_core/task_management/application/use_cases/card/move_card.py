from dataclasses import dataclass
from sigma_core.task_management.domain.errors import (
    CardNotFoundError,
    SpaceNotFoundError,
    InvalidTransitionError,
)
from sigma_core.shared_kernel.value_objects import CardId
from sigma_core.task_management.domain.value_objects import WorkflowStateId
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.ports.space_repository import SpaceRepository


@dataclass
class MoveCardCommand:
    card_id: CardId
    target_state_id: WorkflowStateId


class MoveCard:
    def __init__(self, card_repo: CardRepository, space_repo: SpaceRepository) -> None:
        self._card_repo = card_repo
        self._space_repo = space_repo

    async def execute(self, cmd: MoveCardCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        space = await self._space_repo.get_by_id(card.space_id)
        if space is None:
            raise SpaceNotFoundError(card.space_id)

        if card.workflow_state_id is None:
            raise InvalidTransitionError(
                "Card is not in workflow — use PromoteToWorkflow instead"
            )

        if not space.is_valid_transition(card.workflow_state_id, cmd.target_state_id):
            raise InvalidTransitionError(
                f"Transition from {card.workflow_state_id} to {cmd.target_state_id} is not allowed"
            )

        card.move_to_workflow_state(cmd.target_state_id)
        await self._card_repo.save(card)