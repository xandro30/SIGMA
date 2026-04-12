from fastapi import Request
from fastapi.responses import JSONResponse
from sigma_core.planning.application.error_handlers import (
    handle_planning_error,
)
from sigma_core.planning.domain.errors import PlanningDomainError
from sigma_core.task_management.application.error_handlers import handle_domain_error
from sigma_core.shared_kernel.errors import SigmaDomainError


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # FastAPI registers handlers with signature ``(request, exc: Exception)``,
    # pero este handler solo se engancha a ``SigmaDomainError`` vía
    # ``add_exception_handler``. Validamos sin ``assert`` (que desaparece con
    # ``python -O``) para que el narrowing sea robusto en producción.
    if not isinstance(exc, SigmaDomainError):
        raise TypeError(
            f"domain_error_handler expects SigmaDomainError, got {type(exc).__name__}"
        )
    result = handle_domain_error(exc)
    return JSONResponse(
        status_code=result.status_code,
        content={
            "error": result.code,
            "message": result.message,
            "detail": result.detail,
        },
    )


async def planning_domain_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handler específico para errores del BC planning.

    Registrado antes que `domain_error_handler` aunque ambos deriven de
    `SigmaDomainError`: al mapear por tipo concreto conseguimos codes/details
    propios del BC sin ensuciar `task_management.handle_domain_error`.
    """
    if not isinstance(exc, PlanningDomainError):
        raise TypeError(
            "planning_domain_error_handler expects PlanningDomainError, "
            f"got {type(exc).__name__}"
        )
    result = handle_planning_error(exc)
    return JSONResponse(
        status_code=result.status_code,
        content={
            "error": result.code,
            "message": result.message,
            "detail": result.detail,
        },
    )