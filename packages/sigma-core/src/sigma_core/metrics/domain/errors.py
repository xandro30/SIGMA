"""Domain errors del BC metrics."""
from sigma_core.shared_kernel.errors import SigmaDomainError


class MetricsDomainError(SigmaDomainError):
    """Base para todos los errores del BC metrics."""


class CycleSummaryNotFoundError(MetricsDomainError):
    """CycleSummary no encontrado para el cycle_id dado."""


class CycleSnapshotNotFoundError(MetricsDomainError):
    """CycleSnapshot no encontrado para el cycle_id dado."""


class MetricsCycleNotFoundError(MetricsDomainError):
    """Cycle no encontrado o no existe ciclo activo en el Space."""
