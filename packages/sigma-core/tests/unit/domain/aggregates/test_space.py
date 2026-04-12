import pytest

from sigma_core.task_management.domain.aggregates.space import Space, BEGIN_STATE_ID, FINISH_STATE_ID, WorkflowState, Transition, WorkflowStateId
from sigma_core.task_management.domain.errors import (
    InvalidWorkflowError,
    DuplicateStateError,
)
from sigma_core.shared_kernel.value_objects import SpaceId, SizeMapping
from sigma_core.task_management.domain.value_objects import SpaceName


def test_space_create_with_valid_name():
    space_id = SpaceId.generate()
    name = SpaceName("Work")

    result = Space(
        id=space_id,
        name=name,
        workflow_states=[],
        transitions=[],
    )

    assert result.id == space_id
    assert result.name == name


def test_is_valid_transition_without_workflow_is_always_valid():
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"), workflow_states=[], transitions=[])

    result = space.is_valid_transition(BEGIN_STATE_ID, FINISH_STATE_ID)

    assert result is True


def test_is_valid_transition_with_workflow_returns_true_if_exists():
    in_progress_id = WorkflowStateId.generate()
    in_progress = WorkflowState(id=in_progress_id, name="In Progress", order=1)
    transition = Transition(from_id=BEGIN_STATE_ID, to_id=in_progress_id)
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"), workflow_states=[in_progress], transitions=[transition])

    result = space.is_valid_transition(BEGIN_STATE_ID, in_progress_id)

    assert result is True


def test_is_valid_transition_with_workflow_returns_false_if_not_exists():
    in_progress_id = WorkflowStateId.generate()
    in_progress = WorkflowState(id=in_progress_id, name="In Progress", order=1)
    transition = Transition(from_id=BEGIN_STATE_ID, to_id=in_progress_id)
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"), workflow_states=[in_progress], transitions=[transition])

    result = space.is_valid_transition(in_progress_id, FINISH_STATE_ID)

    assert result is False


def test_add_state_adds_state_to_workflow():
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"), workflow_states=[], transitions=[])
    state = WorkflowState(id=WorkflowStateId.generate(), name="In Progress", order=1)

    space.add_state(state)

    assert state in space.workflow_states


def test_add_state_raises_error_if_name_is_reserved():
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"), workflow_states=[], transitions=[])
    state = WorkflowState(id=WorkflowStateId.generate(), name="begin", order=1)

    with pytest.raises(InvalidWorkflowError):
        space.add_state(state)


def test_add_state_raises_error_if_duplicate_id():
    state_id = WorkflowStateId.generate()
    state = WorkflowState(id=state_id, name="In Progress", order=1)
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"),workflow_states=[state], transitions=[])
    duplicate = WorkflowState(id=state_id, name="Otro", order=2)

    with pytest.raises(DuplicateStateError):
        space.add_state(duplicate)


def test_add_transition_adds_valid_transition():
    in_progress_id = WorkflowStateId.generate()
    state = WorkflowState(id=in_progress_id, name="In Progress", order=1)
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"), workflow_states=[state], transitions=[])

    space.add_transition(BEGIN_STATE_ID, in_progress_id)

    assert Transition(from_id=BEGIN_STATE_ID, to_id=in_progress_id) in space.transitions


def test_remove_state_also_removes_its_transitions():
    in_progress_id = WorkflowStateId.generate()
    state = WorkflowState(id=in_progress_id, name="In Progress", order=1)
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
    space.add_state(state)
    space.add_transition(BEGIN_STATE_ID, in_progress_id)
    space.add_transition(in_progress_id, FINISH_STATE_ID)

    space.remove_state(in_progress_id)

    assert len(space.transitions) == 0


# ── SizeMapping ──────────────────────────────────────────────────

def test_space_size_mapping_es_none_por_defecto():
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))

    assert space.size_mapping is None


def test_space_set_size_mapping_establece_el_mapping():
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
    mapping = SizeMapping.default()

    space.set_size_mapping(mapping)

    assert space.size_mapping == mapping


def test_space_set_size_mapping_none_limpia_el_mapping():
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
    space.set_size_mapping(SizeMapping.default())

    space.set_size_mapping(None)

    assert space.size_mapping is None