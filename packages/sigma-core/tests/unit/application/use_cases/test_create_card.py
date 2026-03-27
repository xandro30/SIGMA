import pytest
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.task_management.domain.errors import SpaceNotFoundError
from sigma_core.task_management.domain.aggregates.space import Space
from sigma_core.task_management.domain.value_objects import SpaceId, SpaceName, CardTitle
from sigma_core.task_management.application.use_cases.card.create_card import CreateCard, CreateCardCommand
from tests.fakes.fake_card_repository import FakeCardRepository
from tests.fakes.fake_space_repository import FakeSpaceRepository


@pytest.fixture
def space():
    return Space(id=SpaceId.generate(), name=SpaceName("Work"))


@pytest.fixture
def repos(space):
    card_repo = FakeCardRepository()
    space_repo = FakeSpaceRepository()
    return card_repo, space_repo, space


@pytest.mark.asyncio
async def test_create_card_in_inbox_by_default(repos):
    card_repo, space_repo, space = repos
    await space_repo.save(space)
    use_case = CreateCard(card_repo, space_repo)

    card_id = await use_case.execute(CreateCardCommand(
        space_id=space.id,
        title=CardTitle("Revisar logs"),
    ))

    card = await card_repo.get_by_id(card_id)
    assert card is not None
    assert card.pre_workflow_stage == PreWorkflowStage.INBOX
    assert card.workflow_state_id is None


@pytest.mark.asyncio
async def test_create_card_raises_error_if_space_not_found():
    card_repo = FakeCardRepository()
    space_repo = FakeSpaceRepository()
    use_case = CreateCard(card_repo, space_repo)

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(CreateCardCommand(
            space_id=SpaceId.generate(),
            title=CardTitle("Tarea"),
        ))