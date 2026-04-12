"""Mapeo de errores de dominio del BC `planning` a `ErrorResult` HTTP.

Reutiliza `ErrorResult` del BC task_management para mantener una única
envoltura en los adaptadores (el router FastAPI espera siempre la misma
forma). La función `handle_planning_error` es consumida por el exception
handler en `sigma-rest`.
"""
from sigma_core.planning.domain.errors import (
    BlockNotFoundError,
    BlockOverlapError,
    BudgetNotFoundError,
    CrossSpaceReferenceError,
    CycleAlreadyActiveError,
    CycleNotFoundError,
    DayNotEmptyError,
    DayNotFoundError,
    DayTemplateNotFoundError,
    InvalidBufferError,
    InvalidCardForEtaError,
    InvalidCycleTransitionError,
    InvalidDateRangeError,
    InvalidTimeBlockError,
    InvalidWeekStartError,
    PlanningCardNotFoundError,
    PlanningDomainError,
    WeekNotFoundError,
    WeekTemplateNotFoundError,
)
from sigma_core.shared_kernel.error_result import ErrorResult


def handle_planning_error(exc: PlanningDomainError) -> ErrorResult:
    match exc:
        # ── Not found (404) ────────────────────────────────────
        case CycleNotFoundError():
            return ErrorResult(
                code="cycle_not_found",
                message=str(exc),
                detail={},
                status_code=404,
            )
        case DayNotFoundError():
            return ErrorResult(
                code="day_not_found",
                message=str(exc),
                detail={},
                status_code=404,
            )
        case BlockNotFoundError():
            return ErrorResult(
                code="block_not_found",
                message=str(exc),
                detail={},
                status_code=404,
            )
        case DayTemplateNotFoundError():
            return ErrorResult(
                code="day_template_not_found",
                message=str(exc),
                detail={},
                status_code=404,
            )
        case WeekTemplateNotFoundError():
            return ErrorResult(
                code="week_template_not_found",
                message=str(exc),
                detail={},
                status_code=404,
            )
        case WeekNotFoundError():
            return ErrorResult(
                code="week_not_found",
                message=str(exc),
                detail={},
                status_code=404,
            )
        case PlanningCardNotFoundError():
            return ErrorResult(
                code="card_not_found",
                message=str(exc),
                detail={},
                status_code=404,
            )

        # ── Conflict (409) ─────────────────────────────────────
        case CycleAlreadyActiveError():
            return ErrorResult(
                code="cycle_already_active",
                message=str(exc),
                detail={
                    "space_id": exc.space_id,
                    "active_cycle_id": exc.active_cycle_id,
                },
                status_code=409,
            )
        case DayNotEmptyError():
            return ErrorResult(
                code="day_not_empty",
                message=str(exc),
                detail={},
                status_code=409,
            )
        case BlockOverlapError():
            return ErrorResult(
                code="block_overlap",
                message=str(exc),
                detail={"block_id": exc.block_id},
                status_code=409,
            )

        # ── Unprocessable (422) ────────────────────────────────
        case InvalidCycleTransitionError():
            return ErrorResult(
                code="invalid_cycle_transition",
                message=str(exc),
                detail={
                    "from_state": exc.from_state,
                    "to_state": exc.to_state,
                },
                status_code=422,
            )
        case InvalidBufferError():
            return ErrorResult(
                code="invalid_buffer",
                message=str(exc),
                detail={},
                status_code=422,
            )
        case InvalidDateRangeError():
            return ErrorResult(
                code="invalid_date_range",
                message=str(exc),
                detail={},
                status_code=422,
            )
        case InvalidTimeBlockError():
            return ErrorResult(
                code="invalid_time_block",
                message=str(exc),
                detail={},
                status_code=422,
            )
        case InvalidWeekStartError():
            return ErrorResult(
                code="invalid_week_start",
                message=str(exc),
                detail={},
                status_code=422,
            )
        case InvalidCardForEtaError():
            return ErrorResult(
                code="invalid_card_for_eta",
                message=str(exc),
                detail={},
                status_code=422,
            )
        case BudgetNotFoundError():
            return ErrorResult(
                code="budget_not_found",
                message=str(exc),
                detail={},
                status_code=422,
            )
        case CrossSpaceReferenceError():
            return ErrorResult(
                code="cross_space_reference",
                message=str(exc),
                detail={
                    "source_kind": exc.source_kind,
                    "source_space_id": exc.source_space_id,
                    "target_kind": exc.target_kind,
                    "target_space_id": exc.target_space_id,
                },
                status_code=422,
            )

        # ── Fallback ───────────────────────────────────────────
        case _:
            return ErrorResult(
                code="planning_domain_error",
                message=str(exc),
                detail={},
                status_code=500,
            )
