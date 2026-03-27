import pytest
from sigma_core.task_management.domain.errors import (
    CardNotFoundError, InvalidTransitionError,
)
from sigma_core.task_management.domain.aggregates.space import Space, WorkflowState, BEGIN_STATE_ID, FINISH_STATE_ID
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.value_objects import (
    SpaceId, SpaceName, CardId, CardTitle, WorkflowStateId,
)
from sigma_core.task_management.application.use_cases.card.move_card import MoveCard, MoveCardCommand
from tests.fakes.fake_card_repository import FakeCardRepository
from tests.fakes.fake_space_repository import FakeSpaceRepository


@pytest.fixture
def space_with_workflow():
    in_progress_id = WorkflowStateId.generate()
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
    state = WorkflowState(id=in_progress_id, name="In Progress", order=1)
    space.add_state(state)
    space.add_transition(BEGIN_STATE_ID, in_progress_id)
    space.add_transition(in_progress_id, FINISH_STATE_ID)
    return space, in_progress_id


@pytest.mark.asyncio
async def test_move_card_within_workflow(space_with_workflow):
    space, in_progress_id = space_with_workflow
    card = Card(
        id=CardId.generate(),
        space_id=space.id,
        title=CardTitle("Tarea"),
        pre_workflow_stage=None,
        workflow_state_id=BEGIN_STATE_ID,
    )
    card_repo = FakeCardRepository()
    space_repo = FakeSpaceRepository()
    await card_repo.save(card)
    await space_repo.save(space)

    use_case = MoveCard(card_repo, space_repo)
    await use_case.execute(MoveCardCommand(card_id=card.id, target_state_id=in_progress_id))

    updated = await card_repo.get_by_id(card.id)
    assert updated.workflow_state_id == in_progress_id


@pytest.mark.asyncio
async def test_move_card_raises_error_if_card_not_found():
    card_repo = FakeCardRepository()
    space_repo = FakeSpaceRepository()
    use_case = MoveCard(card_repo, space_repo)

    with pytest.raises(CardNotFoundError):
        await use_case.execute(MoveCardCommand(
            card_id=CardId.generate(),
            target_state_id=WorkflowStateId.generate(),
        ))


@pytest.mark.asyncio
async def test_move_card_raises_error_if_transition_not_allowed(space_with_workflow):
    space, in_progress_id = space_with_workflow
    card = Card(
        id=CardId.generate(),
        space_id=space.id,
        title=CardTitle("Tarea"),
        pre_workflow_stage=None,
        workflow_state_id=BEGIN_STATE_ID,
    )
    card_repo = FakeCardRepository()
    space_repo = FakeSpaceRepository()
    await card_repo.save(card)
    await space_repo.save(space)

    use_case = MoveCard(card_repo, space_repo)

    with pytest.raises(InvalidTransitionError):
        await use_case.execute(MoveCardCommand(
            card_id=card.id,
            target_state_id=FINISH_STATE_ID,
        ))