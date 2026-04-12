"""Integration tests de las planning queries (capacity + ETA)."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleState
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import (
    FINISH_STATE_ID,
    Space,
)
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.shared_kernel.value_objects import (
    AreaId,
    CardId,
    Minutes,
    SizeMapping,
    SpaceId,
    Timestamp,
)
from sigma_core.task_management.domain.value_objects import (
    CardTitle,
    SpaceName,
    WorkflowStateId,
)


_MADRID_TZ = ZoneInfo("Europe/Madrid")


def _default_size_mapping() -> SizeMapping:
    return SizeMapping(
        entries={
            CardSize.XXS: Minutes(15),
            CardSize.XS: Minutes(30),
            CardSize.S: Minutes(60),
            CardSize.M: Minutes(120),
            CardSize.L: Minutes(240),
            CardSize.XL: Minutes(480),
            CardSize.XXL: Minutes(960),
        }
    )


def _space_with_mapping(space_id: SpaceId) -> Space:
    return Space(
        id=space_id,
        name=SpaceName("Test space"),
        size_mapping=_default_size_mapping(),
    )


def _active_cycle(
    space_id: SpaceId,
    *,
    area_budgets: dict[AreaId, Minutes] | None = None,
    buffer_percentage: int = 10,
) -> Cycle:
    return Cycle(
        id=CycleId.generate(),
        space_id=space_id,
        name="Ciclo test",
        date_range=DateRange(
            start=date(2026, 4, 1), end=date(2026, 4, 30)
        ),
        state=CycleState.ACTIVE,
        area_budgets=area_budgets or {},
        buffer_percentage=buffer_percentage,
    )


def _completed_card(
    space_id: SpaceId,
    *,
    area_id: AreaId,
    size: CardSize = CardSize.S,
    completed_on: date = date(2026, 4, 10),
) -> Card:
    return Card(
        id=CardId.generate(),
        space_id=space_id,
        title=CardTitle("Done card"),
        pre_workflow_stage=None,
        workflow_state_id=FINISH_STATE_ID,
        area_id=area_id,
        size=size,
        completed_at=Timestamp(
            datetime(
                completed_on.year,
                completed_on.month,
                completed_on.day,
                12,
                0,
                tzinfo=_MADRID_TZ,
            )
        ),
    )


def _pending_card(
    space_id: SpaceId,
    *,
    area_id: AreaId,
    size: CardSize = CardSize.M,
) -> Card:
    return Card(
        id=CardId.generate(),
        space_id=space_id,
        title=CardTitle("Pending card"),
        pre_workflow_stage=None,
        workflow_state_id=WorkflowStateId.generate(),
        area_id=area_id,
        size=size,
    )


class TestSpaceCapacity:
    @pytest.mark.asyncio
    async def test_capacity_sin_cycle_activo_404(self, client):
        space_id = SpaceId.generate()
        response = await client.get(f"/v1/spaces/{space_id.value}/capacity")
        assert response.status_code == 404
        assert response.json()["error"] == "cycle_not_found"

    @pytest.mark.asyncio
    async def test_capacity_basica(
        self, client, cycle_repo, card_repo, space_repo
    ):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        cycle = _active_cycle(
            space_id,
            area_budgets={area_id: Minutes(600)},
            buffer_percentage=10,
        )
        await cycle_repo.save(cycle)
        await space_repo.save(_space_with_mapping(space_id))
        # Card completada (size S → 60 min)
        await card_repo.save(
            _completed_card(space_id, area_id=area_id, size=CardSize.S)
        )

        response = await client.get(f"/v1/spaces/{space_id.value}/capacity")
        assert response.status_code == 200
        body = response.json()
        assert body["cycle_id"] == cycle.id.value
        assert body["buffer_percentage"] == 10
        assert len(body["areas"]) == 1
        area_result = body["areas"][0]
        assert area_result["area_id"] == area_id.value
        assert area_result["budget_minutes"] == 600
        assert area_result["consumed_minutes"] == 60
        # effective_budget = 600 * 90 // 100 = 540 → remaining = 540 - 60 = 480
        assert area_result["remaining_minutes"] == 480

    @pytest.mark.asyncio
    async def test_capacity_ignora_cards_no_completadas(
        self, client, cycle_repo, card_repo, space_repo
    ):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        cycle = _active_cycle(
            space_id, area_budgets={area_id: Minutes(600)}
        )
        await cycle_repo.save(cycle)
        await space_repo.save(_space_with_mapping(space_id))
        await card_repo.save(
            _pending_card(space_id, area_id=area_id, size=CardSize.M)
        )

        response = await client.get(f"/v1/spaces/{space_id.value}/capacity")
        assert response.status_code == 200
        assert response.json()["areas"][0]["consumed_minutes"] == 0


class TestCardEta:
    @pytest.mark.asyncio
    async def test_eta_feliz(
        self, client, cycle_repo, card_repo, space_repo
    ):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        await space_repo.save(_space_with_mapping(space_id))
        # budget 1500 min/sem → 300 min/día
        await cycle_repo.save(
            _active_cycle(
                space_id,
                area_budgets={area_id: Minutes(1500)},
                buffer_percentage=20,
            )
        )
        # size M → 120 min → raw_days = ceil(120/300) = 1
        card = Card(
            id=CardId.generate(),
            space_id=space_id,
            title=CardTitle("ETA card"),
            pre_workflow_stage=PreWorkflowStage.INBOX,
            workflow_state_id=None,
            area_id=area_id,
            size=CardSize.M,
        )
        await card_repo.save(card)

        response = await client.get(
            f"/v1/cards/{card.id.value}/eta",
            params={"reference_date": "2026-04-10"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["card_id"] == card.id.value
        assert body["estimated_minutes"] == 120
        assert body["daily_capacity_minutes"] == 300
        # raw_days = 1 → lunes siguiente (13 abril)
        assert body["raw_completion_date"] == "2026-04-13"
        # buffered_days = ceil(1 * 1.20) = 2 → martes 14 abril
        assert body["buffered_completion_date"] == "2026-04-14"

    @pytest.mark.asyncio
    async def test_eta_card_not_found(self, client):
        response = await client.get(
            f"/v1/cards/{CardId.generate().value}/eta",
            params={"reference_date": "2026-04-10"},
        )
        assert response.status_code == 404
        assert response.json()["error"] == "card_not_found"

    @pytest.mark.asyncio
    async def test_eta_card_sin_size_422(
        self, client, cycle_repo, card_repo, space_repo
    ):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        await space_repo.save(_space_with_mapping(space_id))
        await cycle_repo.save(
            _active_cycle(
                space_id, area_budgets={area_id: Minutes(1500)}
            )
        )
        card = Card(
            id=CardId.generate(),
            space_id=space_id,
            title=CardTitle("Sin size"),
            pre_workflow_stage=PreWorkflowStage.INBOX,
            workflow_state_id=None,
            area_id=area_id,
            size=None,
        )
        await card_repo.save(card)

        response = await client.get(
            f"/v1/cards/{card.id.value}/eta",
            params={"reference_date": "2026-04-10"},
        )
        assert response.status_code == 422
        assert response.json()["error"] == "invalid_card_for_eta"

    @pytest.mark.asyncio
    async def test_eta_sin_cycle_activo_404(
        self, client, card_repo, space_repo
    ):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        await space_repo.save(_space_with_mapping(space_id))
        card = Card(
            id=CardId.generate(),
            space_id=space_id,
            title=CardTitle("Sin cycle"),
            pre_workflow_stage=PreWorkflowStage.INBOX,
            workflow_state_id=None,
            area_id=area_id,
            size=CardSize.M,
        )
        await card_repo.save(card)

        response = await client.get(
            f"/v1/cards/{card.id.value}/eta",
            params={"reference_date": "2026-04-10"},
        )
        assert response.status_code == 404
        assert response.json()["error"] == "cycle_not_found"

    @pytest.mark.asyncio
    async def test_eta_sin_budget_para_area_422(
        self, client, cycle_repo, card_repo, space_repo
    ):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        other_area = AreaId.generate()
        await space_repo.save(_space_with_mapping(space_id))
        await cycle_repo.save(
            _active_cycle(
                space_id, area_budgets={other_area: Minutes(1500)}
            )
        )
        card = Card(
            id=CardId.generate(),
            space_id=space_id,
            title=CardTitle("Sin budget"),
            pre_workflow_stage=PreWorkflowStage.INBOX,
            workflow_state_id=None,
            area_id=area_id,
            size=CardSize.M,
        )
        await card_repo.save(card)

        response = await client.get(
            f"/v1/cards/{card.id.value}/eta",
            params={"reference_date": "2026-04-10"},
        )
        assert response.status_code == 422
        assert response.json()["error"] == "budget_not_found"
