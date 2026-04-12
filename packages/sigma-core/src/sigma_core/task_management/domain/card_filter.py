from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sigma_core.task_management.domain.aggregates.card import Card

from sigma_core.task_management.domain.enums import PreWorkflowStage, Priority
from sigma_core.shared_kernel.value_objects import AreaId
from sigma_core.task_management.domain.value_objects import (
    ProjectId,
    EpicId,
    WorkflowStateId,
)


# ── String predicates ─────────────────────────────────────────────

@dataclass(frozen=True)
class StringEquals:
    value: str

@dataclass(frozen=True)
class StringNotEquals:
    value: str

@dataclass(frozen=True)
class StringContains:
    value: str

@dataclass(frozen=True)
class StringNotContains:
    value: str

StringPredicate = StringEquals | StringNotEquals | StringContains | StringNotContains


# ── List predicates ───────────────────────────────────────────────

@dataclass(frozen=True)
class ListHasAny:
    values: frozenset[str]

@dataclass(frozen=True)
class ListHasAll:
    values: frozenset[str]

@dataclass(frozen=True)
class ListHasNone:
    values: frozenset[str]

ListPredicate = ListHasAny | ListHasAll | ListHasNone


# ── Date predicates ───────────────────────────────────────────────

@dataclass(frozen=True)
class DateEquals:
    value: date

@dataclass(frozen=True)
class DateBefore:
    value: date

@dataclass(frozen=True)
class DateAfter:
    value: date

DatePredicate = DateEquals | DateBefore | DateAfter


# ── Helpers ───────────────────────────────────────────────────────

def _match_string(predicate: StringPredicate, value: str) -> bool:
    match predicate:
        case StringEquals(v):       return value == v
        case StringNotEquals(v):    return value != v
        case StringContains(v):     return v in value
        case StringNotContains(v):  return v not in value
    return True

def _match_list(predicate: ListPredicate, values: set[str] | list[str]) -> bool:
    s = set(values)
    match predicate:
        case ListHasAny(vs):  return bool(s & vs)
        case ListHasAll(vs):  return vs <= s
        case ListHasNone(vs): return not (s & vs)
    return True

def _match_date(predicate: DatePredicate, value: date) -> bool:
    match predicate:
        case DateEquals(v):  return value == v
        case DateBefore(v):  return value < v
        case DateAfter(v):   return value > v
    return True


# ── CardFilter ────────────────────────────────────────────────────

@dataclass(frozen=True)
class CardFilter:
    title:              StringPredicate | None = None
    description:        StringPredicate | None = None
    priority:           list[Priority] | None = None
    labels:             ListPredicate | None = None
    topics:             ListPredicate | None = None
    area_id:            list[AreaId] | None = None
    project_id:         list[ProjectId] | None = None
    epic_id:            list[EpicId] | None = None
    due_date:           DatePredicate | None = None
    pre_workflow_stage: list[PreWorkflowStage] | None = None
    workflow_state_id:  list[WorkflowStateId] | None = None

    def matches(self, card: Card) -> bool:
        if self.title and not _match_string(self.title, card.title.value):
            return False
        if self.description and card.description:
            if not _match_string(self.description, card.description):
                return False
        if self.priority and card.priority not in self.priority:
            return False
        if self.labels and not _match_list(self.labels, card.labels):
            return False
        if self.topics and not _match_list(self.topics, card.topics):
            return False
        if self.area_id and card.area_id not in self.area_id:
            return False
        if self.project_id and card.project_id not in self.project_id:
            return False
        if self.epic_id and card.epic_id not in self.epic_id:
            return False
        if self.due_date and card.due_date:
            if not _match_date(self.due_date, card.due_date):
                return False
        if self.pre_workflow_stage and card.pre_workflow_stage not in self.pre_workflow_stage:
            return False
        if self.workflow_state_id and card.workflow_state_id not in self.workflow_state_id:
            return False
        return True