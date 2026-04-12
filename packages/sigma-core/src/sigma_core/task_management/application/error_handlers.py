from sigma_core.shared_kernel.error_result import ErrorResult
from sigma_core.shared_kernel.errors import SigmaDomainError
from sigma_core.task_management.domain.errors import (
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
    TimerAlreadyRunningError,
    TimerNotRunningError,
    InvalidTimerClockError,
    SpaceHasActiveTimerError,
)


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
        case TimerAlreadyRunningError():
            return ErrorResult(code="timer_already_running", message=str(exc), detail={}, status_code=409)
        case TimerNotRunningError():
            return ErrorResult(code="timer_not_running", message=str(exc), detail={}, status_code=409)
        case InvalidTimerClockError():
            return ErrorResult(code="invalid_timer_clock", message=str(exc), detail={}, status_code=422)
        case SpaceHasActiveTimerError():
            return ErrorResult(
                code="space_has_active_timer",
                message=str(exc),
                detail={
                    "space_id": exc.space_id,
                    "active_card_id": exc.active_card_id,
                },
                status_code=409,
            )
        case _:
            return ErrorResult(code="domain_error", message=str(exc), detail={}, status_code=500)