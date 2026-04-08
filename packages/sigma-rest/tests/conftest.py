import pytest
import pytest_asyncio
import httpx
from sigma_rest.main import app
from sigma_rest.dependencies import get_card_repo, get_space_repo
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.value_objects import CardId, SpaceId, CardTitle, WorkflowStateId
from sigma_core.task_management.domain.enums import PreWorkflowStage
from fakes.fake_card_repository import FakeCardRepository    # type: ignore[import]  # resolved via pytest pythonpath
from fakes.fake_space_repository import FakeSpaceRepository  # type: ignore[import]


@pytest.fixture
def card_repo():
    return FakeCardRepository()


@pytest.fixture
def space_repo():
    return FakeSpaceRepository()


@pytest_asyncio.fixture
async def client(card_repo, space_repo):
    app.dependency_overrides[get_card_repo]  = lambda: card_repo
    app.dependency_overrides[get_space_repo] = lambda: space_repo
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def card_in_inbox(card_repo):
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Test card in inbox"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
    )
    await card_repo.save(card)
    return card


@pytest_asyncio.fixture
async def card_in_refinement(card_repo):
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Test card in refinement"),
        pre_workflow_stage=PreWorkflowStage.REFINEMENT,
        workflow_state_id=None,
    )
    await card_repo.save(card)
    return card


@pytest_asyncio.fixture
async def card_in_workflow(card_repo):
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Test card in workflow"),
        pre_workflow_stage=None,
        workflow_state_id=WorkflowStateId.generate(),
    )
    await card_repo.save(card)
    return card
