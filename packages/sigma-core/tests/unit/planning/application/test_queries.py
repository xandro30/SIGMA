from datetime import date

import pytest

from sigma_core.planning.application.queries.card_eta import (
    CardEtaResult,
    GetCardEta,
    GetCardEtaQuery,
)
from sigma_core.planning.application.queries.space_capacity import (
    GetSpaceCapacity,
    GetSpaceCapacityQuery,
    SpaceCapacityResult,
)
from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleState
from sigma_core.planning.domain.errors import (
    BudgetNotFoundError,
    CycleNotFoundError,
    InvalidCardForEtaError,
)
from sigma_core.planning.domain.read_models.card_view import CardView
from sigma_core.planning.domain.read_models.space_view import SpaceView
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.planning.domain.errors import PlanningCardNotFoundError
from sigma_core.shared_kernel.value_objects import (
    AreaId,
    CardId,
    Minutes,
    SizeMapping,
    SpaceId,
    Timestamp,
)
from tests.fakes.fake_card_reader import FakeCardReader
from tests.fakes.fake_cycle_repository import FakeCycleRepository
from tests.fakes.fake_space_reader import FakeSpaceReader


# ── Helpers ─────────────────────────────────────────────────


def _range() -> DateRange:
    return DateRange(start=date(2026, 4, 1), end=date(2026, 4, 30))


def _space_view(
    size_mapping: SizeMapping | None = None,
    space_id: SpaceId | None = None,
) -> SpaceView:
    return SpaceView(
        id=space_id if space_id is not None else SpaceId.generate(),
        size_mapping=size_mapping if size_mapping is not None else SizeMapping.default(),
    )


def _cycle(space_id: SpaceId, area_budgets: dict[AreaId, Minutes]) -> Cycle:
    return Cycle(
        id=CycleId.generate(),
        space_id=space_id,
        name="Abril",
        date_range=_range(),
        state=CycleState.ACTIVE,
        area_budgets=dict(area_budgets),
        buffer_percentage=20,
    )


def _completed_at_in_range() -> Timestamp:
    """Un instante dentro del rango _range() (abril 2026)."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    return Timestamp(
        datetime(2026, 4, 15, 12, 0, 0, tzinfo=ZoneInfo("Europe/Madrid"))
    )


def _card_view(
    space_id: SpaceId,
    *,
    size: CardSize | None = CardSize.M,
    area_id: AreaId | None,
    actual_minutes: int = 0,
    completed_at: Timestamp | None = None,
    card_id: CardId | None = None,
) -> CardView:
    return CardView(
        id=card_id if card_id is not None else CardId.generate(),
        space_id=space_id,
        area_id=area_id,
        size=size,
        actual_time=Minutes(actual_minutes),
        completed_at=completed_at,
    )


# ── GetSpaceCapacity ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_space_capacity_agrega_consumo_por_area_usando_actual_time():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))

    area_a = AreaId.generate()
    area_b = AreaId.generate()
    cycle = _cycle(space_id, {area_a: Minutes(600), area_b: Minutes(300)})
    await cycle_repo.save(cycle)

    completed = _completed_at_in_range()
    card_reader.add(
        _card_view(space_id, area_id=area_a, actual_minutes=120, completed_at=completed)
    )
    card_reader.add(
        _card_view(space_id, area_id=area_a, actual_minutes=60, completed_at=completed)
    )
    card_reader.add(
        _card_view(space_id, area_id=area_b, actual_minutes=100, completed_at=completed)
    )

    uc = GetSpaceCapacity(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )

    result: SpaceCapacityResult = await uc.execute(
        GetSpaceCapacityQuery(space_id=space_id)
    )

    assert result.cycle_id == cycle.id
    assert result.buffer_percentage == 20
    by_area = {ac.area_id: ac for ac in result.areas}
    assert by_area[area_a].consumed_minutes == 180
    assert by_area[area_a].budget_minutes == 600
    # effective budget = 600 * (1 - 0.20) = 480 → remaining = 480 - 180 = 300
    assert by_area[area_a].remaining_minutes == 300
    assert by_area[area_b].consumed_minutes == 100
    assert by_area[area_b].remaining_minutes == (300 * 80 // 100) - 100


@pytest.mark.asyncio
async def test_space_capacity_usa_size_si_actual_time_es_cero():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))
    area_a = AreaId.generate()
    cycle = _cycle(space_id, {area_a: Minutes(1000)})
    await cycle_repo.save(cycle)

    # M size -> 480 min según default mapping
    card_reader.add(
        _card_view(
            space_id,
            area_id=area_a,
            size=CardSize.M,
            actual_minutes=0,
            completed_at=_completed_at_in_range(),
        )
    )

    uc = GetSpaceCapacity(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    result = await uc.execute(GetSpaceCapacityQuery(space_id=space_id))

    by_area = {ac.area_id: ac for ac in result.areas}
    assert by_area[area_a].consumed_minutes == 480


@pytest.mark.asyncio
async def test_space_capacity_excluye_cards_no_completadas():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))
    area_a = AreaId.generate()
    cycle = _cycle(space_id, {area_a: Minutes(600)})
    await cycle_repo.save(cycle)

    # Not completed → excluded by list_completed_in_range
    card_reader.add(
        _card_view(
            space_id,
            area_id=area_a,
            actual_minutes=500,
            completed_at=None,
        )
    )
    card_reader.add(
        _card_view(
            space_id,
            area_id=area_a,
            actual_minutes=100,
            completed_at=_completed_at_in_range(),
        )
    )

    uc = GetSpaceCapacity(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    result = await uc.execute(GetSpaceCapacityQuery(space_id=space_id))

    by_area = {ac.area_id: ac for ac in result.areas}
    assert by_area[area_a].consumed_minutes == 100


@pytest.mark.asyncio
async def test_space_capacity_excluye_cards_completadas_fuera_del_rango():
    """Cards completadas antes o despues del date_range del cycle no cuentan."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))
    area_a = AreaId.generate()
    cycle = _cycle(space_id, {area_a: Minutes(600)})
    await cycle_repo.save(cycle)

    madrid = ZoneInfo("Europe/Madrid")
    # Marzo — fuera del rango (que es abril)
    card_reader.add(
        _card_view(
            space_id,
            area_id=area_a,
            actual_minutes=300,
            completed_at=Timestamp(datetime(2026, 3, 15, 12, 0, tzinfo=madrid)),
        )
    )
    # Mayo — fuera del rango
    card_reader.add(
        _card_view(
            space_id,
            area_id=area_a,
            actual_minutes=200,
            completed_at=Timestamp(datetime(2026, 5, 1, 9, 0, tzinfo=madrid)),
        )
    )
    # Abril — dentro del rango
    card_reader.add(
        _card_view(
            space_id,
            area_id=area_a,
            actual_minutes=50,
            completed_at=Timestamp(datetime(2026, 4, 10, 12, 0, tzinfo=madrid)),
        )
    )

    uc = GetSpaceCapacity(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    result = await uc.execute(GetSpaceCapacityQuery(space_id=space_id))

    by_area = {ac.area_id: ac for ac in result.areas}
    assert by_area[area_a].consumed_minutes == 50


@pytest.mark.asyncio
async def test_space_capacity_permite_remaining_negativo():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))
    area_a = AreaId.generate()
    cycle = _cycle(space_id, {area_a: Minutes(100)})
    await cycle_repo.save(cycle)

    card_reader.add(
        _card_view(
            space_id,
            area_id=area_a,
            actual_minutes=500,
            completed_at=_completed_at_in_range(),
        )
    )

    uc = GetSpaceCapacity(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    result = await uc.execute(GetSpaceCapacityQuery(space_id=space_id))

    by_area = {ac.area_id: ac for ac in result.areas}
    assert by_area[area_a].remaining_minutes < 0


@pytest.mark.asyncio
async def test_space_capacity_falla_sin_cycle_activo():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))

    uc = GetSpaceCapacity(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    with pytest.raises(CycleNotFoundError):
        await uc.execute(GetSpaceCapacityQuery(space_id=space_id))


# ── GetCardEta ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_card_eta_calcula_con_size_y_buffer():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))
    area_a = AreaId.generate()
    # Budget 1200 → daily_capacity = 1200 // 5 = 240
    cycle = _cycle(space_id, {area_a: Minutes(1200)})
    await cycle_repo.save(cycle)

    # Size M = 480 min → raw_days = ceil(480/240) = 2
    # buffered_days = ceil(2 * 1.20) = 3
    card = _card_view(
        space_id,
        size=CardSize.M,
        area_id=area_a,
        actual_minutes=0,
    )
    card_reader.add(card)

    uc = GetCardEta(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    # Viernes 2026-04-10 como referencia
    result: CardEtaResult = await uc.execute(
        GetCardEtaQuery(card_id=card.id, reference_date=date(2026, 4, 10))
    )

    assert result.estimated_minutes == 480
    assert result.daily_capacity_minutes == 240
    # raw: 2 workdays desde viernes = lunes 2026-04-13 (salta sábado y domingo)
    assert result.raw_completion_date == date(2026, 4, 14)
    # buffered: 3 workdays desde viernes = miércoles 2026-04-15
    assert result.buffered_completion_date == date(2026, 4, 15)


@pytest.mark.asyncio
async def test_card_eta_falla_si_card_no_existe():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    uc = GetCardEta(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    with pytest.raises(PlanningCardNotFoundError):
        await uc.execute(
            GetCardEtaQuery(
                card_id=CardId.generate(), reference_date=date(2026, 4, 10)
            )
        )


@pytest.mark.asyncio
async def test_card_eta_falla_si_card_sin_size():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))
    area_a = AreaId.generate()
    cycle = _cycle(space_id, {area_a: Minutes(600)})
    await cycle_repo.save(cycle)

    card = _card_view(
        space_id,
        size=None,
        area_id=area_a,
        actual_minutes=0,
    )
    card_reader.add(card)

    uc = GetCardEta(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    with pytest.raises(InvalidCardForEtaError):
        await uc.execute(
            GetCardEtaQuery(card_id=card.id, reference_date=date(2026, 4, 10))
        )


@pytest.mark.asyncio
async def test_card_eta_falla_si_card_sin_area():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))
    area_a = AreaId.generate()
    cycle = _cycle(space_id, {area_a: Minutes(600)})
    await cycle_repo.save(cycle)

    card = _card_view(
        space_id,
        size=CardSize.M,
        area_id=None,
        actual_minutes=0,
    )
    card_reader.add(card)

    uc = GetCardEta(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    with pytest.raises(InvalidCardForEtaError):
        await uc.execute(
            GetCardEtaQuery(card_id=card.id, reference_date=date(2026, 4, 10))
        )


@pytest.mark.asyncio
async def test_card_eta_falla_si_area_sin_budget():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))
    area_a = AreaId.generate()
    cycle = _cycle(space_id, {})  # sin budgets
    await cycle_repo.save(cycle)

    card = _card_view(
        space_id,
        size=CardSize.M,
        area_id=area_a,
        actual_minutes=0,
    )
    card_reader.add(card)

    uc = GetCardEta(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    with pytest.raises(BudgetNotFoundError):
        await uc.execute(
            GetCardEtaQuery(card_id=card.id, reference_date=date(2026, 4, 10))
        )


@pytest.mark.asyncio
async def test_card_eta_falla_si_daily_capacity_es_cero():
    cycle_repo = FakeCycleRepository()
    card_reader = FakeCardReader()
    space_reader = FakeSpaceReader()

    space_id = SpaceId.generate()
    space_reader.add(_space_view(space_id=space_id))
    area_a = AreaId.generate()
    # Budget 4 → daily_capacity = 4 // 5 = 0
    cycle = _cycle(space_id, {area_a: Minutes(4)})
    await cycle_repo.save(cycle)

    card = _card_view(
        space_id,
        size=CardSize.M,
        area_id=area_a,
        actual_minutes=0,
    )
    card_reader.add(card)

    uc = GetCardEta(
        cycle_repo=cycle_repo, card_reader=card_reader, space_reader=space_reader
    )
    with pytest.raises(InvalidCardForEtaError):
        await uc.execute(
            GetCardEtaQuery(card_id=card.id, reference_date=date(2026, 4, 10))
        )
