"""
Integration tests for Plan 1 Estimation endpoints en spaces:

  PATCH /spaces/{id}/size-mapping — configurar tabla size → minutes
"""
import pytest
import pytest_asyncio

from sigma_core.task_management.domain.aggregates.space import Space
from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.task_management.domain.value_objects import SpaceName


@pytest_asyncio.fixture
async def empty_space(space_repo):
    space = Space(
        id=SpaceId.generate(),
        name=SpaceName("Test Space"),
    )
    await space_repo.save(space)
    return space


class TestSetSizeMapping:

    @pytest.mark.asyncio
    async def test_configura_size_mapping_completo(self, client, empty_space):
        mapping = {
            "xxs": 30,
            "xs": 60,
            "s": 120,
            "m": 240,
            "l": 480,
            "xl": 960,
            "xxl": 1920,
        }

        response = await client.patch(
            f"/v1/spaces/{empty_space.id.value}/size-mapping",
            json={"mapping": mapping},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["size_mapping"] == mapping

    @pytest.mark.asyncio
    async def test_limpia_size_mapping_con_null(self, client, empty_space, space_repo):
        from sigma_core.shared_kernel.value_objects import SizeMapping

        empty_space.set_size_mapping(SizeMapping.default())
        await space_repo.save(empty_space)

        response = await client.patch(
            f"/v1/spaces/{empty_space.id.value}/size-mapping",
            json={"mapping": None},
        )

        assert response.status_code == 200
        assert response.json()["size_mapping"] is None

    @pytest.mark.asyncio
    async def test_size_mapping_incompleto_devuelve_422(self, client, empty_space):
        response = await client.patch(
            f"/v1/spaces/{empty_space.id.value}/size-mapping",
            json={"mapping": {"xxs": 30, "s": 120}},
        )

        assert response.status_code == 422
        assert response.json()["detail"]["error"] == "invalid_size_mapping"

    @pytest.mark.asyncio
    async def test_space_no_encontrado_devuelve_404(self, client):
        mapping = {
            "xxs": 30,
            "xs": 60,
            "s": 120,
            "m": 240,
            "l": 480,
            "xl": 960,
            "xxl": 1920,
        }

        response = await client.patch(
            f"/v1/spaces/{SpaceId.generate().value}/size-mapping",
            json={"mapping": mapping},
        )

        assert response.status_code == 404
        assert response.json()["error"] == "space_not_found"
