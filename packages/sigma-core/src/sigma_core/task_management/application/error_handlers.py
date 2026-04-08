from dataclasses import dataclass
from sigma_core.task_management.domain.errors import (
    SigmaDomainError,
    InvalidWorkflowError,
    StateNotFoundError,
    DuplicateStateError,
    InvalidTransitionError,
    WipLimitExceededError,
    CardNotFoundError,
    SpaceNotFoundError,
    AreaNotFoundError,
    ProjectNotFoundError,
    EpicNotFoundError,
    DuplicateChecklistItemError,
    InvalidEpicSpaceError,
    CardNotInTriageError,
    InboxNotAllowedError,
    AlreadyInStageError,
)


@dataclass(frozen=True)
class ErrorResult:
    code: str
    message: str
    detail: dict
    status_code: int


def handle_domain_error(exc: SigmaDomainError) -> ErrorResult:
    match exc:
        case InvalidWorkflowError():
            return ErrorResult(code="invalid_workflow", message=str(exc), detail={}, status_code=422)
        case StateNotFoundError():
            return ErrorResult(code="state_not_found", message=str(exc), detail={}, status_code=404)
        case DuplicateStateError():
            return ErrorResult(code="duplicate_state", message=str(exc), detail={}, status_code=409)
        case InvalidTransitionError():
            return ErrorResult(code="invalid_transition", message=str(exc), detail={}, status_code=422)
        case WipLimitExceededError():
            return ErrorResult(code="wip_limit_exceeded", message=str(exc), detail={}, status_code=422)
        case CardNotFoundError():
            return ErrorResult(code="card_not_found", message=str(exc), detail={}, status_code=404)
        case SpaceNotFoundError():
            return ErrorResult(code="space_not_found", message=str(exc), detail={}, status_code=404)
        case AreaNotFoundError():
            return ErrorResult(code="area_not_found", message=str(exc), detail={}, status_code=404)
        case ProjectNotFoundError():
            return ErrorResult(code="project_not_found", message=str(exc), detail={}, status_code=404)
        case EpicNotFoundError():
            return ErrorResult(code="epic_not_found", message=str(exc), detail={}, status_code=404)
        case DuplicateChecklistItemError():
            return ErrorResult(code="duplicate_checklist_item", message=str(exc), detail={}, status_code=409)
        case InvalidEpicSpaceError():
            return ErrorResult(code="invalid_epic_space", message=str(exc), detail={}, status_code=422)
        case CardNotInTriageError():
            return ErrorResult(code="card_not_in_triage", message=str(exc), detail={}, status_code=422)
        case InboxNotAllowedError():
            return ErrorResult(code="inbox_not_allowed", message=str(exc), detail={}, status_code=422)
        case AlreadyInStageError():
            return ErrorResult(code="already_in_stage", message=str(exc), detail={}, status_code=409)
        case _:
            return ErrorResult(code="domain_error", message=str(exc), detail={}, status_code=500)