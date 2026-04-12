"""Integration tests del router /v1/spaces/{space_id}/week-templates."""
import pytest

from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.enums import DayOfWeek
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DayTemplateId,
    TimeOfDay,
    WeekTemplateId,
)
from sigma_core.shared_kernel.value_objects import Minutes, SpaceId


def _day_template(space_id: SpaceId, *, name: str = "Plan") -> DayTemplate:
    template = DayTemplate(
        id=DayTemplateId.generate(),
        space_id=space_id,
        name=name,
    )
    template.replace_blocks(
        [
            DayTemplateBlock(
                id=BlockId.generate(),
                start_at=TimeOfDay(hour=9, minute=0),
                duration=Minutes(60),
                area_id=None,
                notes="",
            )
        ]
    )
    return template


def _week_template(space_id: SpaceId, *, name: str = "Semana") -> WeekTemplate:
    return WeekTemplate(
        id=WeekTemplateId.generate(),
        space_id=space_id,
        name=name,
    )


class TestCreateWeekTemplate:
    @pytest.mark.asyncio
    async def test_crea_week_template(self, client):
        space_id = SpaceId.generate()
        response = await client.post(
            f"/v1/spaces/{space_id.value}/week-templates",
            json={"name": "Mi semana"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Mi semana"
        assert set(body["slots"].keys()) == {
            "mon", "tue", "wed", "thu", "fri", "sat", "sun"
        }
        assert all(v is None for v in body["slots"].values())


class TestGetWeekTemplate:
    @pytest.mark.asyncio
    async def test_get_by_id(self, client, week_template_repo):
        space_id = SpaceId.generate()
        template = _week_template(space_id)
        await week_template_repo.save(template)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/week-templates/{template.id.value}"
        )
        assert response.status_code == 200
        assert response.json()["id"] == template.id.value

    @pytest.mark.asyncio
    async def test_get_by_id_404(self, client):
        space_id = SpaceId.generate()
        response = await client.get(
            f"/v1/spaces/{space_id.value}/week-templates/{WeekTemplateId.generate().value}"
        )
        assert response.status_code == 404
        assert response.json()["error"] == "week_template_not_found"

    @pytest.mark.asyncio
    async def test_list_by_space(self, client, week_template_repo):
        space_id = SpaceId.generate()
        t1 = _week_template(space_id, name="Uno")
        t2 = _week_template(space_id, name="Dos")
        other = _week_template(SpaceId.generate(), name="Otro")
        for t in (t1, t2, other):
            await week_template_repo.save(t)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/week-templates"
        )
        assert response.status_code == 200
        ids = {t["id"] for t in response.json()["templates"]}
        assert ids == {t1.id.value, t2.id.value}


class TestSlots:
    @pytest.mark.asyncio
    async def test_set_slot(
        self, client, week_template_repo, day_template_repo
    ):
        space_id = SpaceId.generate()
        day_tpl = _day_template(space_id)
        await day_template_repo.save(day_tpl)
        week = _week_template(space_id)
        await week_template_repo.save(week)

        response = await client.put(
            f"/v1/spaces/{space_id.value}/week-templates/{week.id.value}/slots/mon",
            json={"day_template_id": day_tpl.id.value},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["slots"]["mon"] == day_tpl.id.value
        assert body["slots"]["tue"] is None

    @pytest.mark.asyncio
    async def test_set_slot_day_template_not_found(
        self, client, week_template_repo
    ):
        space_id = SpaceId.generate()
        week = _week_template(space_id)
        await week_template_repo.save(week)

        response = await client.put(
            f"/v1/spaces/{space_id.value}/week-templates/{week.id.value}/slots/mon",
            json={"day_template_id": DayTemplateId.generate().value},
        )
        assert response.status_code == 404
        assert response.json()["error"] == "day_template_not_found"

    @pytest.mark.asyncio
    async def test_clear_slot(
        self, client, week_template_repo, day_template_repo
    ):
        space_id = SpaceId.generate()
        day_tpl = _day_template(space_id)
        await day_template_repo.save(day_tpl)
        week = _week_template(space_id)
        week.set_slot(DayOfWeek.TUESDAY, day_tpl.id)
        await week_template_repo.save(week)

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/week-templates/{week.id.value}/slots/tue"
        )
        assert response.status_code == 200
        assert response.json()["slots"]["tue"] is None

    @pytest.mark.asyncio
    async def test_weekday_invalido(self, client, week_template_repo):
        space_id = SpaceId.generate()
        week = _week_template(space_id)
        await week_template_repo.save(week)

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/week-templates/{week.id.value}/slots/funday"
        )
        assert response.status_code == 422
        assert response.json()["detail"]["error"] == "invalid_weekday"


class TestDeleteWeekTemplate:
    @pytest.mark.asyncio
    async def test_delete(self, client, week_template_repo):
        space_id = SpaceId.generate()
        week = _week_template(space_id)
        await week_template_repo.save(week)

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/week-templates/{week.id.value}"
        )
        assert response.status_code == 204
        assert await week_template_repo.get_by_id(week.id) is None

    @pytest.mark.asyncio
    async def test_delete_404(self, client):
        space_id = SpaceId.generate()
        response = await client.delete(
            f"/v1/spaces/{space_id.value}/week-templates/{WeekTemplateId.generate().value}"
        )
        assert response.status_code == 404


# Nota: los tests de ``TestApplyWeekTemplate`` se han migrado al agregado
# Week (``tests/integration/test_weeks.py::TestApplyTemplateToWeek``). La
# antigua ruta ``POST /week-templates/{id}/apply`` ha sido eliminada.
