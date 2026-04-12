from sigma_core.task_management.domain.aggregates.card import Card
from sigma_rest.schemas.card_schemas import CardResponse, ChecklistItemResponse


def card_to_response(card: Card) -> CardResponse:
    return CardResponse(
        id=card.id.value,
        space_id=card.space_id.value,
        title=card.title.value,
        description=card.description,
        pre_workflow_stage=card.pre_workflow_stage.value if card.pre_workflow_stage else None,
        workflow_state_id=card.workflow_state_id.value if card.workflow_state_id else None,
        area_id=card.area_id.value if card.area_id else None,
        project_id=card.project_id.value if card.project_id else None,
        epic_id=card.epic_id.value if card.epic_id else None,
        priority=card.priority.value if card.priority else None,
        labels=list(card.labels),
        topics=list(card.topics),
        urls=[u.value for u in card.urls],
        checklist=[ChecklistItemResponse(text=i.text, done=i.done) for i in card.checklist],
        related_cards=[c.value for c in card.related_cards],
        due_date=card.due_date.isoformat() if card.due_date else None,
        size=card.size.value if card.size else None,
        actual_time=card.actual_time.value,
        timer_started_at=card.timer_started_at.value.isoformat() if card.timer_started_at else None,
        created_at=card.created_at.value.isoformat(),
        updated_at=card.updated_at.value.isoformat(),
    )