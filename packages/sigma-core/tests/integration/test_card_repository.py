import pytest
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.shared_kernel.value_objects import CardId, SpaceId
from sigma_core.task_management.domain.value_objects import CardTitle
from sigma_core.task_management.infrastructure.firestore.card_repository import (
    FirestoreCardRepository,
)


@pytest.fixture
def card():
    return Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea de integración"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
    )


@pytest.mark.asyncio
async def test_save_and_get_card(firestore_client, card):
    repo = FirestoreCardRepository(firestore_client)

    await repo.save(card)
    result = await repo.get_by_id(card.id)

    assert result is not None
    assert result.id == card.id
    assert result.title == card.title
    assert result.pre_workflow_stage == PreWorkflowStage.INBOX


@pytest.mark.asyncio
async def test_get_card_not_found(firestore_client):
    repo = FirestoreCardRepository(firestore_client)

    result = await repo.get_by_id(CardId.generate())

    assert result is None


@pytest.mark.asyncio
async def test_delete_card(firestore_client, card):
    repo = FirestoreCardRepository(firestore_client)
    await repo.save(card)

    await repo.delete(card.id)

    assert await repo.get_by_id(card.id) is None


@pytest.mark.asyncio
async def test_get_cards_by_space(firestore_client):
    repo = FirestoreCardRepository(firestore_client)
    space_id = SpaceId.generate()
    card1 = Card(
        id=CardId.generate(),
        space_id=space_id,
        title=CardTitle("Card 1"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
    )
    card2 = Card(
        id=CardId.generate(),
        space_id=space_id,
        title=CardTitle("Card 2"),
        pre_workflow_stage=PreWorkflowStage.BACKLOG,
        workflow_state_id=None,
    )
    await repo.save(card1)
    await repo.save(card2)

    results = await repo.get_by_space(space_id)

    ids = [c.id for c in results]
    assert card1.id in ids
    assert card2.id in ids