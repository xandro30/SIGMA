from google.cloud.firestore import AsyncClient, async_transactional
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.card_filter import CardFilter
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.shared_kernel.value_objects import CardId, SpaceId, AreaId
from sigma_core.task_management.domain.value_objects import (
    ProjectId,
    EpicId,
    WorkflowStateId,
)
from sigma_core.task_management.infrastructure.firestore.mappers import (
    card_to_dict, card_from_dict, snapshot_data,
)


class FirestoreCardRepository:
    COLLECTION = "cards"
    INDEX_COLLECTION = "card_indexes"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    def _card_ref(self, card_id: str):
        return self._client.collection(self.COLLECTION).document(card_id)

    def _index_ref(self, space_id: str, state_key: str, card_id: str):
        return (
            self._client
            .collection(self.INDEX_COLLECTION)
            .document(space_id)
            .collection("by_state")
            .document(f"{state_key}_{card_id}")
        )

    def _state_key(self, card: Card) -> str:
        if card.pre_workflow_stage:
            return card.pre_workflow_stage.value
        if card.workflow_state_id is None:
            raise ValueError(
                f"Card {card.id.value} has neither pre_workflow_stage nor workflow_state_id"
            )
        return card.workflow_state_id.value

    async def save(self, card: Card) -> None:
        await self._card_ref(card.id.value).set(card_to_dict(card))

    async def save_with_index(self, card: Card, old_state_key: str | None = None) -> None:
        """Guarda card y actualiza card_indexes en transacción atómica."""
        transaction = self._client.transaction()

        @async_transactional
        async def _update(transaction, card, old_state_key):
            new_state_key = self._state_key(card)

            transaction.set(self._card_ref(card.id.value), card_to_dict(card))

            index_data = {
                "card_id": card.id.value,
                "title": card.title.value,
                "priority": card.priority.value if card.priority else None,
                "due_date": card.due_date.isoformat() if card.due_date else None,
                "labels": list(card.labels),
                "epic_id": card.epic_id.value if card.epic_id else None,
                "updated_at": card.updated_at.value,
            }
            transaction.set(
                self._index_ref(card.space_id.value, new_state_key, card.id.value),
                index_data,
            )

            if old_state_key and old_state_key != new_state_key:
                transaction.delete(
                    self._index_ref(card.space_id.value, old_state_key, card.id.value)
                )

        await _update(transaction, card, old_state_key)

    async def get_by_id(self, card_id: CardId) -> Card | None:
        doc = await self._card_ref(card_id.value).get()
        if not doc.exists:
            return None
        return card_from_dict(snapshot_data(doc))

    async def get_by_space(
        self,
        space_id: SpaceId,
        filter: CardFilter | None = None,
    ) -> list[Card]:
        query = self._client.collection(self.COLLECTION).where(filter=FieldFilter("space_id", "==", space_id.value))
        docs = await query.get()
        cards = [card_from_dict(snapshot_data(doc)) for doc in docs]
        if filter:
            cards = [c for c in cards if filter.matches(c)]
        return cards

    async def get_by_pre_workflow_stage(
        self,
        space_id: SpaceId,
        stage: PreWorkflowStage,
    ) -> list[Card]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .where(filter=FieldFilter("pre_workflow_stage", "==", stage.value))
            .get()
        )
        return [card_from_dict(snapshot_data(doc)) for doc in docs]

    async def get_by_workflow_state(
        self,
        space_id: SpaceId,
        state_id: WorkflowStateId,
    ) -> list[Card]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .where(filter=FieldFilter("workflow_state_id", "==", state_id.value))
            .get()
        )
        return [card_from_dict(snapshot_data(doc)) for doc in docs]

    async def count_by_workflow_state(
        self,
        space_id: SpaceId,
        state_id: WorkflowStateId,
        filter: CardFilter | None = None,
    ) -> int:
        if filter:
            cards = await self.get_by_workflow_state(space_id, state_id)
            return len([c for c in cards if filter.matches(c)])

        query = (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .where(filter=FieldFilter("workflow_state_id", "==", state_id.value))
            .count()
        )
        result = await query.get()
        return result[0][0].value

    async def get_by_area(self, area_id: AreaId) -> list[Card]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("area_id", "==", area_id.value))
            .get()
        )
        return [card_from_dict(snapshot_data(doc)) for doc in docs]

    async def get_by_project(self, project_id: ProjectId) -> list[Card]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("project_id", "==", project_id.value))
            .get()
        )
        return [card_from_dict(snapshot_data(doc)) for doc in docs]

    async def get_by_epic(self, epic_id: EpicId) -> list[Card]:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("epic_id", "==", epic_id.value))
            .get()
        )
        return [card_from_dict(snapshot_data(doc)) for doc in docs]

    async def delete(self, card_id: CardId) -> None:
        await self._card_ref(card_id.value).delete()