"""Integration tests del router /v1/spaces/{space_id}/metrics."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleState
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import (
    FINISH_STATE_ID,
    Space,
)
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.task_management.domain.value_objects import (
    CardTitle,
    SpaceName,
    WorkflowStateId,
    ProjectId,
    EpicId,
)


MADRID = ZoneInfo("Europe/Madrid")
CYCLE_START = date(2026, 4, 1)
CYCLE_END = date(2026, 4, 30)


def _ts(day: int = 10, hour: int = 12) -> Timestamp:
    return Timestamp(datetime(2026, 4, day, hour, 0, tzinfo=MADRID))


def _space(space_id: SpaceId) -> Space:
    from sigma_core.shared_kernel.value_objects import SizeMapping

    return Space(
        id=space_id,
        name=SpaceName("Test"),
        size_mapping=SizeMapping(
            entries={
                CardSize.XXS: Minutes(15),
                CardSize.XS: Minutes(30),
                CardSize.S: Minutes(60),
                CardSize.M: Minutes(120),
                CardSize.L: Minutes(240),
                CardSize.XL: Minutes(480),
                CardSize.XXL: Minutes(960),
            }
        ),
    )


def _active_cycle(space_id: SpaceId, area_id: AreaId) -> Cycle:
    return Cycle(
        id=CycleId.generate(),
        space_id=space_id,
        name="Q2",
        date_range=DateRange(start=CYCLE_START, end=CYCLE_END),
        state=CycleState.ACTIVE,
        area_budgets={area_id: Minutes(600)},
    )


def _completed_card(
    space_id: SpaceId,
    *,
    area_id: AreaId | None = None,
    project_id: ProjectId | None = None,
    epic_id: EpicId | None = None,
    size: CardSize = CardSize.M,
    actual_time: int = 90,
) -> Card:
    """Card completada dentro del rango del ciclo."""
    card = Card(
        id=CardId.generate(),
        space_id=space_id,
        title=CardTitle("Done"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
        area_id=area_id,
        project_id=project_id,
        epic_id=epic_id,
        size=size,
    )
    # Promover al workflow (setea entered_workflow_at)
    card.move_to_workflow_state(WorkflowStateId.generate())
    # Mover a FINISH (setea completed_at)
    card.move_to_workflow_state(FINISH_STATE_ID)
    # Forzar actual_time
    object.__setattr__(card, "actual_time", Minutes(actual_time))
    return card


from sigma_core.shared_kernel.value_objects import CardId


class TestGetMetricsOnDemand:
    @pytest.mark.asyncio
    async def test_calcula_on_demand_para_ciclo_activo(
        self, client, cycle_repo, card_repo, space_repo
    ):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        await space_repo.save(_space(space_id))
        cycle = _active_cycle(space_id, area_id)
        await cycle_repo.save(cycle)
        card = _completed_card(space_id, area_id=area_id)
        await card_repo.save(card)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/metrics"
        )
        assert response.status_code == 200
        body = response.json()
        assert body["source"] == "on_demand"
        assert body["global_metrics"]["total_cards_completed"] == 1
        assert body["global_metrics"]["avg_cycle_time_minutes"] is not None
        assert body["global_metrics"]["avg_lead_time_minutes"] is not None
        assert area_id.value in body["areas"]
        assert body["areas"][area_id.value]["budget_minutes"] == 600

    @pytest.mark.asyncio
    async def test_calcula_con_jerarquia_area_project_epic(
        self, client, cycle_repo, card_repo, space_repo
    ):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        project_id = ProjectId.generate()
        epic_id = EpicId.generate()
        await space_repo.save(_space(space_id))
        cycle = _active_cycle(space_id, area_id)
        await cycle_repo.save(cycle)

        card = _completed_card(
            space_id,
            area_id=area_id,
            project_id=project_id,
            epic_id=epic_id,
            size=CardSize.S,
            actual_time=45,
        )
        await card_repo.save(card)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/metrics"
        )
        assert response.status_code == 200
        body = response.json()

        area = body["areas"][area_id.value]
        assert area["metrics"]["total_cards_completed"] == 1
        assert project_id.value in area["projects"]
        project = area["projects"][project_id.value]
        assert project["metrics"]["total_cards_completed"] == 1
        assert epic_id.value in project["epics"]
        assert project["epics"][epic_id.value]["total_cards_completed"] == 1

    @pytest.mark.asyncio
    async def test_404_sin_ciclo_activo(self, client):
        space_id = SpaceId.generate()
        response = await client.get(
            f"/v1/spaces/{space_id.value}/metrics"
        )
        assert response.status_code == 404
        assert response.json()["error"] == "metrics_cycle_not_found"


class TestGetMetricsWithCycleId:
    @pytest.mark.asyncio
    async def test_calcula_on_demand_por_cycle_id_activo(
        self, client, cycle_repo, space_repo
    ):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        await space_repo.save(_space(space_id))
        cycle = _active_cycle(space_id, area_id)
        await cycle_repo.save(cycle)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/metrics",
            params={"cycle_id": cycle.id.value},
        )
        assert response.status_code == 200
        assert response.json()["source"] == "on_demand"
        assert response.json()["cycle_id"] == cycle.id.value

    @pytest.mark.asyncio
    async def test_404_cycle_id_inexistente(self, client):
        space_id = SpaceId.generate()
        response = await client.get(
            f"/v1/spaces/{space_id.value}/metrics",
            params={"cycle_id": CycleId.generate().value},
        )
        assert response.status_code == 404
