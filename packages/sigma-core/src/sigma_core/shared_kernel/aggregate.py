"""Mixin para aggregates que emiten domain events.

Un aggregate que use ``EventEmitterMixin`` acumula eventos con
``_record_event`` durante sus mutaciones. El use case que lo invoca
es responsable de despacharlos via ``collect_events`` + ``EventBus.publish``
tras persistir el aggregate.
"""
from __future__ import annotations

from sigma_core.shared_kernel.events import DomainEvent


class EventEmitterMixin:
    """Mixin para acumular domain events pendientes en un aggregate.

    El aggregate debe inicializar ``_pending_events = []`` en su
    ``__post_init__`` o ``__init__``.
    """

    _pending_events: list[DomainEvent]

    def _record_event(self, event: DomainEvent) -> None:
        self._pending_events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        """Devuelve y limpia los eventos pendientes.

        El caller (use case) los despacha tras persistir. Llamar dos
        veces seguidas devuelve lista vacia la segunda vez.
        """
        events = list(self._pending_events)
        self._pending_events.clear()
        return events
