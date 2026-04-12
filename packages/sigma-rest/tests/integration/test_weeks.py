"""Integration tests del router /v1/spaces/{space_id}/weeks."""
from datetime import date

import pytest

from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.enums import DayOfWeek
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DayId,
    DayTemplateId,
    TimeOfDay,
    WeekTemplateId,
)
from sigma_core.shared_kernel.value_objects import Minutes, SpaceId


MONDAY = date(2026, 4, 13)
WEDNESDAY = date(2026, 4, 15)


def _day_template(
    space_id: SpaceId,
    *,
    hour: int = 9,
    duration: int = 60,
) -> DayTemplate:
    return DayTemplate(
        id=DayTemplateId.generate(),
        space_id=space_id,
        name="DT",
        blocks=[
            DayTemplateBlock(
                id=BlockId.generate(),
                start_at=TimeOfDay(hour=hour, minute=0),
                duration=Minutes(duration),
                area_id=None,
                notes="",
            )
        ],
    )


def _week_template_with_mon_and_wed(
    space_id: SpaceId,
    mon_id: DayTemplateId,
    wed_id: DayTemplateId,
) -> WeekTemplate:
    wt = WeekTemplate(
        id=WeekTemplateId.generate(),
        space_id=space_id,
        name="WT",
    )
    wt.slots[DayOfWeek.MONDAY] = mon_id
    wt.slots[DayOfWeek.WEDNESDAY] = wed_id
    return wt


class TestCreateWeek:
    @pytest.mark.asyncio
    async def test_crea_week_devuelve_201(self, client):
        space_id = SpaceId.generate()
        response = await client.post(
            f"/v1/spaces/{space_id.value}/weeks",
            json={"week_start": MONDAY.isoformat()},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["space_id"] == space_id.value
        assert body["week_start"] == MONDAY.isoformat()
        assert body["notes"] == ""
        assert body["applied_template_id"] is None

    @pytest.mark.asyncio
    async def test_crea_week_idempotente(self, client):
        space_id = SpaceId.generate()
        first = await client.post(
            f"/v1/spaces/{space_id.value}/weeks",
            json={"week_start": MONDAY.isoformat()},
        )
        second = await client.post(
            f"/v1/spaces/{space_id.value}/weeks",
            json={"week_start": MONDAY.isoformat()},
        )
        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json()["id"] == second.json()["id"]

    @pytest.mark.asyncio
    async def test_crea_week_rechaza_no_lunes(self, client):
        space_id = SpaceId.generate()
        response = await client.post(
            f"/v1/spaces/{space_id.value}/weeks",
            json={"week_start": WEDNESDAY.isoformat()},
        )
        assert response.status_code == 422
        assert response.json()["error"] == "invalid_week_start"


class TestGetWeek:
    @pytest.mark.asyncio
    async def test_get_devuelve_week_existente(self, client):
        space_id = SpaceId.generate()
        await client.post(
            f"/v1/spaces/{space_id.value}/weeks",
            json={"week_start": MONDAY.isoformat()},
        )
        response = await client.get(
            f"/v1/spaces/{space_id.value}/weeks/{MONDAY.isoformat()}"
        )
        assert response.status_code == 200
        assert response.json()["week_start"] == MONDAY.isoformat()

    @pytest.mark.asyncio
    async def test_get_404_si_no_existe(self, client):
        space_id = SpaceId.generate()
        response = await client.get(
            f"/v1/spaces/{space_id.value}/weeks/{MONDAY.isoformat()}"
        )
        assert response.status_code == 404
        assert response.json()["error"] == "week_not_found"


class TestSetWeekNotes:
    @pytest.mark.asyncio
    async def test_actualiza_notas(self, client):
        space_id = SpaceId.generate()
        await client.post(
            f"/v1/spaces/{space_id.value}/weeks",
            json={"week_start": MONDAY.isoformat()},
        )
        response = await client.put(
            f"/v1/spaces/{space_id.value}/weeks/{MONDAY.isoformat()}/notes",
            json={"notes": "Mucho foco"},
        )
        assert response.status_code == 200
        assert response.json()["notes"] == "Mucho foco"

    @pytest.mark.asyncio
    async def test_set_notes_404_si_week_no_existe(self, client):
        space_id = SpaceId.generate()
        response = await client.put(
            f"/v1/spaces/{space_id.value}/weeks/{MONDAY.isoformat()}/notes",
            json={"notes": "x"},
        )
        assert response.status_code == 404
        assert response.json()["error"] == "week_not_found"


class TestApplyTemplateToWeek:
    @pytest.mark.asyncio
    async def test_materializa_slots_y_marca_week(
        self, client, day_template_repo, week_template_repo, day_repo
    ):
        space_id = SpaceId.generate()
        dt_mon = _day_template(space_id, hour=9)
        dt_wed = _day_template(space_id, hour=14)
        await day_template_repo.save(dt_mon)
        await day_template_repo.save(dt_wed)
        wt = _week_template_with_mon_and_wed(space_id, dt_mon.id, dt_wed.id)
        await week_template_repo.save(wt)

        await client.post(
            f"/v1/spaces/{space_id.value}/weeks",
            json={"week_start": MONDAY.isoformat()},
        )

        response = await client.post(
            f"/v1/spaces/{space_id.value}/weeks/{MONDAY.isoformat()}/apply-template",
            json={"template_id": wt.id.value, "replace_existing": False},
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["day_ids"]) == 2
        assert body["week"]["applied_template_id"] == wt.id.value

        # Los 2 days están realmente materializados
        mon_day = await day_repo.get_by_id(
            DayId.for_space_and_date(space_id, MONDAY)
        )
        assert mon_day is not None
        assert len(mon_day.blocks) == 1

    @pytest.mark.asyncio
    async def test_apply_rechaza_template_cross_space(
        self, client, day_template_repo, week_template_repo
    ):
        space_a = SpaceId.generate()
        space_b = SpaceId.generate()
        dt_mon = _day_template(space_b, hour=9)
        dt_wed = _day_template(space_b, hour=14)
        await day_template_repo.save(dt_mon)
        await day_template_repo.save(dt_wed)
        wt = _week_template_with_mon_and_wed(space_b, dt_mon.id, dt_wed.id)
        await week_template_repo.save(wt)

        await client.post(
            f"/v1/spaces/{space_a.value}/weeks",
            json={"week_start": MONDAY.isoformat()},
        )

        response = await client.post(
            f"/v1/spaces/{space_a.value}/weeks/{MONDAY.isoformat()}/apply-template",
            json={"template_id": wt.id.value},
        )
        assert response.status_code == 422
        assert response.json()["error"] == "cross_space_reference"

    @pytest.mark.asyncio
    async def test_apply_404_si_week_no_existe(self, client):
        space_id = SpaceId.generate()
        response = await client.post(
            f"/v1/spaces/{space_id.value}/weeks/{MONDAY.isoformat()}/apply-template",
            json={"template_id": WeekTemplateId.generate().value},
        )
        assert response.status_code == 404
        assert response.json()["error"] == "week_not_found"


class TestDeleteWeek:
    @pytest.mark.asyncio
    async def test_delete_cascada_borra_days_materializados(
        self, client, day_template_repo, week_template_repo, day_repo
    ):
        space_id = SpaceId.generate()
        dt_mon = _day_template(space_id, hour=9)
        dt_wed = _day_template(space_id, hour=14)
        await day_template_repo.save(dt_mon)
        await day_template_repo.save(dt_wed)
        wt = _week_template_with_mon_and_wed(space_id, dt_mon.id, dt_wed.id)
        await week_template_repo.save(wt)

        await client.post(
            f"/v1/spaces/{space_id.value}/weeks",
            json={"week_start": MONDAY.isoformat()},
        )
        await client.post(
            f"/v1/spaces/{space_id.value}/weeks/{MONDAY.isoformat()}/apply-template",
            json={"template_id": wt.id.value},
        )

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/weeks/{MONDAY.isoformat()}"
        )
        assert response.status_code == 204

        # Week borrada
        get_resp = await client.get(
            f"/v1/spaces/{space_id.value}/weeks/{MONDAY.isoformat()}"
        )
        assert get_resp.status_code == 404
        # Y los days de la semana en cascada
        assert (
            await day_repo.get_by_id(
                DayId.for_space_and_date(space_id, MONDAY)
            )
            is None
        )
        assert (
            await day_repo.get_by_id(
                DayId.for_space_and_date(space_id, WEDNESDAY)
            )
            is None
        )

    @pytest.mark.asyncio
    async def test_delete_404_si_week_no_existe(self, client):
        space_id = SpaceId.generate()
        response = await client.delete(
            f"/v1/spaces/{space_id.value}/weeks/{MONDAY.isoformat()}"
        )
        assert response.status_code == 404
        assert response.json()["error"] == "week_not_found"
