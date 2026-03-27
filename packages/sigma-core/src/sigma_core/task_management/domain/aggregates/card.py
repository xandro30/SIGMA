from datetime import date
from dataclasses import dataclass, field
from sigma_core.task_management.domain.enums import PreWorkflowStage, Priority
from sigma_core.task_management.domain.errors import DuplicateChecklistItemError
from sigma_core.task_management.domain.value_objects import (
    CardId, SpaceId, CardTitle, WorkflowStateId,
    AreaId, ProjectId, EpicId, Timestamp, Url, ChecklistItem,
)


@dataclass
class Card:
    id: CardId
    space_id: SpaceId
    title: CardTitle
    pre_workflow_stage: PreWorkflowStage | None
    workflow_state_id: WorkflowStateId | None
    description: str | None = None
    due_date: date | None = None
    priority: Priority | None = None
    area_id: AreaId | None = None
    project_id: ProjectId | None = None
    epic_id: EpicId | None = None
    labels: set[str] = field(default_factory=set)
    topics: set[str] = field(default_factory=set)
    urls: list[Url] = field(default_factory=list)
    checklist: list[ChecklistItem] = field(default_factory=list)
    related_cards: list[CardId] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)

    def __post_init__(self) -> None:
        both_set = self.pre_workflow_stage is not None and self.workflow_state_id is not None
        none_set = self.pre_workflow_stage is None and self.workflow_state_id is None
        if both_set or none_set:
            raise ValueError(
                "Card must have exactly one of pre_workflow_stage or workflow_state_id"
            )

    def move_to_workflow_state(self, state_id: WorkflowStateId) -> None:
        self.workflow_state_id = state_id
        self.pre_workflow_stage = None
        self.updated_at = Timestamp.now()

    def move_to_pre_workflow(self, stage: PreWorkflowStage) -> None:
        self.pre_workflow_stage = stage
        self.workflow_state_id = None
        self.updated_at = Timestamp.now()

    def add_label(self, label: str) -> None:
        stripped = label.strip()
        if not stripped:
            raise ValueError("Label cannot be empty")
        self.labels.add(stripped)
        self.updated_at = Timestamp.now()

    def remove_label(self, label: str) -> None:
        self.labels.discard(label)
        self.updated_at = Timestamp.now()

    def add_topic(self, topic: str) -> None:
        stripped = topic.strip()
        if not stripped:
            raise ValueError("Topic cannot be empty")
        self.topics.add(stripped)
        self.updated_at = Timestamp.now()

    def remove_topic(self, topic: str) -> None:
        self.topics.discard(topic)
        self.updated_at = Timestamp.now()

    def add_url(self, url: Url) -> None:
        if url not in self.urls:
            self.urls.append(url)
            self.updated_at = Timestamp.now()

    def remove_url(self, url: Url) -> None:
        self.urls = [u for u in self.urls if u != url]
        self.updated_at = Timestamp.now()

    def add_checklist_item(self, item: ChecklistItem) -> None:
        if any(i.text == item.text for i in self.checklist):
            raise DuplicateChecklistItemError(item.text)
        self.checklist.append(item)
        self.updated_at = Timestamp.now()

    def toggle_checklist_item(self, text: str) -> None:
        self.checklist = [
            item.complete() if item.text == text and not item.done
            else item.reopen() if item.text == text and item.done
            else item
            for item in self.checklist
        ]
        self.updated_at = Timestamp.now()

    def remove_checklist_item(self, text: str) -> None:
        self.checklist = [i for i in self.checklist if i.text != text]
        self.updated_at = Timestamp.now()

    def add_related_card(self, card_id: CardId) -> None:
        if card_id == self.id:
            raise ValueError("A card cannot be related to itself")
        if card_id not in self.related_cards:
            self.related_cards.append(card_id)
            self.updated_at = Timestamp.now()

    def remove_related_card(self, card_id: CardId) -> None:
        self.related_cards = [c for c in self.related_cards if c != card_id]
        self.updated_at = Timestamp.now()