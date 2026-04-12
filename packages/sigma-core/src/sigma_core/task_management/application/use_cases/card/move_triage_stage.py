from dataclasses import dataclass

from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.task_management.domain.errors import (
    CardNotFoundError,
    CardNotInTriageError,
    AlreadyInStageError,
    InboxNotAllowedError,
)
from sigma_core.shared_kernel.value_objects import CardId
from sigma_core.task_management.domain.ports.card_repository import CardRepository


@dataclass
class MoveTriageStageCommand:
    card_id: CardId
    target_stage: PreWorkflowStage


class MoveTriageStage:
    def __init__(self, card_repository: CardRepository) -> None:
        self._repo = card_repository

    async def execute(self, cmd: MoveTriageStageCommand) -> None:
        card = await self._repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        if card.pre_workflow_stage is None:
            raise CardNotInTriageError(
                f"Card '{cmd.card_id}' is in workflow. Use /demote to move it to Triage."
            )

        if card.pre_workflow_stage == cmd.target_stage:
            raise AlreadyInStageError(
                f"Card is already in stage '{cmd.target_stage.value}'."
            )

        if cmd.target_stage == PreWorkflowStage.INBOX and card.pre_workflow_stage != PreWorkflowStage.INBOX:
            raise InboxNotAllowedError(
                "A card that has left Inbox cannot return to it."
            )

        card.pre_workflow_stage = cmd.target_stage
        await self._repo.save(card)
