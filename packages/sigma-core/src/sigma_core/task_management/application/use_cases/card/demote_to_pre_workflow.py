from dataclasses import dataclass
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.task_management.domain.errors import (
    CardNotFoundError, InboxNotAllowedError, InvalidTransitionError,
)
from sigma_core.task_management.domain.value_objects import CardId
from sigma_core.task_management.domain.ports.card_repository import CardRepository


@dataclass
class DemoteToPreWorkflowCommand:
    card_id: CardId
    stage: PreWorkflowStage = PreWorkflowStage.BACKLOG


class DemoteToPreWorkflow:
    def __init__(self, card_repo: CardRepository) -> None:
        self._card_repo = card_repo

    async def execute(self, cmd: DemoteToPreWorkflowCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        if card.workflow_state_id is None:
            raise InvalidTransitionError(
                "Card is not in workflow"
            )

        if cmd.stage == PreWorkflowStage.INBOX:
            raise InboxNotAllowedError(
                "Cannot demote to inbox — inbox is a one-way entry point."
            )

        card.move_to_pre_workflow(cmd.stage)
        await self._card_repo.save(card)