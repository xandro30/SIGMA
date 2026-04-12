"""Integration tests del router /v1/spaces/{space_id}/day-templates."""
from datetime import date, datetime, timezone

import pytest

from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DayId,
    DayTemplateId,
    TimeOfDay,
)
from sigma_core.shared_kernel.value_objects import (
    AreaId,
    Minutes,
    SpaceId,
    Timestamp,
)


def _tpl_block(
    *, hour: int = 9, minute: int = 0, duration: int = 60
) -> DayTemplateBlock:
    return DayTemplateBlock(
        id=BlockId.generate(),
        start_at=TimeOfDay(hour=hour, minute=minute),
        duration=Minutes(duration),
        area_id=None,
        notes="",
    )


def _template(
    space_id: SpaceId,
    *,
    name: str = "Plantilla base",
    blocks: list[DayTemplateBlock] | None = None,
) -> DayTemplate:
    template = DayTemplate(
        id=DayTemplateId.generate(),
        space_id=space_id,
        name=name,
    )
    if blocks:
        template.replace_blocks(blocks)
    return template


class TestCreateDayTemplate:
    @pytest.mark.asyncio
    async def test_crea_template_vacio(self, client):
        space_id = SpaceId.generate()
        response = await client.post(
            f"/v1/spaces/{space_id.value}/day-templates",
            json={"name": "Rutina mañana", "blocks": []},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Rutina mañana"
        assert body["blocks"] == []

    @pytest.mark.asyncio
    async def test_crea_template_con_bloques(self, client):
        space_id = SpaceId.generate()
        response = await client.post(
            f"/v1/spaces/{space_id.value}/day-templates",
            json={
                "name": "Plantilla",
                "blocks": [
                    {
                        "start_at": {"hour": 9, "minute": 0},
                        "duration": 60,
                        "area_id": None,
                        "notes": "deep",
                    },
                    {
                        "start_at": {"hour": 11, "minute": 0},
                        "duration": 30,
                        "area_id": None,
                        "notes": "",
                    },
                ],
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert len(body["blocks"]) == 2
        assert body["blocks"][0]["start_at"] == {"hour": 9, "minute": 0}
        assert body["blocks"][0]["notes"] == "deep"

    @pytest.mark.asyncio
    async def test_crea_template_rechaza_solapamiento(self, client):
        space_id = SpaceId.generate()
        response = await client.post(
            f"/v1/spaces/{space_id.value}/day-templates",
            json={
                "name": "Choque",
                "blocks": [
                    {
                        "start_at": {"hour": 9, "minute": 0},
                        "duration": 60,
                        "area_id": None,
                        "notes": "",
                    },
                    {
                        "start_at": {"hour": 9, "minute": 30},
                        "duration": 30,
                        "area_id": None,
                        "notes": "",
                    },
                ],
            },
        )
        assert response.status_code == 409
        assert response.json()["error"] == "block_overlap"


class TestGetDayTemplate:
    @pytest.mark.asyncio
    async def test_get_by_id(self, client, day_template_repo):
        space_id = SpaceId.generate()
        template = _template(space_id, blocks=[_tpl_block()])
        await day_template_repo.save(template)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/day-templates/{template.id.value}"
        )
        assert response.status_code == 200
        assert response.json()["id"] == template.id.value

    @pytest.mark.asyncio
    async def test_get_by_id_404(self, client):
        space_id = SpaceId.generate()
        response = await client.get(
            f"/v1/spaces/{space_id.value}/day-templates/{DayTemplateId.generate().value}"
        )
        assert response.status_code == 404
        assert response.json()["error"] == "day_template_not_found"

    @pytest.mark.asyncio
    async def test_list_by_space(self, client, day_template_repo):
        space_id = SpaceId.generate()
        t1 = _template(space_id, name="Uno")
        t2 = _template(space_id, name="Dos")
        other = _template(SpaceId.generate(), name="Otro")
        for t in (t1, t2, other):
            await day_template_repo.save(t)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/day-templates"
        )
        assert response.status_code == 200
        ids = {t["id"] for t in response.json()["templates"]}
        assert ids == {t1.id.value, t2.id.value}


class TestUpdateDayTemplate:
    @pytest.mark.asyncio
    async def test_update_reemplaza_nombre_y_bloques(
        self, client, day_template_repo
    ):
        space_id = SpaceId.generate()
        template = _template(
            space_id,
            name="Viejo",
            blocks=[_tpl_block(hour=9)],
        )
        await day_template_repo.save(template)

        response = await client.put(
            f"/v1/spaces/{space_id.value}/day-templates/{template.id.value}",
            json={
                "name": "Nuevo",
                "blocks": [
                    {
                        "start_at": {"hour": 10, "minute": 30},
                        "duration": 45,
                        "area_id": None,
                        "notes": "reemplazo",
                    }
                ],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Nuevo"
        assert len(body["blocks"]) == 1
        assert body["blocks"][0]["start_at"] == {"hour": 10, "minute": 30}
        assert body["blocks"][0]["duration"] == 45

    @pytest.mark.asyncio
    async def test_update_404(self, client):
        space_id = SpaceId.generate()
        response = await client.put(
            f"/v1/spaces/{space_id.value}/day-templates/{DayTemplateId.generate().value}",
            json={"name": "X", "blocks": []},
        )
        assert response.status_code == 404


class TestDeleteDayTemplate:
    @pytest.mark.asyncio
    async def test_delete(self, client, day_template_repo):
        space_id = SpaceId.generate()
        template = _template(space_id)
        await day_template_repo.save(template)

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/day-templates/{template.id.value}"
        )
        assert response.status_code == 204
        assert await day_template_repo.get_by_id(template.id) is None

    @pytest.mark.asyncio
    async def test_delete_404(self, client):
        space_id = SpaceId.generate()
        response = await client.delete(
            f"/v1/spaces/{space_id.value}/day-templates/{DayTemplateId.generate().value}"
        )
        assert response.status_code == 404


class TestApplyDayTemplate:
    @pytest.mark.asyncio
    async def test_apply_crea_day_nuevo(
        self, client, day_template_repo, day_repo
    ):
        space_id = SpaceId.generate()
        template = _template(
            space_id,
            blocks=[
                _tpl_block(hour=9, duration=60),
                _tpl_block(hour=11, duration=30),
            ],
        )
        await day_template_repo.save(template)

        response = await client.post(
            f"/v1/spaces/{space_id.value}/day-templates/{template.id.value}/apply",
            json={
                "target_date": "2026-04-10",
                "replace_existing": False,
            },
        )
        assert response.status_code == 200
        day_id = response.json()["day_id"]

        day = await day_repo.get_by_id(DayId(day_id))
        assert day is not None
        assert len(day.blocks) == 2

    @pytest.mark.asyncio
    async def test_apply_rechaza_day_no_vacio_sin_replace(
        self, client, day_template_repo, day_repo
    ):
        space_id = SpaceId.generate()
        template = _template(
            space_id, blocks=[_tpl_block(hour=9, duration=60)]
        )
        await day_template_repo.save(template)

        existing_day = Day(
            id=DayId.for_space_and_date(space_id, date(2026, 4, 10)),
            space_id=space_id,
            date=date(2026, 4, 10),
        )
        existing_day.add_block(
            TimeBlock(
                id=BlockId.generate(),
                start_at=Timestamp(
                    datetime(2026, 4, 10, 14, 0, tzinfo=timezone.utc)
                ),
                duration=Minutes(60),
                area_id=None,
                notes="existente",
            )
        )
        await day_repo.save(existing_day)

        response = await client.post(
            f"/v1/spaces/{space_id.value}/day-templates/{template.id.value}/apply",
            json={
                "target_date": "2026-04-10",
                "replace_existing": False,
            },
        )
        assert response.status_code == 409
        assert response.json()["error"] == "day_not_empty"

    @pytest.mark.asyncio
    async def test_apply_replace_existing(
        self, client, day_template_repo, day_repo
    ):
        space_id = SpaceId.generate()
        template = _template(
            space_id,
            blocks=[_tpl_block(hour=9, duration=60)],
        )
        await day_template_repo.save(template)

        existing_day = Day(
            id=DayId.for_space_and_date(space_id, date(2026, 4, 10)),
            space_id=space_id,
            date=date(2026, 4, 10),
        )
        existing_day.add_block(
            TimeBlock(
                id=BlockId.generate(),
                start_at=Timestamp(
                    datetime(2026, 4, 10, 14, 0, tzinfo=timezone.utc)
                ),
                duration=Minutes(60),
                area_id=None,
                notes="existente",
            )
        )
        await day_repo.save(existing_day)

        response = await client.post(
            f"/v1/spaces/{space_id.value}/day-templates/{template.id.value}/apply",
            json={
                "target_date": "2026-04-10",
                "replace_existing": True,
            },
        )
        assert response.status_code == 200
        day = await day_repo.get_by_id(existing_day.id)
        assert day is not None
        assert len(day.blocks) == 1
        assert day.blocks[0].notes == ""

    @pytest.mark.asyncio
    async def test_apply_template_not_found(self, client):
        space_id = SpaceId.generate()
        response = await client.post(
            f"/v1/spaces/{space_id.value}/day-templates/{DayTemplateId.generate().value}/apply",
            json={
                "target_date": "2026-04-10",
                "replace_existing": False,
            },
        )
        assert response.status_code == 404
        assert response.json()["error"] == "day_template_not_found"
