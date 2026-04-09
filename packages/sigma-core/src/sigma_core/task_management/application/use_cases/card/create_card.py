from dataclasses import dataclass, field
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.enums import PreWorkflowStage, Priority
from sigma_core.task_management.domain.errors import SpaceNotFoundError
from sigma_core.task_management.domain.value_objects import (
    CardId, SpaceId, CardTitle, WorkflowStateId, AreaId, ProjectId, EpicId,
)
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.ports.space_repository import SpaceRepository


@dataclass
class CreateCardCommand:
    space_id: SpaceId
    title: CardTitle
    initial_stage: PreWorkflowStage | WorkflowStateId = PreWorkflowStage.INBOX
    area_id: AreaId | None = None
    project_id: ProjectId | None = None
    epic_id: EpicId | None = None
    priority: Priority | None = None
    labels: set[str] = field(default_factory=set)


class CreateCard:
    def __init__(self, card_repo: CardRepository, space_repo: SpaceRepository) -> None:
        self._card_repo = card_repo
        self._space_repo = space_repo

    async def execute(self, cmd: CreateCardCommand) -> CardId:
        space = await self._space_repo.get_by_id(cmd.space_id)
        if space is None:
            raise SpaceNotFoundError(cmd.space_id)

        if isinstance(cmd.initial_stage, WorkflowStateId):
            card = Card(
                id=CardId.generate(),
                space_id=cmd.space_id,
                title=cmd.title,
                pre_workflow_stage=None,
                workflow_state_id=cmd.initial_stage,
                area_id=cmd.area_id,
                project_id=cmd.project_id,
                epic_id=cmd.epic_id,
                priority=cmd.priority,
                labels=cmd.labels,
            )
        else:
            card = Card(
                id=CardId.generate(),
                space_id=cmd.space_id,
                title=cmd.title,
                pre_workflow_stage=cmd.initial_stage,
                workflow_state_id=None,
                area_id=cmd.area_id,
                project_id=cmd.project_id,
                epic_id=cmd.epic_id,
                priority=cmd.priority,
                labels=cmd.labels,
            )

        await self._card_repo.save(card)
        return card.id
