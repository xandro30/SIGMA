import pytest

from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.task_management.domain.errors import InvalidTransitionError
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import Space, BEGIN_STATE_ID
from sigma_core.task_management.domain.value_objects import (
    CardId, SpaceId, SpaceName, CardTitle,
)

from sigma_core.task_management.application.use_cases.card.promote_to_workflow import (
    PromoteToWorkflow, PromoteToWorkflowCommand,
)
from sigma_core.task_management.application.use_cases.card.demote_to_pre_workflow import (
    DemoteToPreWorkflow, DemoteToPreWorkflowCommand,
)

from tests.fakes.fake_card_repository import FakeCardRepository
from tests.fakes.fake_space_repository import FakeSpaceRepository


@pytest.fixture
def card_in_backlog():
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
    card = Card(
        id=CardId.generate(),
        space_id=space.id,
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.BACKLOG,
        workflow_state_id=None,
    )
    return space, card


@pytest.mark.asyncio
async def test_promote_card_to_begin_by_default(card_in_backlog):
    space, card = card_in_backlog
    card_repo = FakeCardRepository()
    space_repo = FakeSpaceRepository()
    await card_repo.save(card)
    await space_repo.save(space)

    use_case = PromoteToWorkflow(card_repo, space_repo)
    await use_case.execute(PromoteToWorkflowCommand(card_id=card.id))

    updated = await card_repo.get_by_id(card.id)
    assert updated.workflow_state_id == BEGIN_STATE_ID
    assert updated.pre_workflow_stage is None


@pytest.mark.asyncio
async def test_promote_card_already_in_workflow_raises_error(card_in_backlog):
    space, card = card_in_backlog
    card.move_to_workflow_state(BEGIN_STATE_ID)
    card_repo = FakeCardRepository()
    space_repo = FakeSpaceRepository()
    await card_repo.save(card)
    await space_repo.save(space)

    use_case = PromoteToWorkflow(card_repo, space_repo)

    with pytest.raises(InvalidTransitionError):
        await use_case.execute(PromoteToWorkflowCommand(card_id=card.id))


@pytest.mark.asyncio
async def test_demote_card_to_backlog_by_default(card_in_backlog):
    space, card = card_in_backlog
    card.move_to_workflow_state(BEGIN_STATE_ID)
    card_repo = FakeCardRepository()
    space_repo = FakeSpaceRepository()
    await card_repo.save(card)
    await space_repo.save(space)

    use_case = DemoteToPreWorkflow(card_repo)
    await use_case.execute(DemoteToPreWorkflowCommand(card_id=card.id))

    updated = await card_repo.get_by_id(card.id)
    assert updated.pre_workflow_stage == PreWorkflowStage.BACKLOG
    assert updated.workflow_state_id is None
