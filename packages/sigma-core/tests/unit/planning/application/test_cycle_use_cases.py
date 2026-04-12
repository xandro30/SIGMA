from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from sigma_core.planning.application.use_cases.cycle.activate_cycle import (
    ActivateCycle,
    ActivateCycleCommand,
)
from sigma_core.planning.application.use_cases.cycle.close_cycle import (
    CloseCycle,
    CloseCycleCommand,
)
from sigma_core.planning.application.use_cases.cycle.create_cycle import (
    CreateCycle,
    CreateCycleCommand,
)
from sigma_core.planning.application.use_cases.cycle.delete_cycle import (
    DeleteCycle,
    DeleteCycleCommand,
)
from sigma_core.planning.application.use_cases.cycle.remove_area_budget import (
    RemoveAreaBudget,
    RemoveAreaBudgetCommand,
)
from sigma_core.planning.application.use_cases.cycle.set_area_budget import (
    SetAreaBudget,
    SetAreaBudgetCommand,
)
from sigma_core.planning.application.use_cases.cycle.set_buffer_percentage import (
    SetBufferPercentage,
    SetBufferPercentageCommand,
)
from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleState
from sigma_core.planning.domain.errors import (
    CycleAlreadyActiveError,
    CycleNotFoundError,
    InvalidCycleTransitionError,
)
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.events import DomainEvent, InProcessEventBus
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp


MADRID = ZoneInfo("Europe/Madrid")


def ts() -> Timestamp:
    return Timestamp(datetime(2026, 4, 11, 12, 0, tzinfo=MADRID))


def _range() -> DateRange:
    return DateRange(start=date(2026, 4, 1), end=date(2026, 4, 30))


class FakeCycleRepository:
    def __init__(self) -> None:
        self._store: dict[str, Cycle] = {}

    async def save(self, cycle: Cycle) -> None:
        self._store[cycle.id.value] = cycle

    async def get_by_id(self, cycle_id: CycleId) -> Cycle | None:
        return self._store.get(cycle_id.value)

    async def get_active_by_space(self, space_id: SpaceId, cycle_type=None) -> Cycle | None:
        for cycle in self._store.values():
            if cycle.space_id != space_id or cycle.state != CycleState.ACTIVE:
                continue
            if cycle_type is not None and cycle.cycle_type != cycle_type:
                continue
            return cycle
        return None

    async def list_active_by_space(self, space_id: SpaceId) -> list[Cycle]:
        return [c for c in self._store.values() if c.space_id == space_id and c.state == CycleState.ACTIVE]

    async def list_by_space(self, space_id: SpaceId) -> list[Cycle]:
        return [c for c in self._store.values() if c.space_id == space_id]

    async def delete(self, cycle_id: CycleId) -> None:
        self._store.pop(cycle_id.value, None)


def _seed_draft_cycle(repo: FakeCycleRepository, space_id: SpaceId) -> Cycle:
    cycle = Cycle(
        id=CycleId.generate(),
        space_id=space_id,
        name="Seeded",
        date_range=_range(),
    )
    repo._store[cycle.id.value] = cycle
    return cycle


# ── CreateCycle ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_cycle_persiste_en_estado_draft():
    repo = FakeCycleRepository()
    uc = CreateCycle(cycle_repo=repo)
    space_id = SpaceId.generate()

    cycle_id = await uc.execute(
        CreateCycleCommand(
            space_id=space_id,
            name="April",
            date_range=_range(),
        )
    )

    stored = await repo.get_by_id(cycle_id)
    assert stored is not None
    assert stored.state == CycleState.DRAFT
    assert stored.space_id == space_id
    assert stored.name == "April"


# ── ActivateCycle ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_activate_cycle_activa_si_no_hay_otro_activo():
    repo = FakeCycleRepository()
    space_id = SpaceId.generate()
    cycle = _seed_draft_cycle(repo, space_id)
    uc = ActivateCycle(cycle_repo=repo)

    await uc.execute(ActivateCycleCommand(cycle_id=cycle.id))

    reloaded = await repo.get_by_id(cycle.id)
    assert reloaded is not None
    assert reloaded.state == CycleState.ACTIVE


@pytest.mark.asyncio
async def test_activate_cycle_rechaza_si_existe_otro_activo_en_el_space():
    repo = FakeCycleRepository()
    space_id = SpaceId.generate()
    first = _seed_draft_cycle(repo, space_id)
    first.activate()
    second = _seed_draft_cycle(repo, space_id)
    uc = ActivateCycle(cycle_repo=repo)

    with pytest.raises(CycleAlreadyActiveError) as exc:
        await uc.execute(ActivateCycleCommand(cycle_id=second.id))

    assert exc.value.space_id == space_id.value
    assert exc.value.active_cycle_id == first.id.value


@pytest.mark.asyncio
async def test_activate_cycle_permite_otro_activo_en_otro_space():
    repo = FakeCycleRepository()
    space_a = SpaceId.generate()
    space_b = SpaceId.generate()
    first = _seed_draft_cycle(repo, space_a)
    first.activate()
    second = _seed_draft_cycle(repo, space_b)
    uc = ActivateCycle(cycle_repo=repo)

    await uc.execute(ActivateCycleCommand(cycle_id=second.id))

    reloaded = await repo.get_by_id(second.id)
    assert reloaded is not None
    assert reloaded.state == CycleState.ACTIVE


@pytest.mark.asyncio
async def test_activate_cycle_falla_si_id_no_existe():
    repo = FakeCycleRepository()
    uc = ActivateCycle(cycle_repo=repo)

    with pytest.raises(CycleNotFoundError):
        await uc.execute(ActivateCycleCommand(cycle_id=CycleId.generate()))


@pytest.mark.asyncio
async def test_activate_cycle_propaga_invalid_transition_si_closed():
    repo = FakeCycleRepository()
    space_id = SpaceId.generate()
    cycle = _seed_draft_cycle(repo, space_id)
    cycle.close(ts())
    uc = ActivateCycle(cycle_repo=repo)

    with pytest.raises(InvalidCycleTransitionError):
        await uc.execute(ActivateCycleCommand(cycle_id=cycle.id))


# ── CloseCycle ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_close_cycle_cierra_ciclo_activo():
    repo = FakeCycleRepository()
    cycle = _seed_draft_cycle(repo, SpaceId.generate())
    cycle.activate()
    uc = CloseCycle(cycle_repo=repo, event_bus=InProcessEventBus())

    await uc.execute(CloseCycleCommand(cycle_id=cycle.id, now=ts()))

    reloaded = await repo.get_by_id(cycle.id)
    assert reloaded is not None
    assert reloaded.state == CycleState.CLOSED
    assert reloaded.closed_at is not None


@pytest.mark.asyncio
async def test_close_cycle_cierra_ciclo_draft():
    repo = FakeCycleRepository()
    cycle = _seed_draft_cycle(repo, SpaceId.generate())
    uc = CloseCycle(cycle_repo=repo, event_bus=InProcessEventBus())

    await uc.execute(CloseCycleCommand(cycle_id=cycle.id, now=ts()))

    reloaded = await repo.get_by_id(cycle.id)
    assert reloaded is not None
    assert reloaded.state == CycleState.CLOSED


@pytest.mark.asyncio
async def test_close_cycle_falla_si_no_existe():
    repo = FakeCycleRepository()
    uc = CloseCycle(cycle_repo=repo, event_bus=InProcessEventBus())

    with pytest.raises(CycleNotFoundError):
        await uc.execute(CloseCycleCommand(cycle_id=CycleId.generate(), now=ts()))


@pytest.mark.asyncio
async def test_close_cycle_despacha_cycle_closed_event():
    from sigma_core.shared_kernel.events import CycleClosed

    repo = FakeCycleRepository()
    cycle = _seed_draft_cycle(repo, SpaceId.generate())
    cycle.activate()
    received: list[DomainEvent] = []

    async def capture(event):
        received.append(event)

    bus = InProcessEventBus()
    bus.subscribe(CycleClosed, capture)
    uc = CloseCycle(cycle_repo=repo, event_bus=bus)

    await uc.execute(CloseCycleCommand(cycle_id=cycle.id, now=ts()))

    assert len(received) == 1
    assert isinstance(received[0], CycleClosed)
    assert received[0].cycle_id == cycle.id
    assert received[0].space_id == cycle.space_id


# ── DeleteCycle ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_cycle_permite_borrar_draft():
    repo = FakeCycleRepository()
    cycle = _seed_draft_cycle(repo, SpaceId.generate())
    uc = DeleteCycle(cycle_repo=repo)

    await uc.execute(DeleteCycleCommand(cycle_id=cycle.id))

    assert await repo.get_by_id(cycle.id) is None


@pytest.mark.asyncio
async def test_delete_cycle_rechaza_active():
    repo = FakeCycleRepository()
    cycle = _seed_draft_cycle(repo, SpaceId.generate())
    cycle.activate()
    uc = DeleteCycle(cycle_repo=repo)

    with pytest.raises(InvalidCycleTransitionError):
        await uc.execute(DeleteCycleCommand(cycle_id=cycle.id))

    assert await repo.get_by_id(cycle.id) is not None


@pytest.mark.asyncio
async def test_delete_cycle_rechaza_closed():
    repo = FakeCycleRepository()
    cycle = _seed_draft_cycle(repo, SpaceId.generate())
    cycle.close(ts())
    uc = DeleteCycle(cycle_repo=repo)

    with pytest.raises(InvalidCycleTransitionError):
        await uc.execute(DeleteCycleCommand(cycle_id=cycle.id))


@pytest.mark.asyncio
async def test_delete_cycle_falla_si_no_existe():
    repo = FakeCycleRepository()
    uc = DeleteCycle(cycle_repo=repo)

    with pytest.raises(CycleNotFoundError):
        await uc.execute(DeleteCycleCommand(cycle_id=CycleId.generate()))


# ── SetAreaBudget / RemoveAreaBudget ─────────────────────────────


@pytest.mark.asyncio
async def test_set_area_budget_actualiza_ciclo():
    repo = FakeCycleRepository()
    cycle = _seed_draft_cycle(repo, SpaceId.generate())
    area_id = AreaId.generate()
    uc = SetAreaBudget(cycle_repo=repo)

    await uc.execute(
        SetAreaBudgetCommand(cycle_id=cycle.id, area_id=area_id, minutes=Minutes(600))
    )

    reloaded = await repo.get_by_id(cycle.id)
    assert reloaded is not None
    assert reloaded.area_budgets[area_id] == Minutes(600)


@pytest.mark.asyncio
async def test_set_area_budget_falla_si_no_existe():
    repo = FakeCycleRepository()
    uc = SetAreaBudget(cycle_repo=repo)

    with pytest.raises(CycleNotFoundError):
        await uc.execute(
            SetAreaBudgetCommand(
                cycle_id=CycleId.generate(),
                area_id=AreaId.generate(),
                minutes=Minutes(600),
            )
        )


@pytest.mark.asyncio
async def test_remove_area_budget_quita_entrada():
    repo = FakeCycleRepository()
    cycle = _seed_draft_cycle(repo, SpaceId.generate())
    area_id = AreaId.generate()
    cycle.set_area_budget(area_id, Minutes(600))
    uc = RemoveAreaBudget(cycle_repo=repo)

    await uc.execute(
        RemoveAreaBudgetCommand(cycle_id=cycle.id, area_id=area_id)
    )

    reloaded = await repo.get_by_id(cycle.id)
    assert reloaded is not None
    assert area_id not in reloaded.area_budgets


@pytest.mark.asyncio
async def test_remove_area_budget_falla_si_no_existe_cycle():
    repo = FakeCycleRepository()
    uc = RemoveAreaBudget(cycle_repo=repo)

    with pytest.raises(CycleNotFoundError):
        await uc.execute(
            RemoveAreaBudgetCommand(
                cycle_id=CycleId.generate(),
                area_id=AreaId.generate(),
            )
        )


# ── SetBufferPercentage ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_set_buffer_percentage_actualiza_ciclo():
    repo = FakeCycleRepository()
    cycle = _seed_draft_cycle(repo, SpaceId.generate())
    uc = SetBufferPercentage(cycle_repo=repo)

    await uc.execute(
        SetBufferPercentageCommand(cycle_id=cycle.id, percentage=50)
    )

    reloaded = await repo.get_by_id(cycle.id)
    assert reloaded is not None
    assert reloaded.buffer_percentage == 50


@pytest.mark.asyncio
async def test_set_buffer_percentage_falla_si_cycle_no_existe():
    repo = FakeCycleRepository()
    uc = SetBufferPercentage(cycle_repo=repo)

    with pytest.raises(CycleNotFoundError):
        await uc.execute(
            SetBufferPercentageCommand(cycle_id=CycleId.generate(), percentage=50)
        )
