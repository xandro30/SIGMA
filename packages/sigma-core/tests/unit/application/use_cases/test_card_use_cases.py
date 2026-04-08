import pytest
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import (
    Space, WorkflowState, BEGIN_STATE_ID, FINISH_STATE_ID,
)
from sigma_core.task_management.domain.enums import PreWorkflowStage, Priority
from sigma_core.task_management.domain.errors import (
    CardNotFoundError, SpaceNotFoundError,
    InvalidTransitionError,
)
from sigma_core.task_management.domain.value_objects import (
    CardId, SpaceId, SpaceName, CardTitle, WorkflowStateId,
)
from sigma_core.task_management.application.use_cases.card.create_card import (
    CreateCard, CreateCardCommand,
)
from sigma_core.task_management.application.use_cases.card.move_card import (
    MoveCard, MoveCardCommand,
)
from sigma_core.task_management.application.use_cases.card.promote_to_workflow import (
    PromoteToWorkflow, PromoteToWorkflowCommand,
)
from sigma_core.task_management.application.use_cases.card.demote_to_pre_workflow import (
    DemoteToPreWorkflow, DemoteToPreWorkflowCommand,
)
from sigma_core.task_management.application.use_cases.card.update_card import (
    UpdateCard, UpdateCardCommand,
)
from sigma_core.task_management.application.use_cases.card.archive_card import (
    ArchiveCard, ArchiveCardCommand,
)
from sigma_core.task_management.application.use_cases.card.delete_card import (
    DeleteCard, DeleteCardCommand,
)
from tests.fakes.fake_card_repository import FakeCardRepository
from tests.fakes.fake_space_repository import FakeSpaceRepository
from sigma_core.task_management.application.use_cases.card.move_triage_stage import (
    MoveTriageStage, MoveTriageStageCommand,
)
from sigma_core.task_management.domain.errors import (
    CardNotInTriageError, AlreadyInStageError, InboxNotAllowedError,
)


# ── Fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def space():
    return Space(id=SpaceId.generate(), name=SpaceName("Work"))


@pytest.fixture
def space_with_workflow():
    in_progress_id = WorkflowStateId.generate()
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
    state = WorkflowState(id=in_progress_id, name="In Progress", order=1)
    space.add_state(state)
    space.add_transition(BEGIN_STATE_ID, in_progress_id)
    space.add_transition(in_progress_id, FINISH_STATE_ID)
    return space, in_progress_id


@pytest.fixture
def card_in_backlog(space):
    card = Card(
        id=CardId.generate(),
        space_id=space.id,
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.BACKLOG,
        workflow_state_id=None,
    )
    return space, card


@pytest.fixture
def card_in_workflow(space):
    card = Card(
        id=CardId.generate(),
        space_id=space.id,
        title=CardTitle("Tarea"),
        pre_workflow_stage=None,
        workflow_state_id=BEGIN_STATE_ID,
    )
    return card


@pytest.fixture
def card_in_inbox(space):
    card = Card(
        id=CardId.generate(),
        space_id=space.id,
        title=CardTitle("Tarea en inbox"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
    )
    return card


# ── CreateCard ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_card_in_inbox_by_default(space):
    card_repo = FakeCardRepository()
    space_repo = FakeSpaceRepository()
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


# ── MoveCard ──────────────────────────────────────────────────────

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


# ── PromoteToWorkflow / DemoteToPreWorkflow ───────────────────────

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


# ── UpdateCard ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_card_title(card_in_workflow):
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo)

    await use_case.execute(UpdateCardCommand(
        card_id=card_in_workflow.id,
        title=CardTitle("Tarea actualizada"),
    ))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.title == CardTitle("Tarea actualizada")


@pytest.mark.asyncio
async def test_update_card_priority(card_in_workflow):
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo)

    await use_case.execute(UpdateCardCommand(
        card_id=card_in_workflow.id,
        priority=Priority.HIGH,
    ))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.priority == Priority.HIGH


@pytest.mark.asyncio
async def test_update_card_raises_error_if_not_found():
    card_repo = FakeCardRepository()
    use_case = UpdateCard(card_repo)

    with pytest.raises(CardNotFoundError):
        await use_case.execute(UpdateCardCommand(card_id=CardId.generate()))


# ── ArchiveCard / DeleteCard ──────────────────────────────────────

@pytest.mark.asyncio
async def test_archive_card_moves_to_finish(card_in_workflow):
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_workflow)
    use_case = ArchiveCard(card_repo)

    await use_case.execute(ArchiveCardCommand(card_id=card_in_workflow.id))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.workflow_state_id == FINISH_STATE_ID


@pytest.mark.asyncio
async def test_archive_card_in_pre_workflow_raises_error():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
    )
    card_repo = FakeCardRepository()
    await card_repo.save(card)
    use_case = ArchiveCard(card_repo)

    with pytest.raises(InvalidTransitionError):
        await use_case.execute(ArchiveCardCommand(card_id=card.id))


@pytest.mark.asyncio
async def test_delete_card_removes_card(card_in_workflow):
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_workflow)
    use_case = DeleteCard(card_repo)

    await use_case.execute(DeleteCardCommand(card_id=card_in_workflow.id))

    assert await card_repo.get_by_id(card_in_workflow.id) is None


@pytest.mark.asyncio
async def test_delete_card_raises_error_if_not_found():
    card_repo = FakeCardRepository()
    use_case = DeleteCard(card_repo)

    with pytest.raises(CardNotFoundError):
        await use_case.execute(DeleteCardCommand(card_id=CardId.generate()))


# ── MoveTriageStage ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_move_triage_stage_inbox_to_refinement(card_in_inbox):
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_inbox)
    use_case = MoveTriageStage(card_repo)

    await use_case.execute(MoveTriageStageCommand(
        card_id=card_in_inbox.id,
        target_stage=PreWorkflowStage.REFINEMENT,
    ))

    updated = await card_repo.get_by_id(card_in_inbox.id)
    assert updated.pre_workflow_stage == PreWorkflowStage.REFINEMENT


@pytest.mark.asyncio
async def test_move_triage_stage_inbox_to_backlog(card_in_inbox):
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_inbox)
    use_case = MoveTriageStage(card_repo)

    await use_case.execute(MoveTriageStageCommand(
        card_id=card_in_inbox.id,
        target_stage=PreWorkflowStage.BACKLOG,
    ))

    updated = await card_repo.get_by_id(card_in_inbox.id)
    assert updated.pre_workflow_stage == PreWorkflowStage.BACKLOG


@pytest.mark.asyncio
async def test_move_triage_stage_card_not_found_raises():
    card_repo = FakeCardRepository()
    use_case = MoveTriageStage(card_repo)

    with pytest.raises(CardNotFoundError):
        await use_case.execute(MoveTriageStageCommand(
            card_id=CardId.generate(),
            target_stage=PreWorkflowStage.REFINEMENT,
        ))


@pytest.mark.asyncio
async def test_move_triage_stage_card_in_workflow_raises(card_in_workflow):
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_workflow)
    use_case = MoveTriageStage(card_repo)

    with pytest.raises(CardNotInTriageError):
        await use_case.execute(MoveTriageStageCommand(
            card_id=card_in_workflow.id,
            target_stage=PreWorkflowStage.REFINEMENT,
        ))


@pytest.mark.asyncio
async def test_move_triage_stage_already_in_stage_raises(card_in_inbox):
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_inbox)
    use_case = MoveTriageStage(card_repo)

    with pytest.raises(AlreadyInStageError):
        await use_case.execute(MoveTriageStageCommand(
            card_id=card_in_inbox.id,
            target_stage=PreWorkflowStage.INBOX,
        ))


@pytest.mark.asyncio
async def test_move_triage_stage_inbox_not_allowed_raises(space):
    card_repo = FakeCardRepository()
    card = Card(
        id=CardId.generate(),
        space_id=space.id,
        title=CardTitle("Tarea en refinement"),
        pre_workflow_stage=PreWorkflowStage.REFINEMENT,
        workflow_state_id=None,
    )
    await card_repo.save(card)
    use_case = MoveTriageStage(card_repo)

    with pytest.raises(InboxNotAllowedError):
        await use_case.execute(MoveTriageStageCommand(
            card_id=card.id,
            target_stage=PreWorkflowStage.INBOX,
        ))