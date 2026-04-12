from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from sigma_core.planning.domain.errors import InvalidWeekStartError
from sigma_core.planning.domain.value_objects import WeekId, WeekTemplateId
from sigma_core.shared_kernel.value_objects import SpaceId, Timestamp


MONDAY_WEEKDAY = 0  # ISO: lunes es 0 en `date.weekday()`


@dataclass
class Week:
    """Contenedor semanal sobre un Space concreto.

    Invariantes:
    - ``week_start`` es siempre un lunes.
    - ``notes`` es texto libre (puede estar vacío).
    - ``applied_template_id`` es una referencia opcional al ``WeekTemplate``
      que se materializó sobre esta semana (se acompaña normalmente de la
      creación de los 7 ``Day`` correspondientes, pero ambos agregados son
      independientes: ``Day`` puede existir sin ``Week``).

    Lazy creation: al crearse un ``Week`` NO se materializan los 7 ``Day``
    de su rango. Los días se materializan solo cuando:
      (a) se aplica explícitamente un ``WeekTemplate`` a la semana, o
      (b) el usuario crea un ``Day`` concreto dentro del rango.
    El consumidor debe estar preparado para encontrarse una semana con 0-7
    ``Day`` materializados y tratar los días vacíos como "sin contenido".
    """

    id: WeekId
    space_id: SpaceId
    week_start: date
    applied_template_id: WeekTemplateId | None = None
    notes: str = ""
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)

    def __post_init__(self) -> None:
        if self.week_start.weekday() != MONDAY_WEEKDAY:
            raise InvalidWeekStartError(
                f"week_start {self.week_start} is not a Monday"
            )

    # ── Mutations ───────────────────────────────────────────────

    def set_notes(self, notes: str) -> None:
        self.notes = notes
        self._touch()

    def record_template_applied(self, template_id: WeekTemplateId) -> None:
        """Marca la semana como derivada de un ``WeekTemplate`` concreto.

        No materializa los ``Day``: esa es responsabilidad del use case que
        coordina Week + DayTemplate + Day en una operación atómica.
        """
        self.applied_template_id = template_id
        self._touch()

    def clear_applied_template(self) -> None:
        self.applied_template_id = None
        self._touch()

    # ── Internal helpers ────────────────────────────────────────

    def _touch(self) -> None:
        self.updated_at = Timestamp.now()
