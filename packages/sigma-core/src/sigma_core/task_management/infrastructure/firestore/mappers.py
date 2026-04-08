from datetime import datetime, date
from zoneinfo import ZoneInfo

from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import (
    Space, WorkflowState, Transition,
)
from sigma_core.task_management.domain.entities.area import Area
from sigma_core.task_management.domain.entities.project import Project
from sigma_core.task_management.domain.entities.epic import Epic
from sigma_core.task_management.domain.enums import (
    PreWorkflowStage, Priority, ProjectStatus,
)
from sigma_core.task_management.domain.value_objects import (
    CardId, SpaceId, WorkflowStateId, AreaId, ProjectId, EpicId,
    CardTitle, SpaceName, Url, ChecklistItem, Timestamp,
)


MADRID_TZ = ZoneInfo("Europe/Madrid")


# ── Timestamp helpers ─────────────────────────────────────────────

def _to_timestamp(ts: Timestamp) -> datetime:
    return ts.value


def _from_timestamp(dt: datetime) -> Timestamp:
    return Timestamp(dt.astimezone(MADRID_TZ))


def _to_date_str(d: date | None) -> str | None:
    return d.isoformat() if d else None


def _from_date_str(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None


# ── Space ─────────────────────────────────────────────────────────

def space_to_dict(space: Space) -> dict:
    return {
        "id": space.id.value,
        "name": space.name.value,
        "workflow_states": [
            {
                "id": s.id.value,
                "name": s.name,
                "order": s.order,
            }
            for s in space.workflow_states
        ],
        "transitions": [
            {
                "from_id": t.from_id.value,
                "to_id": t.to_id.value,
            }
            for t in space.transitions
        ],
        "created_at": _to_timestamp(space.created_at),
        "updated_at": _to_timestamp(space.updated_at),
    }


def space_from_dict(data: dict) -> Space:
    workflow_states = [
        WorkflowState(
            id=WorkflowStateId(s["id"]),
            name=s["name"],
            order=s["order"],
        )
        for s in data.get("workflow_states", [])
    ]
    transitions = [
        Transition(
            from_id=WorkflowStateId(t["from_id"]),
            to_id=WorkflowStateId(t["to_id"]),
        )
        for t in data.get("transitions", [])
    ]
    return Space(
        id=SpaceId(data["id"]),
        name=SpaceName(data["name"]),
        workflow_states=workflow_states,
        transitions=transitions,
        created_at=_from_timestamp(data["created_at"]),
        updated_at=_from_timestamp(data["updated_at"]),
    )


# ── Card ──────────────────────────────────────────────────────────

def card_to_dict(card: Card) -> dict:
    return {
        "id": card.id.value,
        "space_id": card.space_id.value,
        "title": card.title.value,
        "description": card.description,
        "pre_workflow_stage": card.pre_workflow_stage.value if card.pre_workflow_stage else None,
        "workflow_state_id": card.workflow_state_id.value if card.workflow_state_id else None,
        "area_id": card.area_id.value if card.area_id else None,
        "project_id": card.project_id.value if card.project_id else None,
        "epic_id": card.epic_id.value if card.epic_id else None,
        "priority": card.priority.value if card.priority else None,
        "labels": list(card.labels),
        "topics": list(card.topics),
        "urls": [u.value for u in card.urls],
        "checklist": [{"text": i.text, "done": i.done} for i in card.checklist],
        "related_cards": [c.value for c in card.related_cards],
        "due_date": _to_date_str(card.due_date),
        "created_at": _to_timestamp(card.created_at),
        "updated_at": _to_timestamp(card.updated_at),
    }


def card_from_dict(data: dict) -> Card:
    return Card(
        id=CardId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        title=CardTitle(data["title"]),
        description=data.get("description"),
        pre_workflow_stage=PreWorkflowStage(data["pre_workflow_stage"]) if data.get("pre_workflow_stage") else None,
        workflow_state_id=WorkflowStateId(data["workflow_state_id"]) if data.get("workflow_state_id") else None,
        area_id=AreaId(data["area_id"]) if data.get("area_id") else None,
        project_id=ProjectId(data["project_id"]) if data.get("project_id") else None,
        epic_id=EpicId(data["epic_id"]) if data.get("epic_id") else None,
        priority=Priority(data["priority"]) if data.get("priority") else None,
        labels=set(data.get("labels", [])),
        topics=set(data.get("topics", [])),
        urls=[Url(u) for u in data.get("urls", [])],
        checklist=[
            ChecklistItem(text=i["text"], done=i["done"])
            for i in data.get("checklist", [])
        ],
        related_cards=[CardId(c) for c in data.get("related_cards", [])],
        due_date=_from_date_str(data.get("due_date")),
        created_at=_from_timestamp(data["created_at"]),
        updated_at=_from_timestamp(data["updated_at"]),
    )


# ── Area ──────────────────────────────────────────────────────────

def area_to_dict(area: Area) -> dict:
    return {
        "id": area.id.value,
        "name": area.name,
        "description": area.description,
        "objectives": area.objectives,
        "created_at": _to_timestamp(area.created_at),
        "updated_at": _to_timestamp(area.updated_at),
    }


def area_from_dict(data: dict) -> Area:
    return Area(
        id=AreaId(data["id"]),
        name=data["name"],
        description=data.get("description"),
        objectives=data.get("objectives", []),
        created_at=_from_timestamp(data["created_at"]),
        updated_at=_from_timestamp(data["updated_at"]),
    )


# ── Project ───────────────────────────────────────────────────────

def project_to_dict(project: Project) -> dict:
    return {
        "id": project.id.value,
        "name": project.name,
        "description": project.description,
        "objectives": project.objectives,
        "area_id": project.area_id.value,
        "status": project.status.value,
        "created_at": _to_timestamp(project.created_at),
        "updated_at": _to_timestamp(project.updated_at),
    }


def project_from_dict(data: dict) -> Project:
    return Project(
        id=ProjectId(data["id"]),
        name=data["name"],
        description=data.get("description"),
        objectives=data.get("objectives", []),
        area_id=AreaId(data["area_id"]),
        status=ProjectStatus(data["status"]),
        created_at=_from_timestamp(data["created_at"]),
        updated_at=_from_timestamp(data["updated_at"]),
    )


# ── Epic ──────────────────────────────────────────────────────────

def epic_to_dict(epic: Epic) -> dict:
    return {
        "id": epic.id.value,
        "space_id": epic.space_id.value,
        "project_id": epic.project_id.value,
        "area_id": epic.area_id.value,
        "name": epic.name,
        "description": epic.description,
        "created_at": _to_timestamp(epic.created_at),
        "updated_at": _to_timestamp(epic.updated_at),
    }


def epic_from_dict(data: dict) -> Epic:
    return Epic(
        id=EpicId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        project_id=ProjectId(data["project_id"]),
        area_id=AreaId(data["area_id"]),
        name=data["name"],
        description=data.get("description"),
        created_at=_from_timestamp(data["created_at"]),
        updated_at=_from_timestamp(data["updated_at"]),
    )