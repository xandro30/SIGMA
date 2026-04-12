"""Tests unit del InProcessEventBus y EventEmitterMixin."""
from dataclasses import dataclass

import pytest

from sigma_core.shared_kernel.aggregate import EventEmitterMixin
from sigma_core.shared_kernel.events import (
    DomainEvent,
    InProcessEventBus,
)
from sigma_core.shared_kernel.value_objects import Timestamp


@dataclass(frozen=True)
class _TestEvent(DomainEvent):
    payload: str


def _event(payload: str = "test") -> _TestEvent:
    return _TestEvent(occurred_at=Timestamp.now(), payload=payload)


# ── InProcessEventBus ─────────────────────────────────────────


class TestInProcessEventBus:
    @pytest.mark.asyncio
    async def test_publish_sin_subscribers_es_noop(self):
        bus = InProcessEventBus()
        await bus.publish(_event())  # no explota

    @pytest.mark.asyncio
    async def test_publish_invoca_subscriber(self):
        bus = InProcessEventBus()
        received: list[DomainEvent] = []
        bus.subscribe(_TestEvent, lambda e: _async_append(received, e))

        await bus.publish(_event("hello"))

        assert len(received) == 1
        assert received[0].payload == "hello"

    @pytest.mark.asyncio
    async def test_publish_invoca_multiples_subscribers_en_orden(self):
        bus = InProcessEventBus()
        order: list[str] = []
        bus.subscribe(
            _TestEvent,
            lambda e: _async_append(order, "first"),
        )
        bus.subscribe(
            _TestEvent,
            lambda e: _async_append(order, "second"),
        )

        await bus.publish(_event())

        assert order == ["first", "second"]

    @pytest.mark.asyncio
    async def test_publish_propaga_excepcion_del_handler(self):
        bus = InProcessEventBus()

        async def failing_handler(event):
            raise RuntimeError("boom")

        bus.subscribe(_TestEvent, failing_handler)

        with pytest.raises(RuntimeError, match="boom"):
            await bus.publish(_event())

    @pytest.mark.asyncio
    async def test_subscriber_de_otro_tipo_no_se_invoca(self):
        @dataclass(frozen=True)
        class _OtherEvent(DomainEvent):
            pass

        bus = InProcessEventBus()
        received: list[DomainEvent] = []
        bus.subscribe(_OtherEvent, lambda e: _async_append(received, e))

        await bus.publish(_event())

        assert received == []


# ── EventEmitterMixin ─────────────────────────────────────────


class _TestAggregate(EventEmitterMixin):
    def __init__(self) -> None:
        self._pending_events = []

    def do_something(self) -> None:
        self._record_event(_event("action"))


class TestEventEmitterMixin:
    def test_record_acumula_eventos(self):
        agg = _TestAggregate()
        agg.do_something()
        agg.do_something()

        assert len(agg._pending_events) == 2

    def test_collect_devuelve_y_limpia(self):
        agg = _TestAggregate()
        agg.do_something()

        events = agg.collect_events()

        assert len(events) == 1
        assert agg._pending_events == []

    def test_collect_doble_devuelve_vacio(self):
        agg = _TestAggregate()
        agg.do_something()

        agg.collect_events()
        second = agg.collect_events()

        assert second == []


# ── Helper ────────────────────────────────────────────────────


async def _async_append(lst, item):
    lst.append(item)
