"""Domain errors del bounded context `planning`.

``PlanningDomainError`` extiende ``SigmaDomainError`` del shared kernel, que
unifica la jerarquía base de errores de dominio en toda la aplicación sin
acoplar a ningún BC concreto.
"""
from __future__ import annotations

from sigma_core.shared_kernel.errors import SigmaDomainError


class PlanningDomainError(SigmaDomainError):
    """Base para todos los errores del BC planning."""


# ── Cycle ────────────────────────────────────────────────────────


class CycleNotFoundError(PlanningDomainError):
    """Cycle no encontrado en repositorio."""


class CycleAlreadyActiveError(PlanningDomainError):
    """Ya existe un ciclo activo en el Space."""

    def __init__(self, space_id: str, active_cycle_id: str) -> None:
        super().__init__(
            f"Space {space_id} already has an active cycle: {active_cycle_id}"
        )
        self.space_id = space_id
        self.active_cycle_id = active_cycle_id


class InvalidCycleTransitionError(PlanningDomainError):
    """Transición de estado de Cycle no permitida."""

    def __init__(self, from_state: str, to_state: str) -> None:
        super().__init__(
            f"Invalid cycle transition: {from_state} -> {to_state}"
        )
        self.from_state = from_state
        self.to_state = to_state


class InvalidBufferError(PlanningDomainError):
    """Valor de `buffer_percentage` fuera del rango 0..100."""


class BudgetNotFoundError(PlanningDomainError):
    """No hay budget para esa Area en el ciclo."""


class InvalidDateRangeError(PlanningDomainError):
    """DateRange con invariante `start <= end` violado."""


# ── Day / TimeBlock ──────────────────────────────────────────────


class DayNotFoundError(PlanningDomainError):
    """Day no encontrado en repositorio."""


class DayNotEmptyError(PlanningDomainError):
    """El Day destino tiene bloques y no se pidió `replace_existing`."""


class BlockNotFoundError(PlanningDomainError):
    """TimeBlock no encontrado en el Day."""


class BlockOverlapError(PlanningDomainError):
    """Un bloque se solapa con otro existente."""

    def __init__(self, block_id: str) -> None:
        super().__init__(f"Block {block_id} overlaps with an existing block")
        self.block_id = block_id


class InvalidTimeBlockError(PlanningDomainError):
    """TimeBlock inválido (duración no positiva, fuera del día, etc.)."""


# ── Templates ────────────────────────────────────────────────────


class DayTemplateNotFoundError(PlanningDomainError):
    """DayTemplate no encontrado en repositorio."""


class WeekTemplateNotFoundError(PlanningDomainError):
    """WeekTemplate no encontrado en repositorio."""


class InvalidWeekStartError(PlanningDomainError):
    """`week_start` no es un lunes."""


class WeekNotFoundError(PlanningDomainError):
    """Week no encontrada en repositorio."""


class CrossSpaceReferenceError(PlanningDomainError):
    """Referencia cruzada ilegal entre agregados de Spaces distintos.

    Ej: un WeekTemplate del space A referencia un DayTemplate del space B.
    """

    def __init__(
        self,
        *,
        source_kind: str,
        source_space_id: str,
        target_kind: str,
        target_space_id: str,
    ) -> None:
        super().__init__(
            f"{source_kind} (space {source_space_id}) cannot reference "
            f"{target_kind} from space {target_space_id}"
        )
        self.source_kind = source_kind
        self.source_space_id = source_space_id
        self.target_kind = target_kind
        self.target_space_id = target_space_id


# ── Queries ──────────────────────────────────────────────────────


class InvalidCardForEtaError(PlanningDomainError):
    """La card no tiene datos suficientes para calcular un ETA."""


class PlanningCardNotFoundError(PlanningDomainError):
    """El card_reader no encontró la card solicitada.

    Error propio del BC planning: evita depender de
    ``task_management.domain.errors.CardNotFoundError`` y mantiene el
    error-handling de planning autocontenido.
    """
