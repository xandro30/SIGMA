import pytest

from sigma_core.task_management.domain.errors import DuplicateChecklistItemError
from sigma_core.task_management.domain.aggregates.space import WorkflowStateId
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.enums import PreWorkflowStage, Priority
from sigma_core.task_management.domain.value_objects import (
    CardId, SpaceId, CardTitle, Timestamp, ChecklistItem, Url, EpicId, ProjectId, AreaId
)


def test_card_default_state():
    card_id = CardId.generate()
    space_id = SpaceId.generate()
    title = CardTitle("Tarea")

    card = Card(
        id=card_id,
        space_id=space_id,
        title=title,
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    assert card.id == card_id
    assert card.space_id == space_id
    assert card.title == title
    assert card.pre_workflow_stage == PreWorkflowStage.INBOX
    assert card.workflow_state_id is None
    assert card.description is None
    assert card.priority is None
    assert card.area_id is None
    assert card.project_id is None
    assert card.epic_id is None
    assert card.labels == set()
    assert card.topics == set()
    assert card.urls == []
    assert card.checklist == []
    assert card.related_cards == []


def test_card_is_created_with_all_fields():
    card_id = CardId.generate()
    space_id = SpaceId.generate()
    title = CardTitle("Implementar login")
    created_at = Timestamp.now()
    area_id = AreaId.generate()
    project_id = ProjectId.generate()
    epic_id = EpicId.generate()
    url = Url("https://docs.google.com")
    checklist_item = ChecklistItem("Revisar docs")

    card = Card(
        id=card_id,
        space_id=space_id,
        title=title,
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=created_at,
        updated_at=created_at,
        description="Descripción completa",
        priority=Priority.HIGH,
        area_id=area_id,
        project_id=project_id,
        epic_id=epic_id,
        labels={"#SecOps"},
        topics={"IAM"},
        urls=[url],
        checklist=[checklist_item],
        related_cards=[CardId.generate()],
    )

    assert card.id == card_id
    assert card.space_id == space_id
    assert card.title == title
    assert card.description == "Descripción completa"
    assert card.priority == Priority.HIGH
    assert card.area_id == area_id
    assert card.project_id == project_id
    assert card.epic_id == epic_id
    assert card.labels == {"#SecOps"}
    assert card.topics == {"IAM"}
    assert card.urls == [url]
    assert card.checklist == [checklist_item]
    assert len(card.related_cards) == 1


def test_card_is_created_in_inbox_by_default():
    card_id = CardId.generate()
    space_id = SpaceId.generate()
    title = CardTitle("Implementar login")

    result = Card(
        id=card_id,
        space_id=space_id,
        title=title,
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    assert result.id == card_id
    assert result.pre_workflow_stage == PreWorkflowStage.INBOX
    assert result.workflow_state_id is None


def test_card_raises_error_if_both_stages_are_set():
    with pytest.raises(ValueError):
        Card(
            id=CardId.generate(),
            space_id=SpaceId.generate(),
            title=CardTitle("Tarea"),
            pre_workflow_stage=PreWorkflowStage.INBOX,
            workflow_state_id=WorkflowStateId.generate(),
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
        )


def test_card_raises_error_if_no_stage_is_set():
    with pytest.raises(ValueError):
        Card(
            id=CardId.generate(),
            space_id=SpaceId.generate(),
            title=CardTitle("Tarea"),
            pre_workflow_stage=None,
            workflow_state_id=None,
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
        )


def test_card_moves_to_workflow_state():
    state_id = WorkflowStateId.generate()
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    card.move_to_workflow_state(state_id)

    assert card.workflow_state_id == state_id
    assert card.pre_workflow_stage is None


def test_card_moves_to_pre_workflow_stage():
    state_id = WorkflowStateId.generate()
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=None,
        workflow_state_id=state_id,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    card.move_to_pre_workflow(PreWorkflowStage.BACKLOG)

    assert card.pre_workflow_stage == PreWorkflowStage.BACKLOG
    assert card.workflow_state_id is None


def test_card_updated_at_changes_on_move():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    original_updated_at = card.updated_at

    card.move_to_workflow_state(WorkflowStateId.generate())

    assert card.updated_at.value > original_updated_at.value


def test_add_label_adds_label_to_card():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    card.add_label("#SecOps")

    assert "#SecOps" in card.labels


def test_remove_label_removes_label_from_card():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    card.add_label("#SecOps")

    card.remove_label("#SecOps")

    assert "#SecOps" not in card.labels


def test_add_and_remove_topic():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    card.add_topic("IAM")

    assert "IAM" in card.topics

    card.remove_topic("IAM")

    assert "IAM" not in card.topics


# ── Labels & Topics ───────────────────────────────────────────────

def test_add_and_remove_topic():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    card.add_topic("IAM")

    assert "IAM" in card.topics

    card.remove_topic("IAM")

    assert "IAM" not in card.topics


# ── URLs ──────────────────────────────────────────────────────────

def test_add_url_adds_url_to_card():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    url = Url("https://docs.google.com")

    card.add_url(url)

    assert url in card.urls


def test_add_url_is_idempotent():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    url = Url("https://docs.google.com")

    card.add_url(url)
    card.add_url(url)

    assert card.urls.count(url) == 1


def test_remove_url_removes_url_from_card():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    url = Url("https://docs.google.com")
    card.add_url(url)

    card.remove_url(url)

    assert url not in card.urls


# ── Checklist ─────────────────────────────────────────────────────

def test_add_checklist_item_adds_item_to_card():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    item = ChecklistItem("Revisar docs")

    card.add_checklist_item(item)

    assert item in card.checklist


def test_add_duplicate_checklist_item_raises_error():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    item = ChecklistItem("Revisar docs")
    card.add_checklist_item(item)

    with pytest.raises(DuplicateChecklistItemError):
        card.add_checklist_item(item)


def test_toggle_checklist_item_marks_as_done():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    card.add_checklist_item(ChecklistItem("Revisar docs"))

    card.toggle_checklist_item("Revisar docs")

    assert card.checklist[0].done is True


def test_toggle_checklist_item_reopens_if_done():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    card.add_checklist_item(ChecklistItem("Revisar docs", done=True))

    card.toggle_checklist_item("Revisar docs")

    assert card.checklist[0].done is False


def test_remove_checklist_item_removes_item():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    item = ChecklistItem("Revisar docs")
    card.add_checklist_item(item)

    card.remove_checklist_item("Revisar docs")

    assert item not in card.checklist


# ── Related Cards ─────────────────────────────────────────────────

def test_add_related_card_adds_card_id():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    related_id = CardId.generate()

    card.add_related_card(related_id)

    assert related_id in card.related_cards


def test_add_related_card_self_reference_raises_error():
    card_id = CardId.generate()
    card = Card(
        id=card_id,
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    with pytest.raises(ValueError):
        card.add_related_card(card_id)


def test_remove_related_card_removes_card_id():
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    related_id = CardId.generate()
    card.add_related_card(related_id)

    card.remove_related_card(related_id)

    assert related_id not in card.related_cards