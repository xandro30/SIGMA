from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import (
    BEGIN_STATE_ID,
    FINISH_STATE_ID,
)
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.shared_kernel.value_objects import CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.value_objects import CardTitle, WorkflowStateId


def _make_card_in_workflow() -> Card:
    return Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Task"),
        pre_workflow_stage=None,
        workflow_state_id=BEGIN_STATE_ID,
    )


def _make_card_in_pre_workflow() -> Card:
    return Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Task"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
    )


# ── Default state ───────────────────────────────────────────────────


def test_new_card_has_no_completed_at() -> None:
    card = _make_card_in_workflow()
    assert card.completed_at is None


def test_new_card_in_pre_workflow_has_no_completed_at() -> None:
    card = _make_card_in_pre_workflow()
    assert card.completed_at is None


# ── Transition INTO finish ──────────────────────────────────────────


def test_move_to_finish_sets_completed_at() -> None:
    card = _make_card_in_workflow()
    assert card.completed_at is None

    card.move_to_workflow_state(FINISH_STATE_ID)

    assert card.completed_at is not None
    assert isinstance(card.completed_at, Timestamp)


def test_move_to_finish_is_idempotent_but_updates_completed_at() -> None:
    """Moving to finish again updates the timestamp (latest completion wins)."""
    card = _make_card_in_workflow()
    card.move_to_workflow_state(FINISH_STATE_ID)
    first_completion = card.completed_at
    assert first_completion is not None

    # Move to finish again — should refresh the completion timestamp.
    card.move_to_workflow_state(FINISH_STATE_ID)

    assert card.completed_at is not None
    assert card.completed_at.value >= first_completion.value


# ── Transition OUT of finish ────────────────────────────────────────


def test_move_away_from_finish_clears_completed_at() -> None:
    card = _make_card_in_workflow()
    card.move_to_workflow_state(FINISH_STATE_ID)
    assert card.completed_at is not None

    # Move to a non-finish workflow state.
    other_state = WorkflowStateId.generate()
    card.move_to_workflow_state(other_state)

    assert card.completed_at is None


def test_move_to_pre_workflow_from_finish_clears_completed_at() -> None:
    card = _make_card_in_workflow()
    card.move_to_workflow_state(FINISH_STATE_ID)
    assert card.completed_at is not None

    card.move_to_pre_workflow(PreWorkflowStage.INBOX)

    assert card.completed_at is None


# ── Transition between non-finish states ───────────────────────────


def test_move_between_non_finish_states_leaves_completed_at_none() -> None:
    card = _make_card_in_workflow()
    state_a = WorkflowStateId.generate()
    state_b = WorkflowStateId.generate()

    card.move_to_workflow_state(state_a)
    assert card.completed_at is None

    card.move_to_workflow_state(state_b)
    assert card.completed_at is None
