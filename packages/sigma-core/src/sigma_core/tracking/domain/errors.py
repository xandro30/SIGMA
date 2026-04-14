"""Errores de dominio del BC tracking."""
from sigma_core.shared_kernel.errors import SigmaDomainError


class TrackingDomainError(SigmaDomainError):
    pass


class WorkSessionNotFoundError(TrackingDomainError):
    pass


class WorkSessionAlreadyActiveError(TrackingDomainError):
    pass


class InvalidWorkSessionTransitionError(TrackingDomainError):
    pass
