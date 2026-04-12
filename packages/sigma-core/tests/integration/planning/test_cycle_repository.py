from datetime import date

import pytest

from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleState
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.planning.infrastructure.firestore.cycle_repository import (
    FirestoreCycleRepository,
)
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId


def _cycle(
    space_id: SpaceId,
    *,
    state: CycleState = CycleState.DRAFT,
    area_budgets: dict[AreaId, Minutes] | None = None,
    name: str = "Abril",
) -> Cycle:
    return Cycle(
        id=CycleId.generate(),
        space_id=space_id,
        name=name,
        date_range=DateRange(start=date(2026, 4, 1), end=date(2026, 4, 30)),
        state=state,
        area_budgets=dict(area_budgets or {}),
        buffer_percentage=15,
    )


@pytest.mark.asyncio
async def test_save_and_get_cycle(firestore_client):
    repo = FirestoreCycleRepository(firestore_client)
    cycle = _cycle(SpaceId.generate())

    await repo.save(cycle)
    result = await repo.get_by_id(cycle.id)

    assert result is not None
    assert result.id == cycle.id
    assert result.space_id == cycle.space_id
    assert result.state == CycleState.DRAFT
    assert result.buffer_percentage == 15


@pytest.mark.asyncio
async def test_get_cycle_not_found(firestore_client):
    repo = FirestoreCycleRepository(firestore_client)
    assert await repo.get_by_id(CycleId.generate()) is None


@pytest.mark.asyncio
async def test_get_active_by_space_devuelve_el_activo(firestore_client):
    repo = FirestoreCycleRepository(firestore_client)
    space_id = SpaceId.generate()

    draft = _cycle(space_id, state=CycleState.DRAFT, name="Draft")
    active = _cycle(space_id, state=CycleState.ACTIVE, name="Active")
    await repo.save(draft)
    await repo.save(active)

    result = await repo.get_active_by_space(space_id)

    assert result is not None
    assert result.id == active.id


@pytest.mark.asyncio
async def test_get_active_by_space_sin_activo_devuelve_none(firestore_client):
    repo = FirestoreCycleRepository(firestore_client)
    space_id = SpaceId.generate()
    await repo.save(_cycle(space_id, state=CycleState.DRAFT))

    assert await repo.get_active_by_space(space_id) is None


@pytest.mark.asyncio
async def test_list_by_space_devuelve_solo_los_del_space(firestore_client):
    repo = FirestoreCycleRepository(firestore_client)
    space_a = SpaceId.generate()
    space_b = SpaceId.generate()

    await repo.save(_cycle(space_a, name="A1"))
    await repo.save(_cycle(space_a, name="A2"))
    await repo.save(_cycle(space_b, name="B1"))

    result = await repo.list_by_space(space_a)
    assert {c.name for c in result} == {"A1", "A2"}


@pytest.mark.asyncio
async def test_delete_cycle(firestore_client):
    repo = FirestoreCycleRepository(firestore_client)
    cycle = _cycle(SpaceId.generate())
    await repo.save(cycle)

    await repo.delete(cycle.id)
    assert await repo.get_by_id(cycle.id) is None


@pytest.mark.asyncio
async def test_round_trip_area_budgets(firestore_client):
    repo = FirestoreCycleRepository(firestore_client)
    area_a = AreaId.generate()
    area_b = AreaId.generate()
    cycle = _cycle(
        SpaceId.generate(),
        area_budgets={area_a: Minutes(600), area_b: Minutes(300)},
    )

    await repo.save(cycle)
    result = await repo.get_by_id(cycle.id)

    assert result is not None
    assert result.area_budgets[area_a] == Minutes(600)
    assert result.area_budgets[area_b] == Minutes(300)
