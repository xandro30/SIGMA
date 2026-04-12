from datetime import datetime, date
from typing import Any

from sigma_core.shared_kernel.config import get_app_timezone
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import (
    Space, WorkflowState, Transition,
)
from sigma_core.task_management.domain.entities.area import Area
from sigma_core.task_management.domain.entities.project import Project
from sigma_core.task_management.domain.entities.epic import Epic
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.task_management.domain.enums import (
    PreWorkflowStage,
    Priority,
    ProjectStatus,
)
from sigma_core.shared_kernel.value_objects import (
    CardId,
    SpaceId,
    AreaId,
    Timestamp,
    Minutes,
    SizeMapping,
)
from sigma_core.task_management.domain.value_objects import (
    WorkflowStateId,
    ProjectId,
    EpicId,
    CardTitle,
    SpaceName,
    Url,
    ChecklistItem,
)




# ── Snapshot helpers ──────────────────────────────────────────────

def snapshot_data(doc) -> dict[str, Any]:
    """
    Narrow the return of `DocumentSnapshot.to_dict()` so it cannot be None.
    Raises if the snapshot has no data (should not happen once `doc.exists`).
    """
    data = doc.to_dict()
    if data is None:
        raise ValueError(f"Firestore snapshot {doc.id} has no data")
    return data


# ── Timestamp helpers ─────────────────────────────────────────────

def _to_timestamp(ts: Timestamp) -> datetime:
    return ts.value


def _from_timestamp(dt: datetime) -> Timestamp:
    return Timestamp(dt.astimezone(get_app_timezone()))


def _to_date_str(d: date | None) -> str | None:
    return d.isoformat() if d else None


def _from_date_str(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None


# ── Space ─────────────────────────────────────────────────────────

def _size_mapping_to_dict(mapping: SizeMapping | None) -> dict[str, int] | None:
    return mapping.to_primitive() if mapping is not None else None


def _size_mapping_from_dict(data: dict[str, int] | None) -> SizeMapping | None:
    return SizeMapping.from_primitive(data) if data is not None else None


def space_to_dict(space: Space) -> dict[str, Any]:
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
        "size_mapping": _size_mapping_to_dict(space.size_mapping),
        "created_at": _to_timestamp(space.created_at),
        "updated_at": _to_timestamp(space.updated_at),
    }


def space_from_dict(data: dict[str, Any]) -> Space:
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
        size_mapping=_size_mapping_from_dict(data["size_mapping"]),
        created_at=_from_timestamp(data["created_at"]),
        updated_at=_from_timestamp(data["updated_at"]),
    )


# ── Card ──────────────────────────────────────────────────────────

def card_to_dict(card: Card) -> dict[str, Any]:
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
        "size": card.size.value if card.size else None,
        "actual_time": card.actual_time.value,
        "timer_started_at": _to_timestamp(card.timer_started_at) if card.timer_started_at else None,
        "completed_at": _to_timestamp(card.completed_at) if card.completed_at else None,
        "entered_workflow_at": _to_timestamp(card.entered_workflow_at) if card.entered_workflow_at else None,
        "created_at": _to_timestamp(card.created_at),
        "updated_at": _to_timestamp(card.updated_at),
    }


def card_from_dict(data: dict[str, Any]) -> Card:
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
        size=CardSize(data["size"]) if data["size"] else None,
        actual_time=Minutes(data["actual_time"]),
        timer_started_at=_from_timestamp(data["timer_started_at"]) if data["timer_started_at"] else None,
        completed_at=_from_timestamp(data["completed_at"]) if data["completed_at"] else None,
        entered_workflow_at=_from_timestamp(data["entered_workflow_at"]) if data["entered_workflow_at"] else None,
        created_at=_from_timestamp(data["created_at"]),
        updated_at=_from_timestamp(data["updated_at"]),
    )


# ── Area ──────────────────────────────────────────────────────────

def area_to_dict(area: Area) -> dict[str, Any]:
    return {
        "id": area.id.value,
        "name": area.name,
        "description": area.description,
        "objectives": area.objectives,
        "color_id": area.color_id,
        "created_at": _to_timestamp(area.created_at),
        "updated_at": _to_timestamp(area.updated_at),
    }


def area_from_dict(data: dict[str, Any]) -> Area:
    return Area(
        id=AreaId(data["id"]),
        name=data["name"],
        description=data.get("description"),
        objectives=data.get("objectives") if isinstance(data.get("objectives"), str) else None,
        color_id=data.get("color_id"),
        created_at=_from_timestamp(data["created_at"]),
        updated_at=_from_timestamp(data["updated_at"]),
    )


# ── Project ───────────────────────────────────────────────────────

def project_to_dict(project: Project) -> dict[str, Any]:
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


def project_from_dict(data: dict[str, Any]) -> Project:
    return Project(
        id=ProjectId(data["id"]),
        name=data["name"],
        description=data.get("description"),
        objectives=data.get("objectives") if isinstance(data.get("objectives"), str) else None,
        area_id=AreaId(data["area_id"]),
        status=ProjectStatus(data["status"]),
        created_at=_from_timestamp(data["created_at"]),
        updated_at=_from_timestamp(data["updated_at"]),
    )


# ── Epic ──────────────────────────────────────────────────────────

def epic_to_dict(epic: Epic) -> dict[str, Any]:
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


def epic_from_dict(data: dict[str, Any]) -> Epic:
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