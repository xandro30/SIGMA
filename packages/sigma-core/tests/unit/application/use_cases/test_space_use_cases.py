import pytest
from sigma_core.task_management.domain.aggregates.space import (
    Space, WorkflowState, BEGIN_STATE_ID, FINISH_STATE_ID,
)
from sigma_core.task_management.domain.errors import SpaceNotFoundError
from sigma_core.task_management.domain.value_objects import SpaceId, SpaceName, WorkflowStateId
from sigma_core.task_management.application.use_cases.space.create_space import (
    CreateSpace, CreateSpaceCommand,
)
from sigma_core.task_management.application.use_cases.space.add_workflow_state import (
    AddWorkflowState, AddWorkflowStateCommand,
)
from sigma_core.task_management.application.use_cases.space.add_transition import (
    AddTransition, AddTransitionCommand,
)
from sigma_core.task_management.application.use_cases.space.remove_workflow_state import (
    RemoveWorkflowState, RemoveWorkflowStateCommand,
)
from tests.fakes.fake_space_repository import FakeSpaceRepository


@pytest.mark.asyncio
async def test_create_space():
    space_repo = FakeSpaceRepository()
    use_case = CreateSpace(space_repo)

    space_id = await use_case.execute(CreateSpaceCommand(name=SpaceName("Work")))

    space = await space_repo.get_by_id(space_id)
    assert space is not None
    assert space.name == SpaceName("Work")


@pytest.mark.asyncio
async def test_add_workflow_state():
    space_repo = FakeSpaceRepository()
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
    await space_repo.save(space)
    use_case = AddWorkflowState(space_repo)

    state_id = await use_case.execute(AddWorkflowStateCommand(
        space_id=space.id,
        name="In Progress",
        order=1,
    ))

    updated = await space_repo.get_by_id(space.id)
    assert any(s.id == state_id for s in updated.workflow_states)


@pytest.mark.asyncio
async def test_add_transition():
    space_repo = FakeSpaceRepository()
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
    state = WorkflowState(id=WorkflowStateId.generate(), name="In Progress", order=1)
    space.add_state(state)
    await space_repo.save(space)
    use_case = AddTransition(space_repo)

    await use_case.execute(AddTransitionCommand(
        space_id=space.id,
        from_id=BEGIN_STATE_ID,
        to_id=state.id,
    ))

    updated = await space_repo.get_by_id(space.id)
    assert space.is_valid_transition(BEGIN_STATE_ID, state.id)


@pytest.mark.asyncio
async def test_add_workflow_state_raises_error_if_space_not_found():
    space_repo = FakeSpaceRepository()
    use_case = AddWorkflowState(space_repo)

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(AddWorkflowStateCommand(
            space_id=SpaceId.generate(),
            name="In Progress",
            order=1,
        ))