"""Domain events infrastructure.

Provee la base para domain events in-process: el tipo base ``DomainEvent``,
los eventos inter-BC (``CycleClosed``), el protocolo ``EventBus`` y la
implementacion ``InProcessEventBus``.

Los handlers se ejecutan secuencialmente en el mismo request. Si un handler
falla, la excepcion propaga al caller — no se tragan errores.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Protocol

from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.value_objects import AreaId, CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId


# ── Base ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DomainEvent:
    """Base de todos los domain events."""

    occurred_at: Timestamp


# ── Eventos inter-BC ──────────────────────────────────────────────


@dataclass(frozen=True)
class CycleClosed(DomainEvent):
    """Emitido por Cycle.close(). Contrato inter-BC planning → metrics."""

    cycle_id: CycleId
    space_id: SpaceId
    date_range: DateRange


@dataclass(frozen=True)
class WorkSessionCompleted(DomainEvent):
    """Emitido por WorkSession.complete() o .stop(save=True).
    Contrato inter-BC tracking → task_management."""

    space_id: SpaceId
    card_id: CardId
    area_id: AreaId | None
    project_id: ProjectId | None
    epic_id: EpicId | None
    description: str
    minutes: int


# ── EventBus ──────────────────────────────────────────────────────

EventHandler = Callable[[Any], Coroutine[Any, Any, None]]


class EventBus(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...

    def subscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> None: ...


class InProcessEventBus:
    """Event bus in-process. Handlers secuenciales, fallo propaga.

    Uso: wiring en el adaptador (sigma-rest main.py) al arrancar la app.
    Los tests inyectan un ``FakeEventBus`` o una instancia real con
    handlers fake.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = (
            defaultdict(list)
        )

    def subscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            await handler(event)
