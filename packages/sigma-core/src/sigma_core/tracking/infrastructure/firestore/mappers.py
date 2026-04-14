"""Mappers Firestore ↔ dominio para el BC tracking."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sigma_core.shared_kernel.config import get_app_timezone
from sigma_core.shared_kernel.value_objects import AreaId, CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId
from sigma_core.tracking.domain.aggregates.tracking_entry import TrackingEntry
from sigma_core.tracking.domain.aggregates.work_session import WorkSession, WorkSessionState
from sigma_core.tracking.domain.value_objects.entry_type import EntryType
from sigma_core.tracking.domain.value_objects.ids import TrackingEntryId, WorkSessionId
from sigma_core.tracking.domain.value_objects.timer import Timer, TimerTechnique


# ── Snapshot helper ───────────────────────────────────────────────

def snapshot_data(doc) -> dict[str, Any]:
    data = doc.to_dict()
    if data is None:
        raise ValueError(f"Firestore snapshot {doc.id} has no data")
    return data


# ── Timestamp helpers ─────────────────────────────────────────────

def _to_dt(ts: Timestamp) -> datetime:
    return ts.value


def _from_dt(dt: datetime) -> Timestamp:
    return Timestamp(dt.astimezone(get_app_timezone()))


# ── WorkSession ───────────────────────────────────────────────────

def work_session_to_dict(session: WorkSession) -> dict[str, Any]:
    return {
        "id": session.id.value,
        "space_id": session.space_id.value,
        "card_id": session.card_id.value,
        "area_id": session.area_id.value if session.area_id else None,
        "project_id": session.project_id.value if session.project_id else None,
        "epic_id": session.epic_id.value if session.epic_id else None,
        "description": session.description,
        "timer": {
            "technique": session.timer.technique.value,
            "work_minutes": session.timer.work_minutes,
            "break_minutes": session.timer.break_minutes,
            "num_rounds": session.timer.num_rounds,
        },
        "completed_rounds": session.completed_rounds,
        "state": session.state.value,
        "session_started_at": _to_dt(session.session_started_at),
        "current_started_at": _to_dt(session.current_started_at),
    }


def work_session_from_dict(data: dict[str, Any]) -> WorkSession:
    timer_data = data["timer"]
    timer = Timer(
        technique=TimerTechnique(timer_data["technique"]),
        work_minutes=timer_data["work_minutes"],
        break_minutes=timer_data["break_minutes"],
        num_rounds=timer_data["num_rounds"],
    )
    return WorkSession(
        id=WorkSessionId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        card_id=CardId(data["card_id"]),
        area_id=AreaId(data["area_id"]) if data.get("area_id") else None,
        project_id=ProjectId(data["project_id"]) if data.get("project_id") else None,
        epic_id=EpicId(data["epic_id"]) if data.get("epic_id") else None,
        description=data["description"],
        timer=timer,
        completed_rounds=data["completed_rounds"],
        state=WorkSessionState(data["state"]),
        session_started_at=_from_dt(data["session_started_at"]),
        current_started_at=_from_dt(data["current_started_at"]),
    )


# ── TrackingEntry ─────────────────────────────────────────────────

def tracking_entry_to_dict(entry: TrackingEntry) -> dict[str, Any]:
    return {
        "id": entry.id.value,
        "space_id": entry.space_id.value,
        "card_id": entry.card_id.value if entry.card_id else None,
        "area_id": entry.area_id.value if entry.area_id else None,
        "project_id": entry.project_id.value if entry.project_id else None,
        "epic_id": entry.epic_id.value if entry.epic_id else None,
        "entry_type": entry.entry_type.value,
        "description": entry.description,
        "minutes": entry.minutes,
        "logged_at": _to_dt(entry.logged_at),
    }


def tracking_entry_from_dict(data: dict[str, Any]) -> TrackingEntry:
    return TrackingEntry(
        id=TrackingEntryId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        card_id=CardId(data["card_id"]) if data.get("card_id") else None,
        area_id=AreaId(data["area_id"]) if data.get("area_id") else None,
        project_id=ProjectId(data["project_id"]) if data.get("project_id") else None,
        epic_id=EpicId(data["epic_id"]) if data.get("epic_id") else None,
        entry_type=EntryType(data["entry_type"]),
        description=data["description"],
        minutes=data["minutes"],
        logged_at=_from_dt(data["logged_at"]),
    )
