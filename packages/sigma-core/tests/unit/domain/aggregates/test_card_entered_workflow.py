"""Tests unit de entered_workflow_at en Card."""
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import FINISH_STATE_ID
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.task_management.domain.value_objects import (
    CardTitle,
    WorkflowStateId,
)
from sigma_core.shared_kernel.value_objects import CardId, SpaceId


def _inbox_card() -> Card:
    return Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Test"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
    )


def _workflow_card() -> Card:
    return Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Test"),
        pre_workflow_stage=None,
        workflow_state_id=WorkflowStateId.generate(),
    )


def test_entered_workflow_at_default_none():
    card = _inbox_card()
    assert card.entered_workflow_at is None


def test_entered_workflow_at_se_setea_al_promover_desde_triage():
    card = _inbox_card()
    card.move_to_workflow_state(WorkflowStateId.generate())
    assert card.entered_workflow_at is not None


def test_entered_workflow_at_no_cambia_al_mover_entre_workflow_states():
    card = _inbox_card()
    card.move_to_workflow_state(WorkflowStateId.generate())
    first_entered = card.entered_workflow_at

    card.move_to_workflow_state(WorkflowStateId.generate())
    assert card.entered_workflow_at == first_entered


def test_entered_workflow_at_se_sobreescribe_al_re_promover_tras_triage():
    card = _inbox_card()
    card.move_to_workflow_state(WorkflowStateId.generate())
    first_entered = card.entered_workflow_at

    card.move_to_pre_workflow(PreWorkflowStage.REFINEMENT)
    assert card.entered_workflow_at is None

    card.move_to_workflow_state(WorkflowStateId.generate())
    assert card.entered_workflow_at is not None
    assert card.entered_workflow_at != first_entered


def test_entered_workflow_at_se_limpia_al_volver_a_triage():
    card = _inbox_card()
    card.move_to_workflow_state(WorkflowStateId.generate())
    assert card.entered_workflow_at is not None

    card.move_to_pre_workflow(PreWorkflowStage.BACKLOG)
    assert card.entered_workflow_at is None


def test_entered_workflow_at_se_setea_al_promover_a_finish():
    card = _inbox_card()
    card.move_to_workflow_state(FINISH_STATE_ID)
    assert card.entered_workflow_at is not None
    assert card.completed_at is not None
