"""Integration tests del router /v1/spaces/{space_id}/cycles."""
from datetime import date

import pytest

from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleState
from sigma_core.planning.domain.value_objects import CycleId, DateRange
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


class TestCreateCycle:
    @pytest.mark.asyncio
    async def test_crea_cycle_en_draft(self, client):
        space_id = SpaceId.generate().value
        response = await client.post(
            f"/v1/spaces/{space_id}/cycles",
            json={
                "name": "Abril",
                "date_range": {"start": "2026-04-01", "end": "2026-04-30"},
                "buffer_percentage": 20,
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["space_id"] == space_id
        assert body["state"] == "draft"
        assert body["buffer_percentage"] == 20
        assert body["name"] == "Abril"

    @pytest.mark.asyncio
    async def test_valida_buffer_percentage(self, client):
        space_id = SpaceId.generate().value
        response = await client.post(
            f"/v1/spaces/{space_id}/cycles",
            json={
                "name": "Abril",
                "date_range": {"start": "2026-04-01", "end": "2026-04-30"},
                "buffer_percentage": 150,
            },
        )
        assert response.status_code == 422


class TestGetCycle:
    @pytest.mark.asyncio
    async def test_get_cycle_existente(self, client, cycle_repo):
        space_id = SpaceId.generate()
        cycle = _cycle(space_id)
        await cycle_repo.save(cycle)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/cycles/{cycle.id.value}"
        )
        assert response.status_code == 200
        assert response.json()["id"] == cycle.id.value

    @pytest.mark.asyncio
    async def test_get_cycle_no_encontrado_404(self, client):
        space_id = SpaceId.generate().value
        response = await client.get(
            f"/v1/spaces/{space_id}/cycles/{CycleId.generate().value}"
        )
        assert response.status_code == 404
        assert response.json()["error"] == "cycle_not_found"

    @pytest.mark.asyncio
    async def test_get_active_por_space(self, client, cycle_repo):
        space_id = SpaceId.generate()
        draft = _cycle(space_id, state=CycleState.DRAFT, name="D")
        active = _cycle(space_id, state=CycleState.ACTIVE, name="A")
        await cycle_repo.save(draft)
        await cycle_repo.save(active)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/cycles/active"
        )
        assert response.status_code == 200
        assert response.json()["id"] == active.id.value

    @pytest.mark.asyncio
    async def test_get_active_sin_activo_404(self, client):
        space_id = SpaceId.generate().value
        response = await client.get(f"/v1/spaces/{space_id}/cycles/active")
        assert response.status_code == 404


class TestActivateAndClose:
    @pytest.mark.asyncio
    async def test_activa_cycle_en_draft(self, client, cycle_repo):
        space_id = SpaceId.generate()
        cycle = _cycle(space_id)
        await cycle_repo.save(cycle)

        response = await client.post(
            f"/v1/spaces/{space_id.value}/cycles/{cycle.id.value}/activate"
        )
        assert response.status_code == 200
        assert response.json()["state"] == "active"

    @pytest.mark.asyncio
    async def test_activa_falla_si_ya_existe_otro_activo(
        self, client, cycle_repo
    ):
        space_id = SpaceId.generate()
        existing = _cycle(space_id, state=CycleState.ACTIVE, name="Existing")
        new = _cycle(space_id, state=CycleState.DRAFT, name="New")
        await cycle_repo.save(existing)
        await cycle_repo.save(new)

        response = await client.post(
            f"/v1/spaces/{space_id.value}/cycles/{new.id.value}/activate"
        )
        assert response.status_code == 409
        assert response.json()["error"] == "cycle_already_active"

    @pytest.mark.asyncio
    async def test_close_cycle_activo(self, client, cycle_repo):
        space_id = SpaceId.generate()
        cycle = _cycle(space_id, state=CycleState.ACTIVE)
        await cycle_repo.save(cycle)

        response = await client.post(
            f"/v1/spaces/{space_id.value}/cycles/{cycle.id.value}/close"
        )
        assert response.status_code == 200
        assert response.json()["state"] == "closed"


class TestBudgets:
    @pytest.mark.asyncio
    async def test_set_area_budget(self, client, cycle_repo):
        space_id = SpaceId.generate()
        cycle = _cycle(space_id)
        await cycle_repo.save(cycle)
        area_id = AreaId.generate()

        response = await client.put(
            f"/v1/spaces/{space_id.value}/cycles/{cycle.id.value}/budgets",
            json={"area_id": area_id.value, "minutes": 600},
        )
        assert response.status_code == 200
        body = response.json()
        assert {
            b["area_id"]: b["minutes"] for b in body["area_budgets"]
        } == {area_id.value: 600}

    @pytest.mark.asyncio
    async def test_remove_area_budget(self, client, cycle_repo):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        cycle = _cycle(space_id, area_budgets={area_id: Minutes(600)})
        await cycle_repo.save(cycle)

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/cycles/{cycle.id.value}/budgets/{area_id.value}"
        )
        assert response.status_code == 200
        assert response.json()["area_budgets"] == []

    @pytest.mark.asyncio
    async def test_remove_area_budget_sin_presupuesto_422(
        self, client, cycle_repo
    ):
        space_id = SpaceId.generate()
        cycle = _cycle(space_id)
        await cycle_repo.save(cycle)

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/cycles/{cycle.id.value}/budgets/{AreaId.generate().value}"
        )
        assert response.status_code == 422
        assert response.json()["error"] == "budget_not_found"


class TestBufferAndDelete:
    @pytest.mark.asyncio
    async def test_set_buffer_percentage(self, client, cycle_repo):
        space_id = SpaceId.generate()
        cycle = _cycle(space_id)
        await cycle_repo.save(cycle)

        response = await client.patch(
            f"/v1/spaces/{space_id.value}/cycles/{cycle.id.value}/buffer",
            json={"buffer_percentage": 35},
        )
        assert response.status_code == 200
        assert response.json()["buffer_percentage"] == 35

    @pytest.mark.asyncio
    async def test_delete_cycle_en_draft(self, client, cycle_repo):
        space_id = SpaceId.generate()
        cycle = _cycle(space_id)
        await cycle_repo.save(cycle)

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/cycles/{cycle.id.value}"
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_cycle_activo_falla(self, client, cycle_repo):
        space_id = SpaceId.generate()
        cycle = _cycle(space_id, state=CycleState.ACTIVE)
        await cycle_repo.save(cycle)

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/cycles/{cycle.id.value}"
        )
        assert response.status_code == 422
        assert response.json()["error"] == "invalid_cycle_transition"
