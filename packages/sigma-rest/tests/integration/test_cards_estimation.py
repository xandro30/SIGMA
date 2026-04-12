"""
Integration tests for Plan 1 Estimation endpoints:

  PATCH /cards/{id}/size        — asignar/limpiar t-shirt size
  POST  /cards/{id}/timer/start — iniciar timer (invariante 1 por space)
  POST  /cards/{id}/timer/stop  — detener timer y acumular actual_time
"""
import pytest
import pytest_asyncio

from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.shared_kernel.value_objects import CardId, SpaceId
from sigma_core.task_management.domain.value_objects import CardTitle


# ── assign_size ───────────────────────────────────────────────────


class TestAssignSize:

    @pytest.mark.asyncio
    async def test_asigna_size_a_card_existente(self, client, card_in_inbox):
        response = await client.patch(
            f"/v1/cards/{card_in_inbox.id.value}/size",
            json={"size": "m"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["size"] == "m"

    @pytest.mark.asyncio
    async def test_limpia_size_con_null(self, client, card_in_inbox, card_repo):
        card_in_inbox.assign_size(CardSize.L)
        await card_repo.save(card_in_inbox)

        response = await client.patch(
            f"/v1/cards/{card_in_inbox.id.value}/size",
            json={"size": None},
        )

        assert response.status_code == 200
        assert response.json()["size"] is None

    @pytest.mark.asyncio
    async def test_card_no_encontrada_devuelve_404(self, client):
        response = await client.patch(
            f"/v1/cards/{CardId.generate().value}/size",
            json={"size": "s"},
        )

        assert response.status_code == 404
        assert response.json()["error"] == "card_not_found"


# ── start_timer ───────────────────────────────────────────────────


class TestStartTimer:

    @pytest.mark.asyncio
    async def test_inicia_timer_en_card_sin_timer(self, client, card_in_inbox):
        response = await client.post(
            f"/v1/cards/{card_in_inbox.id.value}/timer/start",
        )

        assert response.status_code == 200
        body = response.json()
        assert body["timer_started_at"] is not None

    @pytest.mark.asyncio
    async def test_iniciar_timer_con_timer_activo_devuelve_409(self, client, card_in_inbox):
        await client.post(f"/v1/cards/{card_in_inbox.id.value}/timer/start")

        response = await client.post(
            f"/v1/cards/{card_in_inbox.id.value}/timer/start",
        )

        assert response.status_code == 409
        assert response.json()["error"] == "timer_already_running"

    @pytest.mark.asyncio
    async def test_iniciar_timer_con_otro_timer_en_mismo_space_devuelve_409(
        self, client, card_repo
    ):
        space_id = SpaceId.generate()
        card_a = Card(
            id=CardId.generate(),
            space_id=space_id,
            title=CardTitle("Card A"),
            pre_workflow_stage=PreWorkflowStage.INBOX,
            workflow_state_id=None,
        )
        card_b = Card(
            id=CardId.generate(),
            space_id=space_id,
            title=CardTitle("Card B"),
            pre_workflow_stage=PreWorkflowStage.INBOX,
            workflow_state_id=None,
        )
        await card_repo.save(card_a)
        await card_repo.save(card_b)

        await client.post(f"/v1/cards/{card_a.id.value}/timer/start")

        response = await client.post(
            f"/v1/cards/{card_b.id.value}/timer/start",
        )

        assert response.status_code == 409
        body = response.json()
        assert body["error"] == "space_has_active_timer"
        assert body["detail"]["space_id"] == space_id.value
        assert body["detail"]["active_card_id"] == card_a.id.value

    @pytest.mark.asyncio
    async def test_card_no_encontrada_devuelve_404(self, client):
        response = await client.post(
            f"/v1/cards/{CardId.generate().value}/timer/start",
        )

        assert response.status_code == 404
        assert response.json()["error"] == "card_not_found"


# ── stop_timer ────────────────────────────────────────────────────


class TestStopTimer:

    @pytest.mark.asyncio
    async def test_detiene_timer_activo(self, client, card_in_inbox):
        await client.post(f"/v1/cards/{card_in_inbox.id.value}/timer/start")

        response = await client.post(
            f"/v1/cards/{card_in_inbox.id.value}/timer/stop",
        )

        assert response.status_code == 200
        body = response.json()
        assert body["timer_started_at"] is None
        assert body["actual_time"] >= 0

    @pytest.mark.asyncio
    async def test_detener_timer_sin_timer_activo_devuelve_409(self, client, card_in_inbox):
        response = await client.post(
            f"/v1/cards/{card_in_inbox.id.value}/timer/stop",
        )

        assert response.status_code == 409
        assert response.json()["error"] == "timer_not_running"

    @pytest.mark.asyncio
    async def test_card_no_encontrada_devuelve_404(self, client):
        response = await client.post(
            f"/v1/cards/{CardId.generate().value}/timer/stop",
        )

        assert response.status_code == 404
        assert response.json()["error"] == "card_not_found"


# ── Plan completo: start → stop → actual_time acumulado ─────────────


@pytest_asyncio.fixture
async def card_with_size(card_repo):
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Card con size"),
        pre_workflow_stage=PreWorkflowStage.BACKLOG,
        workflow_state_id=None,
    )
    card.assign_size(CardSize.S)
    await card_repo.save(card)
    return card


class TestFlujoCompleto:

    @pytest.mark.asyncio
    async def test_size_persiste_en_get(self, client, card_with_size):
        response = await client.get(f"/v1/cards/{card_with_size.id.value}")

        assert response.status_code == 200
        assert response.json()["size"] == "s"
