"""Error handlers para el BC tracking."""
from sigma_core.shared_kernel.error_result import ErrorResult
from sigma_core.tracking.domain.errors import (
    TrackingDomainError,
    WorkSessionAlreadyActiveError,
    WorkSessionNotFoundError,
    InvalidWorkSessionTransitionError,
)


def handle_tracking_error(exc: TrackingDomainError) -> ErrorResult:
    match exc:
        case WorkSessionNotFoundError():
            return ErrorResult(
                code="work_session_not_found",
                message=str(exc),
                detail={},
                status_code=404,
            )
        case WorkSessionAlreadyActiveError():
            return ErrorResult(
                code="work_session_already_active",
                message=str(exc),
                detail={},
                status_code=409,
            )
        case InvalidWorkSessionTransitionError():
            return ErrorResult(
                code="invalid_work_session_transition",
                message=str(exc),
                detail={},
                status_code=422,
            )
        case _:
            return ErrorResult(
                code="tracking_domain_error",
                message=str(exc),
                detail={},
                status_code=500,
            )
