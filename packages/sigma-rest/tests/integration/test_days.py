"""Integration tests del router /v1/spaces/{space_id}/days."""
from datetime import date, datetime, timezone

import pytest

from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.value_objects import BlockId, DayId
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp


def _block(
    *, hour: int = 9, duration: int = 60, area_id: AreaId | None = None
) -> TimeBlock:
    return TimeBlock(
        id=BlockId.generate(),
        start_at=Timestamp(
            datetime(2026, 4, 10, hour, 0, tzinfo=timezone.utc)
        ),
        duration=Minutes(duration),
        area_id=area_id,
        notes="",
    )


def _day(
    space_id: SpaceId,
    *,
    on: date = date(2026, 4, 10),
    blocks: list[TimeBlock] | None = None,
) -> Day:
    return Day(
        id=DayId.for_space_and_date(space_id, on),
        space_id=space_id,
        date=on,
        blocks=blocks or [],
    )


class TestCreateDay:
    @pytest.mark.asyncio
    async def test_crea_day_vacio(self, client):
        space_id = SpaceId.generate()
        response = await client.post(
            f"/v1/spaces/{space_id.value}/days",
            json={"date": "2026-04-10"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["date"] == "2026-04-10"
        assert body["blocks"] == []

    @pytest.mark.asyncio
    async def test_create_day_idempotente(self, client, day_repo):
        space_id = SpaceId.generate()
        existing = _day(space_id, on=date(2026, 4, 10))
        await day_repo.save(existing)

        response = await client.post(
            f"/v1/spaces/{space_id.value}/days",
            json={"date": "2026-04-10"},
        )
        assert response.status_code == 201
        assert response.json()["id"] == existing.id.value


class TestGetDay:
    @pytest.mark.asyncio
    async def test_get_by_id(self, client, day_repo):
        space_id = SpaceId.generate()
        day = _day(space_id)
        await day_repo.save(day)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/days/{day.id.value}"
        )
        assert response.status_code == 200
        assert response.json()["id"] == day.id.value

    @pytest.mark.asyncio
    async def test_get_by_date(self, client, day_repo):
        space_id = SpaceId.generate()
        day = _day(space_id, on=date(2026, 4, 10))
        await day_repo.save(day)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/days/by-date/2026-04-10"
        )
        assert response.status_code == 200
        assert response.json()["id"] == day.id.value

    @pytest.mark.asyncio
    async def test_get_by_date_miss_devuelve_404(self, client):
        space_id = SpaceId.generate()
        response = await client.get(
            f"/v1/spaces/{space_id.value}/days/by-date/2026-04-10"
        )
        assert response.status_code == 404
        assert response.json()["error"] == "day_not_found"

    @pytest.mark.asyncio
    async def test_list_by_range(self, client, day_repo):
        space_id = SpaceId.generate()
        d1 = _day(space_id, on=date(2026, 4, 10))
        d2 = _day(space_id, on=date(2026, 4, 15))
        d_outside = _day(space_id, on=date(2026, 5, 1))
        for d in (d1, d2, d_outside):
            await day_repo.save(d)

        response = await client.get(
            f"/v1/spaces/{space_id.value}/days/by-range",
            params={"start": "2026-04-01", "end": "2026-04-30"},
        )
        assert response.status_code == 200
        ids = {d["id"] for d in response.json()["days"]}
        assert ids == {d1.id.value, d2.id.value}

    @pytest.mark.asyncio
    async def test_list_by_range_rechaza_rangos_mayores_a_365_dias(
        self, client
    ):
        space_id = SpaceId.generate()
        response = await client.get(
            f"/v1/spaces/{space_id.value}/days/by-range",
            params={"start": "2026-01-01", "end": "2027-02-01"},
        )
        assert response.status_code == 422
        body = response.json()
        assert body["detail"]["error"] == "date_range_too_large"
        assert body["detail"]["max_days"] == 365


class TestBlocks:
    @pytest.mark.asyncio
    async def test_add_block(self, client, day_repo):
        space_id = SpaceId.generate()
        day = _day(space_id)
        await day_repo.save(day)
        area_id = AreaId.generate()

        response = await client.post(
            f"/v1/spaces/{space_id.value}/days/{day.id.value}/blocks",
            json={
                "start_at": "2026-04-10T09:00:00+00:00",
                "duration": 60,
                "area_id": area_id.value,
                "notes": "deep work",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert len(body["blocks"]) == 1
        assert body["blocks"][0]["duration"] == 60
        assert body["blocks"][0]["area_id"] == area_id.value
        assert body["blocks"][0]["notes"] == "deep work"

    @pytest.mark.asyncio
    async def test_add_block_rechaza_solapamiento(self, client, day_repo):
        space_id = SpaceId.generate()
        existing_block = _block(hour=9, duration=60)
        day = _day(space_id, blocks=[existing_block])
        await day_repo.save(day)

        response = await client.post(
            f"/v1/spaces/{space_id.value}/days/{day.id.value}/blocks",
            json={
                "start_at": "2026-04-10T09:30:00+00:00",
                "duration": 30,
                "area_id": None,
                "notes": "",
            },
        )
        assert response.status_code == 409
        assert response.json()["error"] == "block_overlap"

    @pytest.mark.asyncio
    async def test_update_block_duracion(self, client, day_repo):
        space_id = SpaceId.generate()
        block = _block(hour=9, duration=60)
        day = _day(space_id, blocks=[block])
        await day_repo.save(day)

        response = await client.patch(
            f"/v1/spaces/{space_id.value}/days/{day.id.value}/blocks/{block.id.value}",
            json={"duration": 90},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["blocks"][0]["duration"] == 90

    @pytest.mark.asyncio
    async def test_update_block_limpia_area(self, client, day_repo):
        space_id = SpaceId.generate()
        area_id = AreaId.generate()
        block = _block(hour=9, area_id=area_id)
        day = _day(space_id, blocks=[block])
        await day_repo.save(day)

        response = await client.patch(
            f"/v1/spaces/{space_id.value}/days/{day.id.value}/blocks/{block.id.value}",
            json={"area_id_set": True, "area_id": None},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["blocks"][0]["area_id"] is None

    @pytest.mark.asyncio
    async def test_remove_block(self, client, day_repo):
        space_id = SpaceId.generate()
        block = _block(hour=9)
        day = _day(space_id, blocks=[block])
        await day_repo.save(day)

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/days/{day.id.value}/blocks/{block.id.value}"
        )
        assert response.status_code == 200
        body = response.json()
        assert body["blocks"] == []

    @pytest.mark.asyncio
    async def test_clear_blocks(self, client, day_repo):
        space_id = SpaceId.generate()
        day = _day(
            space_id,
            blocks=[_block(hour=9), _block(hour=11)],
        )
        await day_repo.save(day)

        response = await client.delete(
            f"/v1/spaces/{space_id.value}/days/{day.id.value}/blocks"
        )
        assert response.status_code == 204

        refreshed = await day_repo.get_by_id(day.id)
        assert refreshed.blocks == []
