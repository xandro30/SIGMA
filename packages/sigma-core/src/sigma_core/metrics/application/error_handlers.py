"""Mapeo de errores del BC metrics a ErrorResult HTTP."""
from sigma_core.metrics.domain.errors import (
    CycleSnapshotNotFoundError,
    CycleSummaryNotFoundError,
    MetricsCycleNotFoundError,
    MetricsDomainError,
)
from sigma_core.shared_kernel.error_result import ErrorResult


def handle_metrics_error(exc: MetricsDomainError) -> ErrorResult:
    match exc:
        case MetricsCycleNotFoundError():
            return ErrorResult(
                code="metrics_cycle_not_found",
                message=str(exc),
                detail={},
                status_code=404,
            )
        case CycleSnapshotNotFoundError():
            return ErrorResult(
                code="cycle_snapshot_not_found",
                message=str(exc),
                detail={},
                status_code=404,
            )
        case CycleSummaryNotFoundError():
            return ErrorResult(
                code="cycle_summary_not_found",
                message=str(exc),
                detail={},
                status_code=500,
            )
        case _:
            return ErrorResult(
                code="metrics_domain_error",
                message=str(exc),
                detail={},
                status_code=500,
            )
