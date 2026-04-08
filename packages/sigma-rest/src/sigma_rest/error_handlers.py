from fastapi import Request
from fastapi.responses import JSONResponse
from sigma_core.task_management.domain.errors import SigmaDomainError
from sigma_core.task_management.application.error_handlers import handle_domain_error


async def domain_error_handler(request: Request, exc: SigmaDomainError) -> JSONResponse:
    result = handle_domain_error(exc)
    return JSONResponse(
        status_code=result.status_code,
        content={
            "error": result.code,
            "message": result.message,
            "detail": result.detail,
        },
    )