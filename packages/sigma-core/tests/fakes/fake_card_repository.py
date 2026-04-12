from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.card_filter import CardFilter
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.shared_kernel.value_objects import CardId, SpaceId, AreaId
from sigma_core.task_management.domain.value_objects import (
    ProjectId,
    EpicId,
    WorkflowStateId,
)


class FakeCardRepository:
    def __init__(self) -> None:
        self._store: dict[str, Card] = {}

    async def save(self, card: Card) -> None:
        self._store[card.id.value] = card

    async def get_by_id(self, card_id: CardId) -> Card | None:
        return self._store.get(card_id.value)

    async def get_by_space(self, space_id: SpaceId, filter: CardFilter | None = None) -> list[Card]:
        cards = [c for c in self._store.values() if c.space_id == space_id]
        if filter:
            cards = [c for c in cards if filter.matches(c)]
        return cards

    async def get_by_pre_workflow_stage(self, space_id: SpaceId, stage: PreWorkflowStage) -> list[Card]:
        return [c for c in self._store.values()
                if c.space_id == space_id and c.pre_workflow_stage == stage]

    async def get_by_workflow_state(self, space_id: SpaceId, state_id: WorkflowStateId) -> list[Card]:
        return [c for c in self._store.values()
                if c.space_id == space_id and c.workflow_state_id == state_id]

    async def count_by_workflow_state(self, space_id: SpaceId, state_id: WorkflowStateId, filter: CardFilter | None = None) -> int:
        cards = await self.get_by_workflow_state(space_id, state_id)
        if filter:
            cards = [c for c in cards if filter.matches(c)]
        return len(cards)

    async def get_by_area(self, area_id: AreaId) -> list[Card]:
        return [c for c in self._store.values() if c.area_id == area_id]

    async def get_by_project(self, project_id: ProjectId) -> list[Card]:
        return [c for c in self._store.values() if c.project_id == project_id]

    async def get_by_epic(self, epic_id: EpicId) -> list[Card]:
        return [c for c in self._store.values() if c.epic_id == epic_id]

    async def delete(self, card_id: CardId) -> None:
        self._store.pop(card_id.value, None)