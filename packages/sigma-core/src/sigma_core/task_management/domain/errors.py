class SigmaDomainError(Exception):
    """Base para todos los errores de dominio"""


class InvalidWorkflowError(SigmaDomainError):
    """Invariante del workflow de Space violado"""


class StateNotFoundError(SigmaDomainError):
    """WorkflowStateId no existe en el Space"""


class DuplicateStateError(SigmaDomainError):
    """Se intenta añadir un estado con ID ya existente"""


class InvalidTransitionError(SigmaDomainError):
    """Transición de estado no permitida"""


class WipLimitExceededError(SigmaDomainError):
    """Conteo de Cards supera el límite de una WipLimitRule"""


class CardNotFoundError(SigmaDomainError):
    """Card no encontrada en repositorio"""


class SpaceNotFoundError(SigmaDomainError):
    """Space no encontrado en repositorio"""


class AreaNotFoundError(SigmaDomainError):
    """Área no encontrada en repositorio"""


class ProjectNotFoundError(SigmaDomainError):
    """Project no encontrado en repositorio"""


class EpicNotFoundError(SigmaDomainError):
    """Epic no encontrado en repositorio"""


class DuplicateChecklistItemError(SigmaDomainError):
    """Checklist item con texto ya existente en la Card"""


class InvalidEpicSpaceError(SigmaDomainError):
    """Epic pertenece a un Space distinto al de la Card"""