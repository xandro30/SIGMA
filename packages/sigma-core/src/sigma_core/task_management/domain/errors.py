from sigma_core.shared_kernel.errors import SigmaDomainError


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


class CardNotInTriageError(SigmaDomainError):
    """Card is in workflow, not in Triage."""


class InboxNotAllowedError(SigmaDomainError):
    """Card cannot return to Inbox once it has left."""


class AlreadyInStageError(SigmaDomainError):
    """Card is already in that stage."""


class TimerAlreadyRunningError(SigmaDomainError):
    """Card already has a timer running"""


class TimerNotRunningError(SigmaDomainError):
    """Card has no timer running to stop"""


class InvalidTimerClockError(SigmaDomainError):
    """Stop timer received a now timestamp earlier than timer_started_at"""


class SpaceHasActiveTimerError(SigmaDomainError):
    """Another card in the same Space already has an active timer"""

    def __init__(self, space_id: str, active_card_id: str) -> None:
        super().__init__(
            f"Space {space_id} already has an active timer in card {active_card_id}"
        )
        self.space_id = space_id
        self.active_card_id = active_card_id