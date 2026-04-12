import pytest
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import (
    Space, WorkflowState, BEGIN_STATE_ID, FINISH_STATE_ID,
)
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.task_management.domain.enums import PreWorkflowStage, Priority
from sigma_core.task_management.domain.errors import (
    CardNotFoundError,
    SpaceNotFoundError,
    InvalidTransitionError,
    AreaNotFoundError,
    EpicNotFoundError,
    InvalidEpicSpaceError,
    TimerAlreadyRunningError,
    TimerNotRunningError,
    SpaceHasActiveTimerError,
)
from sigma_core.shared_kernel.value_objects import (
    CardId,
    SpaceId,
    AreaId,
    Minutes,
    SizeMapping,
)
from sigma_core.task_management.domain.value_objects import (
    SpaceName,
    CardTitle,
    WorkflowStateId,
    EpicId,
    ProjectId,
)
from sigma_core.task_management.domain.entities.area import Area
from sigma_core.task_management.domain.entities.epic import Epic
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
    UpdateCard, UpdateCardCommand, UNSET,
)
from sigma_core.task_management.application.use_cases.card.archive_card import (
    ArchiveCard, ArchiveCardCommand,
)
from sigma_core.task_management.application.use_cases.card.delete_card import (
    DeleteCard, DeleteCardCommand,
)
from tests.fakes.fake_card_repository import FakeCardRepository
from tests.fakes.fake_space_repository import FakeSpaceRepository
from tests.fakes.fake_area_repository import FakeAreaRepository
from tests.fakes.fake_epic_repository import FakeEpicRepository
from sigma_core.task_management.application.use_cases.card.move_triage_stage import (
    MoveTriageStage, MoveTriageStageCommand,
)
from sigma_core.task_management.domain.errors import (
    CardNotInTriageError,
    AlreadyInStageError,
    InboxNotAllowedError,
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
    use_case = UpdateCard(card_repo, FakeAreaRepository(), FakeEpicRepository())

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
    use_case = UpdateCard(card_repo, FakeAreaRepository(), FakeEpicRepository())

    await use_case.execute(UpdateCardCommand(
        card_id=card_in_workflow.id,
        priority=Priority.HIGH,
    ))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.priority == Priority.HIGH


@pytest.mark.asyncio
async def test_update_card_raises_error_if_not_found():
    card_repo = FakeCardRepository()
    use_case = UpdateCard(card_repo, FakeAreaRepository(), FakeEpicRepository())

    with pytest.raises(CardNotFoundError):
        await use_case.execute(UpdateCardCommand(card_id=CardId.generate()))


@pytest.mark.asyncio
async def test_update_card_assigns_area(card_in_workflow):
    card_repo = FakeCardRepository()
    area_repo = FakeAreaRepository()
    area = Area(id=AreaId.generate(), name="Backend")
    await area_repo.save(area)
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo, area_repo, FakeEpicRepository())

    await use_case.execute(UpdateCardCommand(
        card_id=card_in_workflow.id,
        area_id=area.id,
    ))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.area_id == area.id


@pytest.mark.asyncio
async def test_update_card_clears_area_when_area_id_is_none(card_in_workflow):
    card_repo = FakeCardRepository()
    area_repo = FakeAreaRepository()
    area = Area(id=AreaId.generate(), name="Backend")
    await area_repo.save(area)
    card_in_workflow.area_id = area.id
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo, area_repo, FakeEpicRepository())

    await use_case.execute(UpdateCardCommand(
        card_id=card_in_workflow.id,
        area_id=None,  # explícito: limpiar
    ))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.area_id is None


@pytest.mark.asyncio
async def test_update_card_area_id_unset_does_not_touch_existing_area(card_in_workflow):
    card_repo = FakeCardRepository()
    area_repo = FakeAreaRepository()
    area = Area(id=AreaId.generate(), name="Backend")
    await area_repo.save(area)
    card_in_workflow.area_id = area.id
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo, area_repo, FakeEpicRepository())

    await use_case.execute(UpdateCardCommand(
        card_id=card_in_workflow.id,
        title=CardTitle("Solo actualizo título"),
        # area_id UNSET → no tocar
    ))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.area_id == area.id


@pytest.mark.asyncio
async def test_update_card_raises_error_if_area_not_found(card_in_workflow):
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo, FakeAreaRepository(), FakeEpicRepository())

    with pytest.raises(AreaNotFoundError):
        await use_case.execute(UpdateCardCommand(
            card_id=card_in_workflow.id,
            area_id=AreaId.generate(),  # no existe en repo
        ))


@pytest.mark.asyncio
async def test_update_card_assigns_epic(card_in_workflow):
    card_repo = FakeCardRepository()
    epic_repo = FakeEpicRepository()
    epic = Epic(
        id=EpicId.generate(),
        space_id=card_in_workflow.space_id,  # mismo space
        area_id=AreaId.generate(),
        project_id=ProjectId.generate(),
        name="Epic A",
    )
    await epic_repo.save(epic)
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo, FakeAreaRepository(), epic_repo)

    await use_case.execute(UpdateCardCommand(
        card_id=card_in_workflow.id,
        epic_id=epic.id,
    ))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.epic_id == epic.id


@pytest.mark.asyncio
async def test_update_card_raises_error_if_epic_not_found(card_in_workflow):
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo, FakeAreaRepository(), FakeEpicRepository())

    with pytest.raises(EpicNotFoundError):
        await use_case.execute(UpdateCardCommand(
            card_id=card_in_workflow.id,
            epic_id=EpicId.generate(),
        ))


@pytest.mark.asyncio
async def test_update_card_raises_error_if_epic_belongs_to_different_space(card_in_workflow):
    card_repo = FakeCardRepository()
    epic_repo = FakeEpicRepository()
    other_space_id = SpaceId.generate()
    epic = Epic(
        id=EpicId.generate(),
        space_id=other_space_id,  # space distinto
        area_id=AreaId.generate(),
        project_id=ProjectId.generate(),
        name="Epic de otro space",
    )
    await epic_repo.save(epic)
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo, FakeAreaRepository(), epic_repo)

    with pytest.raises(InvalidEpicSpaceError):
        await use_case.execute(UpdateCardCommand(
            card_id=card_in_workflow.id,
            epic_id=epic.id,
        ))


@pytest.mark.asyncio
async def test_update_card_replaces_labels(card_in_workflow):
    card_in_workflow.labels = {"bug", "backend"}
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo, FakeAreaRepository(), FakeEpicRepository())

    await use_case.execute(UpdateCardCommand(
        card_id=card_in_workflow.id,
        labels={"urgente", "frontend"},
    ))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.labels == {"urgente", "frontend"}


@pytest.mark.asyncio
async def test_update_card_clears_labels_when_empty_set(card_in_workflow):
    card_in_workflow.labels = {"bug", "backend"}
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo, FakeAreaRepository(), FakeEpicRepository())

    await use_case.execute(UpdateCardCommand(
        card_id=card_in_workflow.id,
        labels=set(),
    ))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.labels == set()


@pytest.mark.asyncio
async def test_update_card_labels_none_does_not_touch_existing_labels(card_in_workflow):
    card_in_workflow.labels = {"bug", "backend"}
    card_repo = FakeCardRepository()
    await card_repo.save(card_in_workflow)
    use_case = UpdateCard(card_repo, FakeAreaRepository(), FakeEpicRepository())

    await use_case.execute(UpdateCardCommand(
        card_id=card_in_workflow.id,
        title=CardTitle("Solo título"),
        # labels=None (UNSET) → no tocar
    ))

    updated = await card_repo.get_by_id(card_in_workflow.id)
    assert updated.labels == {"bug", "backend"}


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


# ── AssignSize use case ──────────────────────────────────────────

from sigma_core.task_management.application.use_cases.card.assign_size import (
    AssignSize, AssignSizeCommand,
)


@pytest.mark.asyncio
async def test_assign_size_establece_tamaño(card_in_backlog):
    space, card = card_in_backlog
    card_repo = FakeCardRepository()
    await card_repo.save(card)
    use_case = AssignSize(card_repo)

    await use_case.execute(AssignSizeCommand(card_id=card.id, size=CardSize.M))

    updated = await card_repo.get_by_id(card.id)
    assert updated.size == CardSize.M


@pytest.mark.asyncio
async def test_assign_size_none_limpia_tamaño(card_in_backlog):
    space, card = card_in_backlog
    card.assign_size(CardSize.L)
    card_repo = FakeCardRepository()
    await card_repo.save(card)
    use_case = AssignSize(card_repo)

    await use_case.execute(AssignSizeCommand(card_id=card.id, size=None))

    updated = await card_repo.get_by_id(card.id)
    assert updated.size is None


@pytest.mark.asyncio
async def test_assign_size_card_not_found_raises():
    card_repo = FakeCardRepository()
    use_case = AssignSize(card_repo)

    with pytest.raises(CardNotFoundError):
        await use_case.execute(AssignSizeCommand(card_id=CardId.generate(), size=CardSize.M))


# ── StartTimer / StopTimer use cases ─────────────────────────────

from sigma_core.task_management.application.use_cases.card.start_timer import (
    StartTimer, StartTimerCommand,
)
from sigma_core.task_management.application.use_cases.card.stop_timer import (
    StopTimer, StopTimerCommand,
)
from tests.helpers.timestamps import ts as _ts


@pytest.mark.asyncio
async def test_start_timer_marca_timestamp(card_in_backlog):
    space, card = card_in_backlog
    card_repo = FakeCardRepository()
    await card_repo.save(card)
    use_case = StartTimer(card_repo)
    now = _ts(2026, 1, 1, 10, 0)

    await use_case.execute(StartTimerCommand(card_id=card.id, now=now))

    updated = await card_repo.get_by_id(card.id)
    assert updated.timer_started_at == now


@pytest.mark.asyncio
async def test_start_timer_card_not_found_raises():
    card_repo = FakeCardRepository()
    use_case = StartTimer(card_repo)

    with pytest.raises(CardNotFoundError):
        await use_case.execute(StartTimerCommand(
            card_id=CardId.generate(),
            now=_ts(2026, 1, 1, 10, 0),
        ))


@pytest.mark.asyncio
async def test_start_timer_lanza_error_si_otra_card_del_mismo_space_tiene_timer_activo(space):
    card_repo = FakeCardRepository()
    busy_card = Card(
        id=CardId.generate(),
        space_id=space.id,
        title=CardTitle("Card ocupada"),
        pre_workflow_stage=PreWorkflowStage.BACKLOG,
        workflow_state_id=None,
    )
    busy_card.start_timer(_ts(2026, 1, 1, 9, 0))
    await card_repo.save(busy_card)

    new_card = Card(
        id=CardId.generate(),
        space_id=space.id,
        title=CardTitle("Card nueva"),
        pre_workflow_stage=PreWorkflowStage.BACKLOG,
        workflow_state_id=None,
    )
    await card_repo.save(new_card)
    use_case = StartTimer(card_repo)

    with pytest.raises(SpaceHasActiveTimerError) as exc_info:
        await use_case.execute(StartTimerCommand(
            card_id=new_card.id,
            now=_ts(2026, 1, 1, 10, 0),
        ))

    assert exc_info.value.space_id == space.id.value
    assert exc_info.value.active_card_id == busy_card.id.value


@pytest.mark.asyncio
async def test_start_timer_permite_iniciar_en_otra_card_si_el_timer_activo_es_de_otro_space():
    repo = FakeCardRepository()
    space_a = SpaceId.generate()
    space_b = SpaceId.generate()

    busy_card = Card(
        id=CardId.generate(),
        space_id=space_a,
        title=CardTitle("Card ocupada en A"),
        pre_workflow_stage=PreWorkflowStage.BACKLOG,
        workflow_state_id=None,
    )
    busy_card.start_timer(_ts(2026, 1, 1, 9, 0))
    await repo.save(busy_card)

    new_card = Card(
        id=CardId.generate(),
        space_id=space_b,
        title=CardTitle("Card nueva en B"),
        pre_workflow_stage=PreWorkflowStage.BACKLOG,
        workflow_state_id=None,
    )
    await repo.save(new_card)
    use_case = StartTimer(repo)

    await use_case.execute(StartTimerCommand(
        card_id=new_card.id,
        now=_ts(2026, 1, 1, 10, 0),
    ))

    updated = await repo.get_by_id(new_card.id)
    assert updated.timer_started_at == _ts(2026, 1, 1, 10, 0)


@pytest.mark.asyncio
async def test_stop_timer_acumula_actual_time(card_in_backlog):
    space, card = card_in_backlog
    card.start_timer(_ts(2026, 1, 1, 10, 0))
    card_repo = FakeCardRepository()
    await card_repo.save(card)
    use_case = StopTimer(card_repo)

    await use_case.execute(StopTimerCommand(
        card_id=card.id,
        now=_ts(2026, 1, 1, 10, 45),
    ))

    updated = await card_repo.get_by_id(card.id)
    assert updated.actual_time == Minutes(45)
    assert updated.timer_started_at is None


@pytest.mark.asyncio
async def test_stop_timer_sin_timer_corriendo_raises(card_in_backlog):
    space, card = card_in_backlog
    card_repo = FakeCardRepository()
    await card_repo.save(card)
    use_case = StopTimer(card_repo)

    with pytest.raises(TimerNotRunningError):
        await use_case.execute(StopTimerCommand(
            card_id=card.id,
            now=_ts(2026, 1, 1, 10, 45),
        ))


@pytest.mark.asyncio
async def test_stop_timer_card_not_found_raises():
    card_repo = FakeCardRepository()
    use_case = StopTimer(card_repo)

    with pytest.raises(CardNotFoundError):
        await use_case.execute(StopTimerCommand(
            card_id=CardId.generate(),
            now=_ts(2026, 1, 1, 10, 0),
        ))


# ── SetSizeMapping use case ──────────────────────────────────────

from sigma_core.task_management.application.use_cases.space.set_size_mapping import (
    SetSizeMapping, SetSizeMappingCommand,
)


@pytest.mark.asyncio
async def test_set_size_mapping_establece_mapping(space):
    space_repo = FakeSpaceRepository()
    await space_repo.save(space)
    use_case = SetSizeMapping(space_repo)
    mapping = SizeMapping.default()

    await use_case.execute(SetSizeMappingCommand(space_id=space.id, mapping=mapping))

    updated = await space_repo.get_by_id(space.id)
    assert updated.size_mapping == mapping


@pytest.mark.asyncio
async def test_set_size_mapping_none_limpia(space):
    space.set_size_mapping(SizeMapping.default())
    space_repo = FakeSpaceRepository()
    await space_repo.save(space)
    use_case = SetSizeMapping(space_repo)

    await use_case.execute(SetSizeMappingCommand(space_id=space.id, mapping=None))

    updated = await space_repo.get_by_id(space.id)
    assert updated.size_mapping is None


@pytest.mark.asyncio
async def test_set_size_mapping_space_not_found_raises():
    space_repo = FakeSpaceRepository()
    use_case = SetSizeMapping(space_repo)

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(SetSizeMappingCommand(
            space_id=SpaceId.generate(),
            mapping=SizeMapping.default(),
        ))