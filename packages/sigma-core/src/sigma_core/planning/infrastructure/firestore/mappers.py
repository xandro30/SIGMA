"""Mappers Firestore ↔ Dominio para el BC `planning`.

Schemas documentados:

cycle:
  {id, space_id, name,
   date_range: {start, end},  # ISO date strings
   state,                     # "draft"|"active"|"closed"
   area_budgets: {<area_id>: <minutes int>},
   buffer_percentage,
   created_at, updated_at, closed_at}  # datetimes aware

day:
  {id, space_id, date,  # ISO date
   blocks: [{id, start_at, duration, area_id, notes}],
   created_at, updated_at}

day_template:
  {id, space_id, name,
   blocks: [{id, start_minutes, duration, area_id, notes}],  # start_minutes desde 00:00
   created_at, updated_at}

week_template:
  {id, space_id, name,
   slots: {"0": <day_template_id | null>, ..., "6": ...},  # DayOfWeek.value como str
   created_at, updated_at}

Índices compuestos esperados en Firestore:
  - `cycles`:   `space_id + state`        (get_active_by_space)
  - `days`:     `space_id + date`         (get_by_space_and_date, list_by_space_and_range)
  - `day_templates`:   `space_id`         (list_by_space)
  - `week_templates`:  `space_id`         (list_by_space)
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sigma_core.shared_kernel.config import get_app_timezone
from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.aggregates.week import Week
from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.enums import CycleState, DayOfWeek
from sigma_core.planning.domain.value_objects import (
    BlockId,
    CycleId,
    DateRange,
    DayId,
    DayTemplateId,
    TimeOfDay,
    WeekId,
    WeekTemplateId,
)
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp




# ── Snapshot helper (propio del BC) ───────────────────────────────


def snapshot_data(doc) -> dict[str, Any]:
    """Narrow `DocumentSnapshot.to_dict()` so el return type no sea `dict | None`."""
    data = doc.to_dict()
    if data is None:
        raise ValueError(f"Firestore snapshot {doc.id} has no data")
    return data


# ── Timestamp / date helpers (estrictos, ADR-003) ────────────────


def _ts_to_primitive(ts: Timestamp) -> datetime:
    return ts.value


def _ts_from_primitive(dt: datetime) -> Timestamp:
    return Timestamp(dt.astimezone(get_app_timezone()))


def _date_to_primitive(d: date) -> str:
    return d.isoformat()


def _date_from_primitive(s: str) -> date:
    return date.fromisoformat(s)


# ── Cycle ────────────────────────────────────────────────────────


def cycle_to_dict(cycle: Cycle) -> dict[str, Any]:
    return {
        "id": cycle.id.value,
        "space_id": cycle.space_id.value,
        "name": cycle.name,
        "date_range": {
            "start": _date_to_primitive(cycle.date_range.start),
            "end": _date_to_primitive(cycle.date_range.end),
        },
        "state": cycle.state.value,
        "area_budgets": {
            area_id.value: minutes.value
            for area_id, minutes in cycle.area_budgets.items()
        },
        "buffer_percentage": cycle.buffer_percentage,
        "created_at": _ts_to_primitive(cycle.created_at),
        "updated_at": _ts_to_primitive(cycle.updated_at),
        "closed_at": (
            _ts_to_primitive(cycle.closed_at)
            if cycle.closed_at is not None
            else None
        ),
    }


def cycle_from_dict(data: dict[str, Any]) -> Cycle:
    return Cycle(
        id=CycleId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        name=data["name"],
        date_range=DateRange(
            start=_date_from_primitive(data["date_range"]["start"]),
            end=_date_from_primitive(data["date_range"]["end"]),
        ),
        state=CycleState(data["state"]),
        area_budgets={
            AreaId(area_id): Minutes(minutes)
            for area_id, minutes in data["area_budgets"].items()
        },
        buffer_percentage=data["buffer_percentage"],
        created_at=_ts_from_primitive(data["created_at"]),
        updated_at=_ts_from_primitive(data["updated_at"]),
        closed_at=(
            _ts_from_primitive(data["closed_at"])
            if data["closed_at"] is not None
            else None
        ),
    )


# ── Day + TimeBlock ──────────────────────────────────────────────


def _time_block_to_dict(block: TimeBlock) -> dict[str, Any]:
    return {
        "id": block.id.value,
        "start_at": _ts_to_primitive(block.start_at),
        "duration": block.duration.value,
        "area_id": block.area_id.value if block.area_id is not None else None,
        "notes": block.notes,
    }


def _time_block_from_dict(data: dict[str, Any]) -> TimeBlock:
    return TimeBlock(
        id=BlockId(data["id"]),
        start_at=_ts_from_primitive(data["start_at"]),
        duration=Minutes(data["duration"]),
        area_id=(
            AreaId(data["area_id"]) if data["area_id"] is not None else None
        ),
        notes=data["notes"],
    )


def day_to_dict(day: Day) -> dict[str, Any]:
    return {
        "id": day.id.value,
        "space_id": day.space_id.value,
        "date": _date_to_primitive(day.date),
        "blocks": [_time_block_to_dict(b) for b in day.blocks],
        "created_at": _ts_to_primitive(day.created_at),
        "updated_at": _ts_to_primitive(day.updated_at),
    }


def day_from_dict(data: dict[str, Any]) -> Day:
    return Day(
        id=DayId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        date=_date_from_primitive(data["date"]),
        blocks=[_time_block_from_dict(b) for b in data["blocks"]],
        created_at=_ts_from_primitive(data["created_at"]),
        updated_at=_ts_from_primitive(data["updated_at"]),
    )


# ── DayTemplate + DayTemplateBlock ───────────────────────────────


def _day_template_block_to_dict(block: DayTemplateBlock) -> dict[str, Any]:
    return {
        "id": block.id.value,
        "start_minutes": block.start_at.to_minutes(),
        "duration": block.duration.value,
        "area_id": block.area_id.value if block.area_id is not None else None,
        "notes": block.notes,
    }


def _day_template_block_from_dict(
    data: dict[str, Any],
) -> DayTemplateBlock:
    start_minutes = int(data["start_minutes"])
    return DayTemplateBlock(
        id=BlockId(data["id"]),
        start_at=TimeOfDay(
            hour=start_minutes // 60,
            minute=start_minutes % 60,
        ),
        duration=Minutes(data["duration"]),
        area_id=(
            AreaId(data["area_id"]) if data["area_id"] is not None else None
        ),
        notes=data["notes"],
    )


def day_template_to_dict(template: DayTemplate) -> dict[str, Any]:
    return {
        "id": template.id.value,
        "space_id": template.space_id.value,
        "name": template.name,
        "blocks": [_day_template_block_to_dict(b) for b in template.blocks],
        "created_at": _ts_to_primitive(template.created_at),
        "updated_at": _ts_to_primitive(template.updated_at),
    }


def day_template_from_dict(data: dict[str, Any]) -> DayTemplate:
    template = DayTemplate(
        id=DayTemplateId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        name=data["name"],
        blocks=[],  # rehydrate_blocks valida y ordena sin tocar updated_at
        created_at=_ts_from_primitive(data["created_at"]),
        updated_at=_ts_from_primitive(data["updated_at"]),
    )
    blocks = [_day_template_block_from_dict(b) for b in data["blocks"]]
    template.rehydrate_blocks(blocks)
    return template


# ── WeekTemplate ─────────────────────────────────────────────────


def week_template_to_dict(template: WeekTemplate) -> dict[str, Any]:
    slots: dict[str, str | None] = {}
    for dow in DayOfWeek:
        slot = template.slots.get(dow)
        slots[str(dow.value)] = slot.value if slot is not None else None
    return {
        "id": template.id.value,
        "space_id": template.space_id.value,
        "name": template.name,
        "slots": slots,
        "created_at": _ts_to_primitive(template.created_at),
        "updated_at": _ts_to_primitive(template.updated_at),
    }


def week_template_from_dict(data: dict[str, Any]) -> WeekTemplate:
    slots: dict[DayOfWeek, DayTemplateId | None] = {}
    for dow in DayOfWeek:
        raw = data["slots"][str(dow.value)]
        slots[dow] = DayTemplateId(raw) if raw is not None else None
    return WeekTemplate(
        id=WeekTemplateId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        name=data["name"],
        slots=slots,
        created_at=_ts_from_primitive(data["created_at"]),
        updated_at=_ts_from_primitive(data["updated_at"]),
    )


# ── Week ─────────────────────────────────────────────────────────


def week_to_dict(week: Week) -> dict[str, Any]:
    return {
        "id": week.id.value,
        "space_id": week.space_id.value,
        "week_start": _date_to_primitive(week.week_start),
        "applied_template_id": (
            week.applied_template_id.value
            if week.applied_template_id is not None
            else None
        ),
        "notes": week.notes,
        "created_at": _ts_to_primitive(week.created_at),
        "updated_at": _ts_to_primitive(week.updated_at),
    }


def week_from_dict(data: dict[str, Any]) -> Week:
    raw_template_id = data["applied_template_id"]
    return Week(
        id=WeekId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        week_start=_date_from_primitive(data["week_start"]),
        applied_template_id=(
            WeekTemplateId(raw_template_id)
            if raw_template_id is not None
            else None
        ),
        notes=data["notes"],
        created_at=_ts_from_primitive(data["created_at"]),
        updated_at=_ts_from_primitive(data["updated_at"]),
    )
