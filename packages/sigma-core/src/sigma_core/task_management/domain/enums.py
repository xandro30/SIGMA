from enum import Enum


class PreWorkflowStage(str, Enum):
    INBOX = "inbox"
    REFINEMENT = "refinement"
    BACKLOG = "backlog"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"